"""Base entity for Barco Pulse integration."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import BarcoDataUpdateCoordinator


class BarcoEntity(CoordinatorEntity[BarcoDataUpdateCoordinator]):
    """Base entity for Barco Pulse."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        # Build device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.config_entry.title,
            manufacturer="Barco",
            model=coordinator.data.get("model", "Pulse"),
            sw_version=coordinator.data.get("firmware_version"),
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
