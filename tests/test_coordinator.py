"""Tests for the Barco Pulse coordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.barco_pulse.api import (
    BarcoPulseApiError,
    BarcoPulseAuthenticationError,
    BarcoPulseConnectionError,
)
from custom_components.barco_pulse.coordinator import BarcoPulseDataUpdateCoordinator


async def test_coordinator_update_success(hass: HomeAssistant) -> None:
    """Test successful data update."""
    mock_client = MagicMock()
    mock_client.get_system_state = AsyncMock(return_value="on")
    mock_client.get_system_info = AsyncMock(
        return_value={
            "serial_number": "ABC123456",
            "model_name": "Barco Pulse",
            "firmware_version": "1.2.3",
        }
    )
    mock_client.get_active_source = AsyncMock(return_value="HDMI 1")
    mock_client.list_sources = AsyncMock(
        return_value=["HDMI 1", "HDMI 2", "DisplayPort 1"]
    )
    mock_client.get_laser_power = AsyncMock(return_value=75.0)

    coordinator = BarcoPulseDataUpdateCoordinator(
        hass=hass,
        logger=MagicMock(),
        name="Test",
        update_interval=timedelta(seconds=30),
        client=mock_client,
    )

    data = await coordinator._async_update_data()

    assert data["system"]["state"] == "on"
    assert data["system"]["serial_number"] == "ABC123456"
    assert data["system"]["model_name"] == "Barco Pulse"
    assert data["system"]["firmware_version"] == "1.2.3"
    assert data["power"]["is_on"] is True
    assert data["source"]["active"] == "HDMI 1"
    assert data["source"]["available"] == ["HDMI 1", "HDMI 2", "DisplayPort 1"]
    assert data["illumination"]["laser_power"] == 75.0


async def test_coordinator_power_off_state(hass: HomeAssistant) -> None:
    """Test coordinator with power off state."""
    mock_client = MagicMock()
    mock_client.get_system_state = AsyncMock(return_value="standby")
    mock_client.get_system_info = AsyncMock(
        return_value={
            "serial_number": "ABC123456",
            "model_name": "Barco Pulse",
            "firmware_version": "1.2.3",
        }
    )
    mock_client.get_active_source = AsyncMock(return_value="HDMI 1")
    mock_client.list_sources = AsyncMock(return_value=["HDMI 1", "HDMI 2"])
    mock_client.get_laser_power = AsyncMock(return_value=0.0)

    coordinator = BarcoPulseDataUpdateCoordinator(
        hass=hass,
        logger=MagicMock(),
        name="Test",
        update_interval=timedelta(seconds=30),
        client=mock_client,
    )

    data = await coordinator._async_update_data()

    assert data["system"]["state"] == "standby"
    assert data["power"]["is_on"] is False


async def test_coordinator_connection_error(hass: HomeAssistant) -> None:
    """Test coordinator handles connection error."""
    mock_client = MagicMock()
    mock_client.get_system_state = AsyncMock(
        side_effect=BarcoPulseConnectionError("Connection failed")
    )

    coordinator = BarcoPulseDataUpdateCoordinator(
        hass=hass,
        logger=MagicMock(),
        name="Test",
        update_interval=timedelta(seconds=30),
        client=mock_client,
    )

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_coordinator_auth_error(hass: HomeAssistant) -> None:
    """Test coordinator handles authentication error."""
    mock_client = MagicMock()
    mock_client.get_system_state = AsyncMock(
        side_effect=BarcoPulseAuthenticationError("Auth failed")
    )

    coordinator = BarcoPulseDataUpdateCoordinator(
        hass=hass,
        logger=MagicMock(),
        name="Test",
        update_interval=timedelta(seconds=30),
        client=mock_client,
    )

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


async def test_coordinator_api_error(hass: HomeAssistant) -> None:
    """Test coordinator handles API error."""
    mock_client = MagicMock()
    mock_client.get_system_state = AsyncMock(
        side_effect=BarcoPulseApiError("API error")
    )

    coordinator = BarcoPulseDataUpdateCoordinator(
        hass=hass,
        logger=MagicMock(),
        name="Test",
        update_interval=timedelta(seconds=30),
        client=mock_client,
    )

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
