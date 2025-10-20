"""Binary sensor platform for Barco Pulse integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import POWER_STATES_ACTIVE
from .entity import BarcoEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoDataUpdateCoordinator
    from .data import BarcoRuntimeData


@dataclass(frozen=True, kw_only=True)
class BarcoBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe Barco binary sensor entity."""

    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSORS: tuple[BarcoBinarySensorEntityDescription, ...] = (
    BarcoBinarySensorEntityDescription(
        key="power",
        translation_key="power",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: data.get("state") in POWER_STATES_ACTIVE,
    ),
)


class BarcoBinarySensor(BarcoEntity, BinarySensorEntity):
    """Barco Pulse binary sensor entity."""

    entity_description: BarcoBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: BarcoDataUpdateCoordinator,
        description: BarcoBinarySensorEntityDescription,
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Barco Pulse binary sensors."""
    runtime_data: BarcoRuntimeData = entry.runtime_data
    coordinator = runtime_data.coordinator

    entities = [
        BarcoBinarySensor(coordinator, description) for description in BINARY_SENSORS
    ]

    async_add_entities(entities)
