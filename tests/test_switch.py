"""Tests for Barco Pulse switch entities."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from custom_components.barco_pulse.switch import (
    ENTITY_DESCRIPTIONS,
    BarcoPulseSwitch,
    async_setup_entry,
)


async def test_switch_setup(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    mock_config_entry: MagicMock,
) -> None:
    """Test switch platform setup."""
    mock_config_entry.runtime_data = MagicMock()
    mock_config_entry.runtime_data.coordinator = mock_coordinator

    async_add_entities = MagicMock()
    await async_setup_entry(hass, mock_config_entry, async_add_entities)

    async_add_entities.assert_called_once()
    entities = list(async_add_entities.call_args[0][0])
    assert len(entities) == len(ENTITY_DESCRIPTIONS)


async def test_power_switch_on(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    coordinator_data: dict[str, Any],
) -> None:
    """Test power switch when projector is on."""
    description = ENTITY_DESCRIPTIONS[0]  # power
    switch = BarcoPulseSwitch(mock_coordinator, description)

    assert switch.unique_id == "ABC123456_power"
    assert switch.is_on is True


async def test_power_switch_off(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    coordinator_data: dict[str, Any],
) -> None:
    """Test power switch when projector is off."""
    mock_coordinator.data["power"]["is_on"] = False
    mock_coordinator.data["system"]["state"] = "standby"

    description = ENTITY_DESCRIPTIONS[0]  # power
    switch = BarcoPulseSwitch(mock_coordinator, description)

    assert switch.is_on is False


async def test_turn_on(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    mock_barco_pulse_api: MagicMock,
) -> None:
    """Test turning on the projector."""
    # Setup runtime_data with client
    mock_coordinator.config_entry.runtime_data = MagicMock()
    mock_coordinator.config_entry.runtime_data.client = mock_barco_pulse_api

    description = ENTITY_DESCRIPTIONS[0]  # power
    switch = BarcoPulseSwitch(mock_coordinator, description)

    await switch.async_turn_on()

    mock_barco_pulse_api.power_on.assert_called_once()
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_turn_off(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
    mock_barco_pulse_api: MagicMock,
) -> None:
    """Test turning off the projector."""
    # Setup runtime_data with client
    mock_coordinator.config_entry.runtime_data = MagicMock()
    mock_coordinator.config_entry.runtime_data.client = mock_barco_pulse_api

    description = ENTITY_DESCRIPTIONS[0]  # power
    switch = BarcoPulseSwitch(mock_coordinator, description)

    await switch.async_turn_off()

    mock_barco_pulse_api.power_off.assert_called_once()
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_switch_unavailable_when_no_data(
    hass: HomeAssistant,
    mock_coordinator: MagicMock,
) -> None:
    """Test switch is unavailable when coordinator has no data."""
    mock_coordinator.data = None

    description = ENTITY_DESCRIPTIONS[0]
    switch = BarcoPulseSwitch(mock_coordinator, description)

    assert switch.is_on is None
