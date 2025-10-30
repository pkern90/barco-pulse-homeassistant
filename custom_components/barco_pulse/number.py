"""Barco Pulse number platform."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)
from homeassistant.const import PERCENTAGE

from .entity import BarcoEntity
from .helpers import handle_api_errors, safe_refresh

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoDataUpdateCoordinator
    from .data import BarcoRuntimeData

_LOGGER = logging.getLogger(__name__)


class BarcoNumberEntity(BarcoEntity, NumberEntity):
    """Base class for Barco number entities with shared validation logic."""

    _attr_mode = NumberMode.SLIDER

    @handle_api_errors
    async def _set_value_with_validation(self, value: float, method_name: str) -> None:
        """
        Validate and set value with proper error handling.

        Args:
            value: The value to set
            method_name: Name of the device method to call (e.g., 'set_brightness')

        Raises:
            ValueError: If value is out of range

        """
        # Validate bounds
        if value < self.native_min_value or value > self.native_max_value:
            msg = (
                f"Value {value} out of range "
                f"[{self.native_min_value}, {self.native_max_value}]"
            )
            _LOGGER.error("%s validation failed: %s", method_name, msg)
            raise ValueError(msg)

        # Call the device method
        method = getattr(self.coordinator.device, method_name)
        await method(value)

        # Request refresh
        await safe_refresh(self.coordinator, method_name)


class BarcoLaserPowerNumber(BarcoNumberEntity):
    """Barco Pulse laser power number entity."""

    _attr_translation_key = "laser_power"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = NumberDeviceClass.POWER_FACTOR

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the laser power number."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_laser_power"

    @property
    def native_value(self) -> float | None:
        """Return the current laser power percentage."""
        return self.coordinator.data.get("laser_power")

    @property
    def native_min_value(self) -> float:
        """Return the minimum laser power value."""
        return self.coordinator.data.get("laser_min", 0.0)

    @property
    def native_max_value(self) -> float:
        """Return the maximum laser power value."""
        return self.coordinator.data.get("laser_max", 100.0)

    async def async_set_native_value(self, value: float) -> None:
        """Set the laser power with validation."""
        await self._set_value_with_validation(value, "set_laser_power")


class BarcoBrightnessNumber(BarcoNumberEntity):
    """Barco Pulse brightness number entity."""

    _attr_translation_key = "brightness"
    _attr_native_min_value = -1.0
    _attr_native_max_value = 1.0
    _attr_native_step = 0.01

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the brightness number."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_brightness"

    @property
    def native_value(self) -> float | None:
        """Return the current brightness value."""
        return self.coordinator.data.get("brightness")

    async def async_set_native_value(self, value: float) -> None:
        """Set the brightness with validation and error handling."""
        await self._set_value_with_validation(value, "set_brightness")


class BarcoContrastNumber(BarcoNumberEntity):
    """Barco Pulse contrast number entity."""

    _attr_translation_key = "contrast"
    _attr_native_min_value = -1.0
    _attr_native_max_value = 1.0
    _attr_native_step = 0.01

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the contrast number."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_contrast"

    @property
    def native_value(self) -> float | None:
        """Return the current contrast value."""
        return self.coordinator.data.get("contrast")

    async def async_set_native_value(self, value: float) -> None:
        """Set the contrast with validation and error handling."""
        await self._set_value_with_validation(value, "set_contrast")


class BarcoSaturationNumber(BarcoNumberEntity):
    """Barco Pulse saturation number entity."""

    _attr_translation_key = "saturation"
    _attr_native_min_value = -1.0
    _attr_native_max_value = 1.0
    _attr_native_step = 0.01

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the saturation number."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_saturation"

    @property
    def native_value(self) -> float | None:
        """Return the current saturation value."""
        return self.coordinator.data.get("saturation")

    async def async_set_native_value(self, value: float) -> None:
        """Set the saturation with validation and error handling."""
        await self._set_value_with_validation(value, "set_saturation")


class BarcoHueNumber(BarcoNumberEntity):
    """Barco Pulse hue number entity."""

    _attr_translation_key = "hue"
    _attr_native_min_value = -1.0
    _attr_native_max_value = 1.0
    _attr_native_step = 0.01

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the hue number."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_hue"

    @property
    def native_value(self) -> float | None:
        """Return the current hue value."""
        return self.coordinator.data.get("hue")

    async def async_set_native_value(self, value: float) -> None:
        """Set the hue with validation and error handling."""
        await self._set_value_with_validation(value, "set_hue")


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Barco Pulse number entities from a config entry."""
    runtime_data: BarcoRuntimeData = entry.runtime_data
    coordinator = runtime_data.coordinator

    entities = [
        BarcoLaserPowerNumber(coordinator),
        BarcoBrightnessNumber(coordinator),
        BarcoContrastNumber(coordinator),
        BarcoSaturationNumber(coordinator),
        BarcoHueNumber(coordinator),
    ]

    async_add_entities(entities)
