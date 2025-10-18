"""
Barco Pulse JSON-RPC 2.0 API Client.

This client communicates with Barco HDR CS projectors using a hybrid HTTP/0.9 protocol:
- Sends HTTP POST requests with JSON-RPC 2.0 payload
- Receives raw JSON responses (without HTTP headers)

This is a synchronous request/response pattern (no background read loop needed).
"""

from __future__ import annotations

import asyncio
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
    """Barco Pulse projector API client using JSON-RPC 2.0 over HTTP/0.9."""

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

        # Request ID counter
        self._request_id = 0
        self._lock = asyncio.Lock()

        # Connection state (validated on first request)
        self._validated = False

    async def connect(self) -> None:
        """
        Validate connection to the projector.

        This performs a test request to verify the projector is reachable.
        Authentication is performed if auth_code was provided.
        """
        _LOGGER.info(
            "Validating connection to Barco Pulse at %s:%d",
            self._host,
            self._port,
        )

        try:
            # Test connection with a simple property get
            await self.get_property("system.serialnumber")
            self._validated = True
            _LOGGER.info("Connection validated to %s:%d", self._host, self._port)

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
        """Disconnect from the projector (no persistent connection)."""
        # No persistent connection to close
        self._validated = False
        _LOGGER.debug("Disconnected from %s:%d", self._host, self._port)

    async def _send_request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> Any:
        """
        Send JSON-RPC request using HTTP POST and wait for raw JSON response.

        The projector uses a hybrid HTTP/0.9 protocol:
        - Accepts HTTP POST requests with JSON-RPC 2.0 payload
        - Returns raw JSON (without HTTP response headers)

        Args:
            method: JSON-RPC method name
            params: Optional method parameters

        Returns:
            The result from the JSON-RPC response

        Raises:
            BarcoPulseConnectionError: If connection fails
            BarcoPulseTimeoutError: If request times out
            BarcoPulseCommandError: If JSON-RPC error returned

        """
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

            # Log request (redact auth code)
            log_request = request.copy()
            if method == "authenticate" and "params" in log_request:
                log_params = log_request["params"].copy()
                log_params["code"] = "REDACTED"
                log_request["params"] = log_params
            _LOGGER.debug("Sending request: %s", log_request)

            try:
                # Open TCP connection
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self._host, self._port),
                    timeout=self._timeout,
                )

                try:
                    # Send HTTP POST request
                    json_data = json.dumps(request)
                    http_request = (
                        f"POST / HTTP/1.1\r\n"
                        f"Host: {self._host}\r\n"
                        f"Content-Type: application/json\r\n"
                        f"Content-Length: {len(json_data)}\r\n"
                        f"\r\n"
                        f"{json_data}"
                    )

                    writer.write(http_request.encode())
                    await writer.drain()

                    # Read response (raw JSON, possibly with HTTP headers)
                    data = await asyncio.wait_for(
                        reader.read(4096),
                        timeout=self._timeout,
                    )
                    response_text = data.decode("utf-8")

                    # Extract JSON (skip HTTP headers if present)
                    json_start = response_text.find("{")
                    if json_start < 0:
                        msg = f"No JSON in response: {response_text[:100]}"
                        raise BarcoPulseCommandError(msg)

                    json_text = response_text[json_start:]
                    message = json.loads(json_text)
                    _LOGGER.debug("Received response: %s", message)

                    # Check for JSON-RPC error
                    if "error" in message:
                        error = message["error"]
                        error_code = error.get("code")
                        error_message = error.get("message", "Unknown error")
                        _LOGGER.error(
                            "JSON-RPC error %s: %s", error_code, error_message
                        )
                        raise BarcoPulseCommandError(error_message, error_code)

                    # Return result
                    if "result" in message:
                        return message["result"]

                    msg = "Invalid response: missing result or error"
                    raise BarcoPulseCommandError(msg)

                finally:
                    # Always close connection
                    writer.close()
                    await writer.wait_closed()

            except TimeoutError as err:
                msg = f"Request timeout for method: {method}"
                raise BarcoPulseTimeoutError(msg) from err
            except OSError as err:
                msg = f"Connection error: {err}"
                raise BarcoPulseConnectionError(msg) from err
            except json.JSONDecodeError as err:
                msg = f"Invalid JSON response: {err}"
                raise BarcoPulseCommandError(msg) from err

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
            value = result["value"]
            if isinstance(value, (int, float, str)):
                return float(value)
            msg = f"Invalid laser power value type: {type(value)}"
            raise BarcoPulseApiError(msg)
        if isinstance(result, (int, float, str)):
            return float(result)
        msg = f"Invalid laser power result type: {type(result)}"
        raise BarcoPulseApiError(msg)

    async def set_laser_power(self, power: float) -> None:
        """
        Set laser power percentage.

        Args:
            power: Power percentage (0.0-100.0)

        """
        _LOGGER.info("Setting laser power to: %.1f%%", power)
        await self.set_property("illumination.sources.laser.power", power)
