"""Sensor platform for barco_pulse."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE

from .entity import BarcoPulseEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoPulseDataUpdateCoordinator
    from .data import BarcoPulseConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="system_state",
        name="Projector State",
        icon="mdi:projector",
        device_class=SensorDeviceClass.ENUM,
        options=[
            "boot",
            "eco",
            "standby",
            "ready",
            "conditioning",
            "on",
            "deconditioning",
        ],
    ),
    SensorEntityDescription(
        key="laser_power",
        name="Laser Power",
        icon="mdi:laser-pointer",
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="active_source",
        name="Active Source",
        icon="mdi:video-input-hdmi",
    ),
    SensorEntityDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:chip",
        entity_registry_enabled_default=False,  # Disabled by default
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: BarcoPulseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        BarcoPulseSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class BarcoPulseSensor(BarcoPulseEntity, SensorEntity):
    """barco_pulse Sensor class."""

    def __init__(
        self,
        coordinator: BarcoPulseDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str | float | None:
        """Return the native value of the sensor."""
        # Map entity key to coordinator data
        if self.entity_description.key == "system_state":
            return self.coordinator.data.get("system", {}).get("state")
        if self.entity_description.key == "laser_power":
            return self.coordinator.data.get("illumination", {}).get("laser_power")
        if self.entity_description.key == "active_source":
            return self.coordinator.data.get("source", {}).get("active")
        if self.entity_description.key == "firmware_version":
            return self.coordinator.data.get("system", {}).get("firmware_version")
        return None
