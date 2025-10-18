"""Tests for the Barco Pulse config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.barco_pulse.api import (
    BarcoPulseApiError,
    BarcoPulseAuthenticationError,
    BarcoPulseConnectionError,
)
from custom_components.barco_pulse.const import CONF_AUTH_CODE, CONF_PORT, DOMAIN


async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test successful user config flow."""
    with patch(
        "custom_components.barco_pulse.config_flow.BarcoPulseApiClient"
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.get_system_info = AsyncMock(
            return_value={
                "serial_number": "ABC123456",
                "model_name": "Barco Pulse",
                "firmware_version": "1.2.3",
            }
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"] == {}

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 9090,
            },
        )

        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["title"] == "Barco Pulse (ABC123456)"
        assert result["data"] == {
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 9090,
        }
        assert result["result"].unique_id == "ABC123456"

        mock_client.connect.assert_called_once()
        mock_client.disconnect.assert_called_once()


async def test_user_flow_with_auth_code(hass: HomeAssistant) -> None:
    """Test user config flow with authentication code."""
    with patch(
        "custom_components.barco_pulse.config_flow.BarcoPulseApiClient"
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.authenticate = AsyncMock()
        mock_client.get_system_info = AsyncMock(
            return_value={
                "serial_number": "ABC123456",
                "model_name": "Barco Pulse Pro",
                "firmware_version": "2.0.0",
            }
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 9090,
                CONF_AUTH_CODE: 12345,
            },
        )

        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["title"] == "Barco Pulse Pro (ABC123456)"
        assert result["data"] == {
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 9090,
            CONF_AUTH_CODE: 12345,
        }

        mock_client.connect.assert_called_once()
        # Note: authenticate is called inside connect(), so we can't verify it separately
        # when connect() is mocked
        mock_client.disconnect.assert_called_once()


async def test_user_flow_connection_error(hass: HomeAssistant) -> None:
    """Test user config flow with connection error."""
    with patch(
        "custom_components.barco_pulse.config_flow.BarcoPulseApiClient"
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.connect = AsyncMock(
            side_effect=BarcoPulseConnectionError("Connection refused")
        )
        mock_client.disconnect = AsyncMock()

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 9090,
            },
        )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "connection"}


async def test_user_flow_auth_error(hass: HomeAssistant) -> None:
    """Test user config flow with authentication error."""
    with patch(
        "custom_components.barco_pulse.config_flow.BarcoPulseApiClient"
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        # Auth error happens inside connect() when auth_code is provided
        mock_client.connect = AsyncMock(
            side_effect=BarcoPulseAuthenticationError("Invalid code")
        )
        mock_client.disconnect = AsyncMock()

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 9090,
                CONF_AUTH_CODE: 99999,
            },
        )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "auth"}


async def test_user_flow_unknown_error(hass: HomeAssistant) -> None:
    """Test user config flow with unknown error."""
    with patch(
        "custom_components.barco_pulse.config_flow.BarcoPulseApiClient"
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.get_system_info = AsyncMock(
            side_effect=BarcoPulseApiError("Unknown error")
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 9090,
            },
        )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "unknown"}


async def test_user_flow_already_configured(hass: HomeAssistant) -> None:
    """Test user config flow when projector is already configured."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 9090,
        },
        unique_id="ABC123456",
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.barco_pulse.config_flow.BarcoPulseApiClient"
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.get_system_info = AsyncMock(
            return_value={
                "serial_number": "ABC123456",
                "model_name": "Barco Pulse",
                "firmware_version": "1.2.3",
            }
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 9090,
            },
        )

        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "already_configured"


# Mock ConfigEntry for testing


# No longer need custom MockConfigEntry class - using pytest_homeassistant_custom_component.common.MockConfigEntry
