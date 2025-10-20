"""Barco Pulse sensor platform."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.entity import EntityCategory

from .entity import BarcoEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoDataUpdateCoordinator
    from .data import BarcoRuntimeData


@dataclass(frozen=True, kw_only=True)
class BarcoSensorEntityDescription(SensorEntityDescription):
    """Describe Barco sensor entity."""

    value_fn: Callable[[dict[str, Any]], str | int | float | None]
    enabled_default: bool = True


SENSORS: tuple[BarcoSensorEntityDescription, ...] = (
    BarcoSensorEntityDescription(
        key="state",
        translation_key="state",
        icon="mdi:power",
        value_fn=lambda data: data.get("state"),
    ),
    BarcoSensorEntityDescription(
        key="serial_number",
        translation_key="serial_number",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("serial_number"),
    ),
    BarcoSensorEntityDescription(
        key="model",
        translation_key="model",
        icon="mdi:projector",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("model"),
    ),
    BarcoSensorEntityDescription(
        key="firmware_version",
        translation_key="firmware_version",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firmware_version"),
    ),
    BarcoSensorEntityDescription(
        key="laser_power",
        translation_key="laser_power",
        icon="mdi:laser-pointer",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("laser_power"),
    ),
    BarcoSensorEntityDescription(
        key="source",
        translation_key="source",
        icon="mdi:video-input-hdmi",
        value_fn=lambda data: data.get("source"),
    ),
)


class BarcoSensor(BarcoEntity, SensorEntity):
    """Barco Pulse sensor entity."""

    entity_description: BarcoSensorEntityDescription

    def __init__(
        self,
        coordinator: BarcoDataUpdateCoordinator,
        description: BarcoSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"
        self._attr_entity_registry_enabled_default = description.enabled_default

    @property
    def native_value(self) -> str | int | float | None:
        """Return the native value of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Barco Pulse sensors from a config entry."""
    runtime_data: BarcoRuntimeData = entry.runtime_data
    coordinator = runtime_data.coordinator

    entities = [BarcoSensor(coordinator, description) for description in SENSORS]

    async_add_entities(entities)
