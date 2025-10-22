"""JSON-RPC API client for Barco Pulse projector."""

# ruff: noqa: TRY003, EM101, EM102

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from .const import PRESET_ASSIGNMENT_TUPLE_SIZE
from .exceptions import (
    BarcoApiError,
    BarcoAuthError,
    BarcoConnectionError,
    BarcoStateError,
)

_LOGGER = logging.getLogger(__name__)

# JSON-RPC error codes
ERROR_PROPERTY_NOT_FOUND = -32601


class BarcoDevice:
    """Barco Pulse projector device client."""

    def __init__(
        self,
        host: str,
        port: int = 9090,
        auth_code: str | None = None,
        timeout: int = 10,
    ) -> None:
        """
        Initialize the Barco device client.

        Args:
            host: Projector IP address or hostname
            port: TCP port (default 9090)
            auth_code: Optional 5-digit authentication code
            timeout: Request timeout in seconds

        """
        self.host = host
        self.port = port
        self.auth_code = auth_code
        self.timeout = timeout

        self._lock = asyncio.Lock()
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False
        self._request_id = 0
        self._max_request_id = 2**31 - 1  # Prevent overflow

    async def connect(self) -> None:
        """Establish TCP connection to the projector."""
        try:
            _LOGGER.debug("Connecting to %s:%s", self.host, self.port)
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout,
            )
            self._connected = True
            _LOGGER.debug("Connected to %s:%s", self.host, self.port)

            # Authenticate if auth code provided
            if self.auth_code:
                await self.authenticate(self.auth_code)

        except TimeoutError as err:
            msg = f"Connection timeout to {self.host}:{self.port}"
            raise BarcoConnectionError(msg) from err
        except (ConnectionError, OSError) as err:
            msg = f"Failed to connect to {self.host}:{self.port}: {err}"
            raise BarcoConnectionError(msg) from err

    async def disconnect(self) -> None:
        """Close the TCP connection."""
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except (ConnectionError, OSError) as err:
                _LOGGER.debug("Error closing connection: %s", err)
            finally:
                self._writer = None
                self._reader = None
                self._connected = False
                _LOGGER.debug("Disconnected from %s:%s", self.host, self.port)

    def _build_jsonrpc_request(
        self,
        method: str,
        params: Any = None,
        request_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Build a JSON-RPC 2.0 request.

        Args:
            method: JSON-RPC method name
            params: Method parameters (dict, list, or any JSON-serializable value)
            request_id: Request ID (if None, creates a notification)

        Returns:
            JSON-RPC request dictionary

        """
        request: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
        }

        if params is not None:
            request["params"] = params

        if request_id is not None:
            request["id"] = request_id

        return request

    def _build_http_request(self, json_payload: str) -> str:
        """
        Build HTTP/1.1 POST request with JSON-RPC payload.

        Args:
            json_payload: JSON-RPC request as string

        Returns:
            Complete HTTP request as string

        """
        content_length = len(json_payload.encode("utf-8"))

        return (
            f"POST / HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {content_length}\r\n"
            f"\r\n"
            f"{json_payload}"
        )

    async def _read_json_response(self) -> dict[str, Any]:
        """
        Read JSON response from the projector.

        The Barco Pulse protocol returns raw JSON without HTTP headers.

        Returns:
            Parsed JSON response

        Raises:
            BarcoConnectionError: If connection lost or timeout
            BarcoApiError: If JSON parsing fails

        """
        if not self._reader:
            raise BarcoConnectionError("Not connected")

        try:
            # Read until we get valid JSON
            buffer = b""
            max_buffer_size = 1024 * 1024  # 1MB limit to prevent memory leaks

            while True:
                chunk = await asyncio.wait_for(
                    self._reader.read(4096),
                    timeout=self.timeout,
                )

                if not chunk:
                    raise BarcoConnectionError("Connection closed by projector")

                buffer += chunk

                # Prevent unbounded buffer growth
                if len(buffer) > max_buffer_size:
                    raise BarcoApiError(
                        -1, f"Response too large (>{max_buffer_size} bytes)"
                    )

                # Try to parse as JSON
                try:
                    return json.loads(buffer.decode("utf-8"))
                except json.JSONDecodeError:
                    # Need more data
                    continue

        except TimeoutError as err:
            raise BarcoConnectionError("Response timeout") from err
        except UnicodeDecodeError as err:
            raise BarcoApiError(-1, f"Invalid response encoding: {err}") from err

    def _parse_jsonrpc_response(
        self,
        response: dict[str, Any],
        expected_id: int | None = None,
    ) -> Any:
        """
        Parse and validate JSON-RPC response.

        Args:
            response: JSON-RPC response dictionary
            expected_id: Expected request ID for validation

        Returns:
            Result value from response

        Raises:
            BarcoApiError: If response contains error
            BarcoStateError: If error code indicates state dependency

        """
        # Validate response ID if expected
        if expected_id is not None:
            response_id = response.get("id")
            if response_id != expected_id:
                raise BarcoApiError(
                    -1,
                    f"Response ID mismatch: expected {expected_id}, got {response_id}",
                )

        # Check for error
        if "error" in response:
            error = response["error"]
            code = error.get("code", -1)
            message = error.get("message", "Unknown error")

            # Error -32601 indicates property not found (usually state dependency)
            if code == ERROR_PROPERTY_NOT_FOUND:
                raise BarcoStateError(message)

            raise BarcoApiError(code, message)

        # Return result
        return response.get("result")

    async def _send_request(
        self,
        method: str,
        params: Any = None,
    ) -> Any:
        """
        Send JSON-RPC request and return result.

        Args:
            method: JSON-RPC method name
            params: Method parameters (dict, list, or any JSON-serializable value)

        Returns:
            Result from JSON-RPC response

        Raises:
            BarcoConnectionError: If connection fails
            BarcoApiError: If API returns error
            BarcoStateError: If property not available in current state

        """
        async with self._lock:
            # Auto-connect if not connected
            if not self._connected:
                await self.connect()

            # Generate request ID (reset on overflow to prevent issues)
            self._request_id += 1
            if self._request_id > self._max_request_id:
                self._request_id = 1
            request_id = self._request_id

            # Build JSON-RPC request
            jsonrpc_request = self._build_jsonrpc_request(method, params, request_id)
            json_payload = json.dumps(jsonrpc_request)

            # Build HTTP request
            http_request = self._build_http_request(json_payload)

            _LOGGER.debug("Sending request: %s", json_payload)

            # Send request
            try:
                if not self._writer:
                    raise BarcoConnectionError("Not connected")

                self._writer.write(http_request.encode("utf-8"))
                await self._writer.drain()

            except (ConnectionError, OSError) as err:
                self._connected = False
                raise BarcoConnectionError(f"Failed to send request: {err}") from err

            # Read response
            response = await self._read_json_response()
            _LOGGER.debug("Received response: %s", response)

            # Parse and return result
            return self._parse_jsonrpc_response(response, request_id)

    async def authenticate(self, code: str) -> bool:
        """
        Authenticate with the projector.

        Args:
            code: 5-digit authentication code

        Returns:
            True if authentication successful

        Raises:
            BarcoAuthError: If authentication fails

        """
        try:
            result = await self._send_request("authenticate", {"code": code})
            if result:
                _LOGGER.debug("Authentication successful")
                return True
            raise BarcoAuthError("Authentication failed")
        except BarcoApiError as err:
            raise BarcoAuthError(f"Authentication error: {err.message}") from err

    async def get_state(self) -> str:
        """
        Get current power state.

        Returns:
            Power state (boot, eco, standby, ready, on, conditioning, deconditioning)

        """
        return await self.get_property("system.state")

    async def power_on(self) -> None:
        """Power on the projector."""
        await self._send_request("system.poweron")

    async def power_off(self) -> None:
        """Power off the projector."""
        await self._send_request("system.poweroff")

    async def get_property(self, property_name: str) -> Any:
        """
        Get a single property value.

        Args:
            property_name: Property name (e.g., "system.state")

        Returns:
            Property value

        """
        return await self._send_request("property.get", {"property": property_name})

    async def get_properties(self, property_names: list[str]) -> dict[str, Any]:
        """
        Get multiple property values in a single request.

        Args:
            property_names: List of property names

        Returns:
            Dictionary mapping property names to values

        """
        # Use batch property.get - API returns dict when array is passed
        result = await self._send_request("property.get", {"property": property_names})

        # When an array of properties is requested, result is a dict
        if isinstance(result, dict):
            return result

        # Fallback for single property (shouldn't happen with list input)
        return {property_names[0]: result}

    async def set_property(self, property_name: str, value: Any) -> None:
        """
        Set a property value.

        Args:
            property_name: Property name
            value: New value

        """
        await self._send_request(
            "property.set", {"property": property_name, "value": value}
        )

    async def get_source(self) -> str:
        """
        Get current input source.

        Returns:
            Current source name

        """
        return await self.get_property("image.window.main.source")

    async def get_available_sources(self) -> list[str]:
        """
        Get list of available input sources.

        Returns:
            List of source names

        """
        result = await self._send_request("image.source.list")
        return result if isinstance(result, list) else []

    async def set_source(self, source: str) -> None:
        """
        Set input source.

        Args:
            source: Source name

        """
        await self.set_property("image.window.main.source", source)

    async def get_laser_power(self) -> float:
        """
        Get laser power level.

        Returns:
            Laser power percentage

        """
        result = await self.get_property("illumination.sources.laser.power")
        return float(result)

    async def set_laser_power(self, power: float) -> None:
        """
        Set laser power level.

        Args:
            power: Power percentage

        """
        await self.set_property("illumination.sources.laser.power", power)

    async def get_laser_limits(self) -> tuple[float, float]:
        """
        Get laser power min/max limits.

        Returns:
            Tuple of (min_power, max_power)

        """
        min_power = await self.get_property("illumination.sources.laser.power.min")
        max_power = await self.get_property("illumination.sources.laser.power.max")
        return (float(min_power), float(max_power))

    async def get_brightness(self) -> float:
        """
        Get brightness value.

        Returns:
            Brightness value

        """
        result = await self.get_property("image.brightness")
        return float(result)

    async def set_brightness(self, value: float) -> None:
        """
        Set brightness value.

        Args:
            value: Brightness value

        """
        await self.set_property("image.brightness", value)

    async def get_contrast(self) -> float:
        """
        Get contrast value.

        Returns:
            Contrast value

        """
        result = await self.get_property("image.contrast")
        return float(result)

    async def set_contrast(self, value: float) -> None:
        """
        Set contrast value.

        Args:
            value: Contrast value

        """
        await self.set_property("image.contrast", value)

    async def get_saturation(self) -> float:
        """
        Get saturation value.

        Returns:
            Saturation value

        """
        result = await self.get_property("image.saturation")
        return float(result)

    async def set_saturation(self, value: float) -> None:
        """
        Set saturation value.

        Args:
            value: Saturation value

        """
        await self.set_property("image.saturation", value)

    async def get_hue(self) -> float:
        """
        Get hue value.

        Returns:
            Hue value

        """
        result = await self.get_property("image.hue")
        return float(result)

    async def set_hue(self, value: float) -> None:
        """
        Set hue value.

        Args:
            value: Hue value

        """
        await self.set_property("image.hue", value)

    async def get_serial_number(self) -> str:
        """
        Get projector serial number.

        Returns:
            Serial number

        """
        result = await self.get_property("system.serialnumber")
        return str(result)

    async def get_model_name(self) -> str:
        """
        Get projector model name.

        Returns:
            Model name

        """
        result = await self.get_property("system.modelname")
        return str(result)

    async def get_firmware_version(self) -> str:
        """
        Get firmware version.

        Returns:
            Firmware version

        """
        result = await self.get_property("system.firmwareversion")
        return str(result)

    async def get_preset_assignments(self) -> dict[int, str]:
        """
        Get all preset assignments (preset number -> profile name mapping).

        Returns:
            Dictionary mapping preset numbers to profile names

        Raises:
            BarcoStateError: If projector not in active state

        """
        result = await self.get_property("profile.presetassignments")

        # API returns array of [preset_num, profile_name] pairs
        if not isinstance(result, list):
            return {}

        # Convert to dict, filtering out empty profile names
        assignments = {}
        for item in result:
            if isinstance(item, list) and len(item) >= PRESET_ASSIGNMENT_TUPLE_SIZE:
                preset_num, profile_name = item[0], item[1]
                # Only include presets with assigned profiles
                if profile_name:
                    assignments[int(preset_num)] = profile_name

        return assignments

    async def get_profiles(self) -> list[str]:
        """
        Get list of available profile names.

        Returns:
            List of profile names

        Raises:
            BarcoStateError: If projector not in active state

        """
        result = await self.get_property("profile.profiles")
        if not isinstance(result, list):
            return []
        return result

    async def activate_preset(self, preset: int) -> bool:
        """
        Activate a preset by number.

        Args:
            preset: Preset number to activate

        Returns:
            True if activation successful

        Raises:
            BarcoStateError: If projector not in active state
            BarcoApiError: If preset not assigned or invalid

        """
        result = await self._send_request("profile.activatepreset", preset)
        return bool(result)

    async def activate_profile(self, name: str) -> bool:
        """
        Activate a profile by name.

        Args:
            name: Profile name to activate

        Returns:
            True if activation successful

        Raises:
            BarcoStateError: If projector not in active state
            BarcoApiError: If profile not found

        """
        result = await self._send_request("profile.activateprofile", name)
        return bool(result)

    async def get_profile_for_preset(self, preset: int) -> str:
        """
        Get the profile name assigned to a preset.

        Args:
            preset: Preset number

        Returns:
            Profile name (empty string if unassigned)

        Raises:
            BarcoStateError: If projector not in active state

        """
        result = await self._send_request("profile.profileforpreset", preset)
        return str(result) if result else ""
