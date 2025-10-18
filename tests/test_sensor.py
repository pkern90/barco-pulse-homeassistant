"""Tests for Barco Pulse sensor entities."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant

from custom_components.barco_pulse.sensor import (
    ENTITY_DESCRIPTIONS,
    BarcoPulseSensor,
    async_setup_entry,
)


async def test_sensor_setup(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    mock_config_entry: MagicMock,
) -> None:
    """Test sensor platform setup."""
    mock_config_entry.runtime_data = MagicMock()
    mock_config_entry.runtime_data.coordinator = mock_coordinator

    async_add_entities = MagicMock()
    await async_setup_entry(hass, mock_config_entry, async_add_entities)

    async_add_entities.assert_called_once()
    entities = list(async_add_entities.call_args[0][0])
    assert len(entities) == len(ENTITY_DESCRIPTIONS)


async def test_system_state_sensor(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    coordinator_data: dict[str, Any],
) -> None:
    """Test system state sensor."""
    description = ENTITY_DESCRIPTIONS[0]  # system_state
    sensor = BarcoPulseSensor(mock_coordinator, description)

    assert sensor.unique_id == "ABC123456_system_state"
    assert sensor.native_value == "on"


async def test_laser_power_sensor(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    coordinator_data: dict[str, Any],
) -> None:
    """Test laser power sensor."""
    description = ENTITY_DESCRIPTIONS[1]  # laser_power
    sensor = BarcoPulseSensor(mock_coordinator, description)

    assert sensor.unique_id == "ABC123456_laser_power"
    assert sensor.native_value == 75.0
    assert sensor.native_unit_of_measurement == PERCENTAGE


async def test_active_source_sensor(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    coordinator_data: dict[str, Any],
) -> None:
    """Test active source sensor."""
    description = ENTITY_DESCRIPTIONS[2]  # active_source
    sensor = BarcoPulseSensor(mock_coordinator, description)

    assert sensor.unique_id == "ABC123456_active_source"
    assert sensor.native_value == "HDMI 1"


async def test_firmware_version_sensor(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    coordinator_data: dict[str, Any],
) -> None:
    """Test firmware version sensor."""
    description = ENTITY_DESCRIPTIONS[3]  # firmware_version
    sensor = BarcoPulseSensor(mock_coordinator, description)

    assert sensor.unique_id == "ABC123456_firmware_version"
    assert sensor.native_value == "1.2.3"


async def test_sensor_unavailable_when_no_data(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
) -> None:
    """Test sensor is unavailable when coordinator has no data."""
    mock_coordinator.data = None

    description = ENTITY_DESCRIPTIONS[0]
    sensor = BarcoPulseSensor(mock_coordinator, description)

    assert sensor.native_value is None
