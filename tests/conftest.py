"""Fixtures for Barco Pulse tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.barco_pulse.const import CONF_AUTH_CODE, CONF_PORT, DOMAIN

if TYPE_CHECKING:
    from collections.abc import Generator
    from homeassistant.core import HomeAssistant

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> None:
    """Enable custom integrations."""


@pytest.fixture(name="mock_barco_pulse_api")
def mock_barco_pulse_api_fixture() -> Generator[MagicMock]:
    """Mock BarcoPulseApiClient."""
    with patch(
        "custom_components.barco_pulse.api.BarcoPulseApiClient", autospec=True
    ) as mock_api:
        client = mock_api.return_value
        client.connect = AsyncMock()
        client.disconnect = AsyncMock()
        client.authenticate = AsyncMock()
        client.get_system_info = AsyncMock(
            return_value={
                "serial_number": "ABC123456",
                "model_name": "Barco Pulse",
                "firmware_version": "1.2.3",
            }
        )
        client.get_system_state = AsyncMock(return_value="on")
        client.get_active_source = AsyncMock(return_value="HDMI 1")
        client.list_sources = AsyncMock(
            return_value=["HDMI 1", "HDMI 2", "DisplayPort 1"]
        )
        client.get_laser_power = AsyncMock(return_value=75.0)
        client.set_laser_power = AsyncMock()
        client.power_on = AsyncMock()
        client.power_off = AsyncMock()
        client.set_active_source = AsyncMock()
        client.is_connected = True
        yield client


@pytest.fixture(name="mock_config_entry")
def mock_config_entry_fixture(hass: HomeAssistant) -> MockConfigEntry:
    """Mock ConfigEntry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Barco Pulse (ABC123456)",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 9090,
            CONF_AUTH_CODE: 12345,
        },
        entry_id="test_entry_id",
        unique_id="ABC123456",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture(name="mock_setup_entry")
def mock_setup_entry_fixture() -> Generator[AsyncMock]:
    """Mock async_setup_entry."""
    with patch(
        "custom_components.barco_pulse.async_setup_entry",
        return_value=True,
    ) as mock_setup:
        yield mock_setup


@pytest.fixture(name="coordinator_data")
def coordinator_data_fixture() -> dict[str, Any]:
    """Return mock coordinator data."""
    return {
        "system": {
            "state": "on",
            "serial_number": "ABC123456",
            "model_name": "Barco Pulse",
            "firmware_version": "1.2.3",
        },
        "power": {
            "is_on": True,
        },
        "source": {
            "active": "HDMI 1",
            "available": ["HDMI 1", "HDMI 2", "DisplayPort 1"],
        },
        "illumination": {
            "laser_power": 75.0,
        },
    }


@pytest.fixture(name="mock_coordinator")
def mock_coordinator_fixture(
    hass: MagicMock,
    mock_barco_pulse_api: MagicMock,
    mock_config_entry: MagicMock,
    coordinator_data: dict[str, Any],
) -> MagicMock:
    """Mock BarcoPulseDataUpdateCoordinator."""
    coordinator = MagicMock()
    coordinator.hass = hass
    coordinator.data = coordinator_data
    coordinator.client = mock_barco_pulse_api
    coordinator.config_entry = mock_config_entry
    coordinator.async_request_refresh = AsyncMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    return coordinator
