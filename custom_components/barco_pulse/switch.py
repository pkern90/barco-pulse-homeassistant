"""Barco Pulse switch platform."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity

from .const import POWER_STATES_ACTIVE
from .entity import BarcoEntity
from .helpers import handle_api_errors, safe_refresh

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoDataUpdateCoordinator
    from .data import BarcoRuntimeData

_LOGGER = logging.getLogger(__name__)


class BarcoPowerSwitch(BarcoEntity, SwitchEntity):
    """Barco Pulse power switch entity."""

    _attr_translation_key = "power"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the power switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_power_switch"

    @property
    def is_on(self) -> bool:
        """Return True if the projector is on."""
        return self.coordinator.data.get("state") in POWER_STATES_ACTIVE

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the projector on."""
        await self._turn_on_with_refresh()

    @handle_api_errors
    async def _turn_on_with_refresh(self) -> None:
        """Execute power on command."""
        await self.coordinator.device.power_on()
        await safe_refresh(self.coordinator, "power on")

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the projector off."""
        await self._turn_off_with_refresh()

    @handle_api_errors
    async def _turn_off_with_refresh(self) -> None:
        """Execute power off command."""
        await self.coordinator.device.power_off()
        await safe_refresh(self.coordinator, "power off")


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Barco Pulse switch from a config entry."""
    runtime_data: BarcoRuntimeData = entry.runtime_data
    coordinator = runtime_data.coordinator

    switch = BarcoPowerSwitch(coordinator)

    async_add_entities([switch])
