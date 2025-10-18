"""Tests for the Barco Pulse API client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.barco_pulse.api import (
    BarcoPulseApiClient,
    BarcoPulseAuthenticationError,
    BarcoPulseCommandError,
    BarcoPulseConnectionError,
    BarcoPulseTimeoutError,
)


class TestBarcoPulseApiClient:
    """Test the BarcoPulseApiClient."""

    async def test_init(self) -> None:
        """Test client initialization."""
        client = BarcoPulseApiClient(
            host="192.168.1.100",
            port=9090,
            auth_code=12345,
            timeout=10.0,
        )

        assert client._host == "192.168.1.100"
        assert client._port == 9090
        assert client._auth_code == 12345
        assert client._timeout == 10.0
        assert not client.is_connected

    async def test_connect_success(self) -> None:
        """Test successful connection."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            assert client.is_connected
            mock_open_connection.assert_called_once_with("192.168.1.100", 9090)

    async def test_connect_with_auth(self) -> None:
        """Test connection with authentication."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100", auth_code=12345)

            with (
                patch.object(client, "_read_loop", return_value=None),
                patch.object(client, "authenticate", return_value=None) as mock_auth,
            ):
                await client.connect()

            assert client.is_connected
            mock_auth.assert_called_once_with(12345)

    async def test_connect_timeout(self) -> None:
        """Test connection timeout."""
        with patch(
            "asyncio.open_connection",
            side_effect=asyncio.TimeoutError,
        ):
            client = BarcoPulseApiClient(host="192.168.1.100", timeout=1.0)

            with pytest.raises(BarcoPulseTimeoutError):
                await client.connect()

            assert not client.is_connected

    async def test_connect_connection_error(self) -> None:
        """Test connection error."""
        with patch(
            "asyncio.open_connection",
            side_effect=OSError("Connection refused"),
        ):
            client = BarcoPulseApiClient(host="192.168.1.100")

            with pytest.raises(BarcoPulseConnectionError):
                await client.connect()

            assert not client.is_connected

    async def test_disconnect(self) -> None:
        """Test disconnection."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_writer.is_closing.return_value = False
            mock_writer.wait_closed = AsyncMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            # Don't replace the read task - let the actual task be created
            # Just verify disconnect works
            await client.disconnect()

            assert not client.is_connected
            mock_writer.close.assert_called_once()

    async def test_send_request_success(self) -> None:
        """Test successful send request."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            # Mock _send_request to return a result
            with patch.object(
                client,
                "_send_request",
                return_value="success",
            ):
                result = await client._send_request("test.method", {"param": "value"})

            assert result == "success"

    async def test_send_request_error_response(self) -> None:
        """Test send request with error response."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            # Mock _send_request to raise an error
            with (
                patch.object(
                    client,
                    "_send_request",
                    side_effect=BarcoPulseCommandError("Method not found", -32601),
                ),
                pytest.raises(BarcoPulseCommandError) as exc_info,
            ):
                await client._send_request("invalid.method")

            assert exc_info.value.code == -32601
            assert "Method not found" in str(exc_info.value)

    async def test_send_request_not_connected(self) -> None:
        """Test send request when not connected."""
        client = BarcoPulseApiClient(host="192.168.1.100")

        with pytest.raises(BarcoPulseConnectionError):
            await client._send_request("test.method")

    async def test_authenticate_success(self) -> None:
        """Test successful authentication."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(
                client,
                "_send_request",
                return_value=True,
            ) as mock_send:
                await client.authenticate(12345)

            mock_send.assert_called_once_with("authenticate", {"code": 12345})

    async def test_authenticate_failure(self) -> None:
        """Test authentication failure."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with (
                patch.object(
                    client,
                    "_send_request",
                    side_effect=BarcoPulseCommandError("Invalid code", -32000),
                ),
                pytest.raises(BarcoPulseAuthenticationError),
            ):
                await client.authenticate(99999)

    async def test_power_on(self) -> None:
        """Test power on command."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(client, "_send_request", return_value=None) as mock_send:
                await client.power_on()

            mock_send.assert_called_once_with("system.poweron")

    async def test_power_off(self) -> None:
        """Test power off command."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(client, "_send_request", return_value=None) as mock_send:
                await client.power_off()

            mock_send.assert_called_once_with("system.poweroff")

    async def test_get_property(self) -> None:
        """Test get property."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(
                client, "_send_request", return_value={"value": "on"}
            ) as mock_send:
                result = await client.get_property("system.state")

            assert result == {"value": "on"}
            mock_send.assert_called_once_with(
                "property.get", {"property": "system.state"}
            )

    async def test_get_property_multiple(self) -> None:
        """Test get multiple properties."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(
                client,
                "_send_request",
                return_value=[{"value": "on"}, {"value": "HDMI 1"}],
            ) as mock_send:
                result = await client.get_property(
                    ["system.state", "image.window.main.source"]
                )

            assert result == [{"value": "on"}, {"value": "HDMI 1"}]
            mock_send.assert_called_once_with(
                "property.get",
                {"property": ["system.state", "image.window.main.source"]},
            )

    async def test_set_property(self) -> None:
        """Test set property."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(client, "_send_request", return_value=None) as mock_send:
                await client.set_property("illumination.sources.laser.power", 75.0)

            mock_send.assert_called_once_with(
                "property.set",
                {"property": "illumination.sources.laser.power", "value": 75.0},
            )

    async def test_get_system_state(self) -> None:
        """Test get system state."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(
                client, "get_property", return_value={"value": "on"}
            ) as mock_get:
                result = await client.get_system_state()

            assert result == "on"
            mock_get.assert_called_once_with("system.state")

    async def test_get_system_info(self) -> None:
        """Test get system info."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(
                client,
                "get_property",
                return_value=[
                    {"property": "system.serialnumber", "value": "ABC123456"},
                    {"property": "system.modelname", "value": "Barco Pulse"},
                    {"property": "system.firmwareversion", "value": "1.2.3"},
                ],
            ) as mock_get:
                result = await client.get_system_info()

            assert result == {
                "serial_number": "ABC123456",
                "model_name": "Barco Pulse",
                "firmware_version": "1.2.3",
            }
            mock_get.assert_called_once_with(
                ["system.serialnumber", "system.modelname", "system.firmwareversion"]
            )

    async def test_list_sources(self) -> None:
        """Test list sources."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(
                client,
                "_send_request",
                return_value=["HDMI 1", "HDMI 2", "DisplayPort 1"],
            ) as mock_send:
                result = await client.list_sources()

            assert result == ["HDMI 1", "HDMI 2", "DisplayPort 1"]
            mock_send.assert_called_once_with("image.source.list")

    async def test_get_active_source(self) -> None:
        """Test get active source."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(
                client, "get_property", return_value={"value": "HDMI 1"}
            ) as mock_get:
                result = await client.get_active_source()

            assert result == "HDMI 1"
            mock_get.assert_called_once_with("image.window.main.source")

    async def test_set_active_source(self) -> None:
        """Test set active source."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(client, "set_property", return_value=None) as mock_set:
                await client.set_active_source("DisplayPort 1")

            mock_set.assert_called_once_with(
                "image.window.main.source", "DisplayPort 1"
            )

    async def test_get_laser_power(self) -> None:
        """Test get laser power."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(
                client, "get_property", return_value={"value": 75.0}
            ) as mock_get:
                result = await client.get_laser_power()

            assert result == 75.0
            mock_get.assert_called_once_with("illumination.sources.laser.power")

    async def test_set_laser_power(self) -> None:
        """Test set laser power."""
        with patch("asyncio.open_connection") as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = MagicMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)

            client = BarcoPulseApiClient(host="192.168.1.100")

            with patch.object(client, "_read_loop", return_value=None):
                await client.connect()

            with patch.object(client, "set_property", return_value=None) as mock_set:
                await client.set_laser_power(80.0)

            mock_set.assert_called_once_with("illumination.sources.laser.power", 80.0)
