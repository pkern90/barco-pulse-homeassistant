"""Tests for Barco Pulse binary sensor entities."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from custom_components.barco_pulse.binary_sensor import (
    ENTITY_DESCRIPTIONS,
    BarcoPulseBinarySensor,
    async_setup_entry,
)


async def test_binary_sensor_setup(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    mock_config_entry: MagicMock,
) -> None:
    """Test binary sensor platform setup."""
    mock_config_entry.runtime_data = MagicMock()
    mock_config_entry.runtime_data.coordinator = mock_coordinator

    async_add_entities = MagicMock()
    await async_setup_entry(hass, mock_config_entry, async_add_entities)

    async_add_entities.assert_called_once()
    entities = list(async_add_entities.call_args[0][0])
    assert len(entities) == len(ENTITY_DESCRIPTIONS)


async def test_power_status_on(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    coordinator_data: dict[str, Any],
) -> None:
    """Test power status binary sensor when projector is on."""
    description = ENTITY_DESCRIPTIONS[0]  # power_status
    sensor = BarcoPulseBinarySensor(mock_coordinator, description)

    assert sensor.unique_id == "ABC123456_power_status"
    assert sensor.is_on is True


async def test_power_status_off(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    coordinator_data: dict[str, Any],
) -> None:
    """Test power status binary sensor when projector is off."""
    mock_coordinator.data["power"]["is_on"] = False
    mock_coordinator.data["system"]["state"] = "standby"

    description = ENTITY_DESCRIPTIONS[0]  # power_status
    sensor = BarcoPulseBinarySensor(mock_coordinator, description)

    assert sensor.is_on is False


async def test_binary_sensor_unavailable_when_no_data(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
) -> None:
    """Test binary sensor is unavailable when coordinator has no data."""
    mock_coordinator.data = None

    description = ENTITY_DESCRIPTIONS[0]
    sensor = BarcoPulseBinarySensor(mock_coordinator, description)

    assert sensor.is_on is None
