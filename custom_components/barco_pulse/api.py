"""Barco Pulse JSON-RPC 2.0 API Client."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class BarcoPulseApiError(Exception):
    """Base exception for Barco Pulse API errors."""


class BarcoPulseConnectionError(BarcoPulseApiError):
    """Exception to indicate a connection error."""


class BarcoPulseAuthenticationError(BarcoPulseApiError):
    """Exception to indicate an authentication error."""


class BarcoPulseTimeoutError(BarcoPulseApiError):
    """Exception to indicate a timeout error."""


class BarcoPulseCommandError(BarcoPulseApiError):
    """Exception to indicate a command/JSON-RPC error."""

    def __init__(self, message: str, code: int | None = None) -> None:
        """Initialize command error with optional error code."""
        super().__init__(message)
        self.code = code


class BarcoPulseApiClient:
    """Barco Pulse projector API client using JSON-RPC 2.0 over TCP."""

    def __init__(
        self,
        host: str,
        port: int = 9090,
        auth_code: int | None = None,
        timeout: float = 10.0,
    ) -> None:
        """
        Initialize the API client.

        Args:
            host: Projector IP address or hostname
            port: TCP port number (default: 9090)
            auth_code: Optional 5-digit authentication code for elevated access
            timeout: Request timeout in seconds (default: 10.0)

        """
        self._host = host
        self._port = port
        self._auth_code = auth_code
        self._timeout = timeout

        # Connection state
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False
        self._read_task: asyncio.Task | None = None

        # Request/response correlation
        self._request_id = 0
        self._pending_requests: dict[int, asyncio.Future] = {}
        self._lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        """Return True if connected to projector."""
        return self._connected

    async def connect(self) -> None:
        """Connect to the projector and start read loop."""
        if self._connected:
            _LOGGER.debug("Already connected to %s:%d", self._host, self._port)
            return

        try:
            _LOGGER.info("Connecting to Barco Pulse at %s:%d", self._host, self._port)
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._timeout,
            )
            self._connected = True
            _LOGGER.info("Connected to %s:%d", self._host, self._port)

            # Start background read loop
            self._read_task = asyncio.create_task(self._read_loop())

            # Authenticate if auth code provided
            if self._auth_code is not None:
                await self.authenticate(self._auth_code)

        except TimeoutError as err:
            msg = f"Timeout connecting to {self._host}:{self._port}"
            raise BarcoPulseTimeoutError(msg) from err
        except OSError as err:
            msg = f"Connection error to {self._host}:{self._port}: {err}"
            raise BarcoPulseConnectionError(msg) from err

    async def disconnect(self) -> None:
        """Disconnect from the projector."""
        if not self._connected:
            return

        _LOGGER.info("Disconnecting from %s:%d", self._host, self._port)
        self._connected = False

        # Cancel read task
        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._read_task

        # Close writer
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Error closing writer: %s", err)

        # Cancel pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.set_exception(BarcoPulseConnectionError("Connection closed"))
        self._pending_requests.clear()

        self._reader = None
        self._writer = None
        self._read_task = None
        _LOGGER.info("Disconnected from %s:%d", self._host, self._port)

    async def _read_loop(self) -> None:
        """Background loop to read responses and notifications from projector."""
        _LOGGER.debug("Starting read loop")
        try:
            while self._connected and self._reader:
                try:
                    # Read line (JSON-RPC messages are newline-delimited)
                    line = await self._reader.readline()
                    if not line:
                        _LOGGER.warning("Connection closed by projector")
                        break

                    # Parse JSON
                    try:
                        message = json.loads(line.decode("utf-8").strip())
                        _LOGGER.debug("Received: %s", message)
                    except json.JSONDecodeError:
                        _LOGGER.exception("Invalid JSON received")
                        continue

                    # Handle response (has 'id' field)
                    if "id" in message:
                        await self._handle_response(message)
                    # Handle notification (no 'id' field)
                    else:
                        await self._handle_notification(message)

                except Exception:
                    _LOGGER.exception("Error in read loop")
                    if not self._connected:
                        break

        except asyncio.CancelledError:
            _LOGGER.debug("Read loop cancelled")
        finally:
            _LOGGER.debug("Read loop ended")
            if self._connected:
                # Connection lost unexpectedly
                await self.disconnect()

    async def _handle_response(self, message: dict[str, Any]) -> None:
        """Handle JSON-RPC response message."""
        request_id = message.get("id")
        if request_id not in self._pending_requests:
            _LOGGER.warning("Received response for unknown request ID: %s", request_id)
            return

        future = self._pending_requests.pop(request_id)

        # Check for error
        if "error" in message:
            error = message["error"]
            error_code = error.get("code")
            error_message = error.get("message", "Unknown error")
            _LOGGER.error("JSON-RPC error %s: %s", error_code, error_message)
            future.set_exception(BarcoPulseCommandError(error_message, error_code))
        # Success response
        elif "result" in message:
            future.set_result(message["result"])
        else:
            future.set_exception(
                BarcoPulseCommandError("Invalid response: missing result or error")
            )

    async def _handle_notification(self, message: dict[str, Any]) -> None:
        """Handle JSON-RPC notification message (property changes, signals)."""
        method = message.get("method")
        params = message.get("params", {})
        _LOGGER.debug("Notification: %s with params: %s", method, params)
        # For now, just log notifications
        # Future: could implement callback handlers for
        # property.changed, signal.callback

    async def _send_request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> Any:
        """
        Send JSON-RPC request and wait for response.

        Args:
            method: JSON-RPC method name
            params: Optional method parameters

        Returns:
            The result from the JSON-RPC response

        Raises:
            BarcoPulseConnectionError: If not connected
            BarcoPulseTimeoutError: If request times out
            BarcoPulseCommandError: If JSON-RPC error returned

        """
        if not self._connected or not self._writer:
            msg = "Not connected to projector"
            raise BarcoPulseConnectionError(msg)

        async with self._lock:
            # Generate request ID
            self._request_id += 1
            request_id = self._request_id

            # Build JSON-RPC request
            request: dict[str, Any] = {
                "jsonrpc": "2.0",
                "method": method,
                "id": request_id,
            }
            if params is not None:
                request["params"] = params

            # Create future for response
            future: asyncio.Future = asyncio.Future()
            self._pending_requests[request_id] = future

            # Send request
            try:
                message = json.dumps(request) + "\n"
                # Redact auth code in logs
                log_request = request.copy()
                if method == "authenticate" and "params" in log_request:
                    log_params = log_request["params"].copy()
                    log_params["code"] = "REDACTED"
                    log_request["params"] = log_params
                _LOGGER.debug("Sending: %s", log_request)

                self._writer.write(message.encode("utf-8"))
                await self._writer.drain()

            except Exception as err:
                self._pending_requests.pop(request_id, None)
                msg = f"Error sending request: {err}"
                raise BarcoPulseConnectionError(msg) from err

        # Wait for response
        try:
            return await asyncio.wait_for(future, timeout=self._timeout)
        except TimeoutError as err:
            self._pending_requests.pop(request_id, None)
            msg = f"Request timeout for method: {method}"
            raise BarcoPulseTimeoutError(msg) from err

    # Authentication

    async def authenticate(self, code: int) -> bool:
        """
        Authenticate with the projector.

        Args:
            code: 5-digit authentication code

        Returns:
            True if authentication successful

        Raises:
            BarcoPulseAuthenticationError: If authentication fails

        """
        try:
            result = await self._send_request("authenticate", {"code": code})
            _LOGGER.info("Authentication successful")
            return bool(result)
        except BarcoPulseCommandError as err:
            msg = "Authentication failed"
            raise BarcoPulseAuthenticationError(msg) from err

    # Power Control

    async def power_on(self) -> None:
        """Power on the projector."""
        _LOGGER.info("Powering on projector")
        await self._send_request("system.poweron")

    async def power_off(self) -> None:
        """Power off the projector."""
        _LOGGER.info("Powering off projector")
        await self._send_request("system.poweroff")

    # Property Access

    async def get_property(self, property_name: str | list[str]) -> Any:
        """
        Get one or more property values.

        Args:
            property_name: Single property name or list of property names

        Returns:
            Single value if string passed, dict if list passed

        """
        return await self._send_request("property.get", {"property": property_name})

    async def set_property(self, property_name: str, value: Any) -> None:
        """
        Set a property value.

        Args:
            property_name: Property name
            value: New value for the property

        """
        await self._send_request(
            "property.set", {"property": property_name, "value": value}
        )

    # System State

    async def get_system_state(self) -> str:
        """
        Get current system state.

        Returns:
            State string: "boot", "eco", "standby", "ready",
            "conditioning", "on", "deconditioning"

        """
        result = await self.get_property("system.state")
        # Extract value from result dict if present
        if isinstance(result, dict) and "value" in result:
            return str(result["value"])
        return str(result)

    async def get_system_info(self) -> dict[str, Any]:
        """
        Get system information (serial, model, firmware).

        Returns:
            Dictionary with system information

        """
        # Get multiple properties at once
        props = await self.get_property(
            ["system.serialnumber", "system.modelname", "system.firmwareversion"]
        )

        # Handle list response (array of {property, value} dicts)
        if isinstance(props, list):
            result = {}
            for item in props:
                if isinstance(item, dict) and "property" in item and "value" in item:
                    result[item["property"]] = item["value"]
            return {
                "serial_number": result.get("system.serialnumber", ""),
                "model_name": result.get("system.modelname", ""),
                "firmware_version": result.get("system.firmwareversion", ""),
            }

        # Handle dict response
        return {
            "serial_number": props.get("system.serialnumber", ""),
            "model_name": props.get("system.modelname", ""),
            "firmware_version": props.get("system.firmwareversion", ""),
        }

    # Source Management

    async def list_sources(self) -> list[str]:
        """
        List available input sources.

        Returns:
            List of source names (e.g., ["DisplayPort 1", "HDMI", ...])

        """
        sources = await self._send_request("image.source.list")
        return list(sources) if sources else []

    async def get_active_source(self) -> str:
        """
        Get the currently active input source.

        Returns:
            Source name (e.g., "DisplayPort 1")

        """
        result = await self.get_property("image.window.main.source")
        # Extract value from result dict if present
        if isinstance(result, dict) and "value" in result:
            return str(result["value"])
        return str(result)

    async def set_active_source(self, source: str) -> None:
        """
        Set the active input source.

        Args:
            source: Source name (e.g., "DisplayPort 1", "HDMI")

        """
        _LOGGER.info("Setting active source to: %s", source)
        await self.set_property("image.window.main.source", source)

    # Illumination Control

    async def get_laser_power(self) -> float:
        """
        Get current laser power percentage.

        Returns:
            Laser power as percentage (0.0-100.0)

        """
        result = await self.get_property("illumination.sources.laser.power")
        # Extract value from result dict if present
        if isinstance(result, dict) and "value" in result:
            return float(result["value"])
        return float(result)

    async def set_laser_power(self, power: float) -> None:
        """
        Set laser power percentage.

        Args:
            power: Power percentage (0.0-100.0)

        """
        _LOGGER.info("Setting laser power to: %.1f%%", power)
        await self.set_property("illumination.sources.laser.power", power)
