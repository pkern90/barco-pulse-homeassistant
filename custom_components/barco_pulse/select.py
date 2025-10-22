"""Barco Pulse select platform."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity

from .const import PRESET_MAX_NUMBER, PowerState
from .entity import BarcoEntity
from .helpers import handle_api_errors, safe_refresh

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoDataUpdateCoordinator
    from .data import BarcoRuntimeData

_LOGGER = logging.getLogger(__name__)


class BarcoSourceSelect(BarcoEntity, SelectEntity):
    """Barco Pulse source select entity."""

    _attr_translation_key = "source"
    _attr_icon = "mdi:video-input-hdmi"

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the source select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_source"

    @property
    def current_option(self) -> str | None:
        """Return the current selected source."""
        return self.coordinator.data.get("source")

    @property
    def options(self) -> list[str]:
        """Return the list of available sources."""
        sources = self.coordinator.data.get("available_sources", [])
        return sources if sources else ["Unknown"]

    async def async_select_option(self, option: str) -> None:
        """Select a new source with validation and error handling."""
        await self._select_with_validation(option, "set_source")

    @handle_api_errors
    async def _select_with_validation(self, option: str, method_name: str) -> None:
        """Validate and select option with proper error handling."""
        # Validate option
        if option not in self.options:
            msg = f"Invalid option: {option}"
            _LOGGER.error("%s validation failed: %s", method_name, msg)
            raise ValueError(msg)

        # Call the device method
        method = getattr(self.coordinator.device, method_name)
        await method(option)

        # Request refresh
        await safe_refresh(self.coordinator, method_name)


class BarcoPresetSelect(BarcoEntity, SelectEntity):
    """Barco Pulse preset select entity."""

    _attr_translation_key = "preset"
    _attr_icon = "mdi:palette"

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the preset select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_preset"

    @property
    def current_option(self) -> str | None:
        """Return the current selected preset."""
        # There's no direct way to get the "active" preset, so we don't show selection
        return None

    @property
    def options(self) -> list[str]:
        """Return the list of available presets."""
        profiles = self.coordinator.data.get("profiles", [])

        # If no profiles exist, show message
        if not profiles:
            return ["No profiles configured"]

        # Presets are numbered 0-29 (30 total slots)
        # Show all presets regardless of assignment
        return [f"Preset {preset_num}" for preset_num in range(30)]

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Only available when projector is powered on
        state = self.coordinator.data.get("state")
        return state in (PowerState.ON, PowerState.READY)

    async def async_select_option(self, option: str) -> None:
        """Select and activate a preset with validation and error handling."""
        await self._activate_preset(option)

    @handle_api_errors
    async def _activate_preset(self, option: str) -> None:
        """Parse, validate and activate preset with proper error handling."""
        # Validate option
        if option not in self.options:
            msg = f"Invalid preset option: {option}"
            _LOGGER.error("Preset validation failed: %s", msg)
            raise ValueError(msg)

        # Extract preset number from "Preset X" format
        try:
            preset_num = int(option.split()[-1])
        except (ValueError, IndexError) as err:
            msg = f"Failed to parse preset option {option}"
            _LOGGER.exception("Preset parsing failed")
            raise ValueError(msg) from err

        # Validate preset number range
        if preset_num < 0 or preset_num > PRESET_MAX_NUMBER:
            msg = f"Preset number {preset_num} out of range [0, {PRESET_MAX_NUMBER}]"
            _LOGGER.error("Preset number validation failed: %s", msg)
            raise ValueError(msg)

        # Execute preset activation
        await self.coordinator.device.activate_preset(preset_num)

        # Request refresh
        await safe_refresh(self.coordinator, "activate_preset")


class BarcoProfileSelect(BarcoEntity, SelectEntity):
    """Barco Pulse profile select entity."""

    _attr_translation_key = "profile"
    _attr_icon = "mdi:image-filter-hdr"

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the profile select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_profile"

    @property
    def current_option(self) -> str | None:
        """Return the current selected profile."""
        # There's no direct way to get the "active" profile, so we don't show selection
        return None

    @property
    def options(self) -> list[str]:
        """Return the list of available profiles."""
        profiles = self.coordinator.data.get("profiles", [])

        # If no profiles exist, show message
        if not profiles:
            return ["No profiles configured"]

        return profiles

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Only available when projector is powered on
        state = self.coordinator.data.get("state")
        return state in (PowerState.ON, PowerState.READY)

    async def async_select_option(self, option: str) -> None:
        """Select and activate a profile with validation and error handling."""
        await self._activate_profile(option)

    @handle_api_errors
    async def _activate_profile(self, option: str) -> None:
        """Validate and activate profile with proper error handling."""
        # Validate option
        if option not in self.options:
            msg = f"Invalid profile option: {option}"
            _LOGGER.error("Profile validation failed: %s", msg)
            raise ValueError(msg)

        # Execute profile activation
        await self.coordinator.device.activate_profile(option)

        # Request refresh
        await safe_refresh(self.coordinator, "activate_profile")


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Barco Pulse select from a config entry."""
    runtime_data: BarcoRuntimeData = entry.runtime_data
    coordinator = runtime_data.coordinator

    entities = [
        BarcoSourceSelect(coordinator),
        BarcoPresetSelect(coordinator),
        BarcoProfileSelect(coordinator),
    ]

    async_add_entities(entities)
