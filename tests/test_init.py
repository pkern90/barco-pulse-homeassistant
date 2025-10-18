"""Tests for the Barco Pulse integration init."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.barco_pulse.api import BarcoPulseConnectionError


async def test_setup_entry_success(hass: HomeAssistant, mock_config_entry) -> None:
    """Test successful setup of config entry."""
    with (
        patch("custom_components.barco_pulse.BarcoPulseApiClient") as mock_client_class,
        patch(
            "custom_components.barco_pulse.BarcoPulseDataUpdateCoordinator"
        ) as mock_coordinator_class,
    ):
        mock_client = mock_client_class.return_value
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()

        mock_coordinator = mock_coordinator_class.return_value
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.config_entry = mock_config_entry

        result = await hass.config_entries.async_setup(mock_config_entry.entry_id)

        assert result is True
        assert mock_config_entry.state is ConfigEntryState.LOADED
        mock_client.connect.assert_called_once()


async def test_setup_entry_connection_failure(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test setup of config entry with connection failure."""
    with patch(
        "custom_components.barco_pulse.BarcoPulseApiClient"
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.connect = AsyncMock(
            side_effect=BarcoPulseConnectionError("Connection failed")
        )
        mock_client.disconnect = AsyncMock()

        result = await hass.config_entries.async_setup(mock_config_entry.entry_id)

        assert result is False


async def test_unload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test successful unload of config entry."""
    with (
        patch("custom_components.barco_pulse.BarcoPulseApiClient") as mock_client_class,
        patch(
            "custom_components.barco_pulse.BarcoPulseDataUpdateCoordinator"
        ) as mock_coordinator_class,
    ):
        mock_client = mock_client_class.return_value
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()

        mock_coordinator = mock_coordinator_class.return_value
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.config_entry = mock_config_entry

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        assert mock_config_entry.state is ConfigEntryState.LOADED

        await hass.config_entries.async_unload(mock_config_entry.entry_id)
        assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_reload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test successful reload of config entry."""
    with (
        patch("custom_components.barco_pulse.BarcoPulseApiClient") as mock_client_class,
        patch(
            "custom_components.barco_pulse.BarcoPulseDataUpdateCoordinator"
        ) as mock_coordinator_class,
    ):
        mock_client = mock_client_class.return_value
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()

        mock_coordinator = mock_coordinator_class.return_value
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.config_entry = mock_config_entry

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        assert mock_config_entry.state is ConfigEntryState.LOADED

        await hass.config_entries.async_reload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.LOADED
        assert mock_client.disconnect.call_count == 1
        assert mock_client.connect.call_count == 2
