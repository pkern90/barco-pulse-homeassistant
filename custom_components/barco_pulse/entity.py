"""BarcoPulseEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import BarcoPulseDataUpdateCoordinator


class BarcoPulseEntity(CoordinatorEntity[BarcoPulseDataUpdateCoordinator]):
    """BarcoPulseEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: BarcoPulseDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        # Use serial number if available, otherwise use entry_id as fallback
        serial = None
        if coordinator.data and isinstance(coordinator.data, dict):
            serial = coordinator.data.get("system", {}).get("serial_number")

        base_id = serial or coordinator.config_entry.entry_id
        self._attr_unique_id = base_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    base_id,
                ),
            },
        )
