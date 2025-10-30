"""Base entity for Barco Pulse integration."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import BarcoDataUpdateCoordinator
from .helpers import handle_api_errors, safe_refresh


class BarcoEntity(CoordinatorEntity[BarcoDataUpdateCoordinator]):
    """Base entity for Barco Pulse."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self.coordinator.config_entry.title,
            manufacturer="Barco",
            model=self.coordinator.data.get("model", "Pulse"),
            sw_version=self.coordinator.data.get("firmware_version"),
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class BarcoPowerMixin:
    """Mixin for entities that support power on/off commands."""

    coordinator: BarcoDataUpdateCoordinator

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the projector on."""

        @handle_api_errors
        async def _turn_on() -> None:
            await self.coordinator.device.power_on()
            await safe_refresh(self.coordinator, "power on")

        await _turn_on()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the projector off."""

        @handle_api_errors
        async def _turn_off() -> None:
            await self.coordinator.device.power_off()
            await safe_refresh(self.coordinator, "power off")

        await _turn_off()
