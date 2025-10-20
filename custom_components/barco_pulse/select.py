"""Barco Pulse select platform."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity

from .entity import BarcoEntity

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
        """Select a new source."""
        await self.coordinator.device.set_source(option)
        await self.coordinator.async_request_refresh()


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
        return state in ("on", "ready")

    async def async_select_option(self, option: str) -> None:
        """Select and activate a preset."""
        # Extract preset number from "Preset X" format
        try:
            preset_num = int(option.split()[-1])
            await self.coordinator.device.activate_preset(preset_num)
            await self.coordinator.async_request_refresh()
        except (ValueError, IndexError):
            _LOGGER.exception("Failed to parse preset option %s", option)


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
    ]

    async_add_entities(entities)
