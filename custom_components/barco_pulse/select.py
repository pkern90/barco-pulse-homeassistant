"""Barco Pulse select platform."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity

from .entity import BarcoEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoDataUpdateCoordinator
    from .data import BarcoRuntimeData


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


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Barco Pulse select from a config entry."""
    runtime_data: BarcoRuntimeData = entry.runtime_data
    coordinator = runtime_data.coordinator

    select = BarcoSourceSelect(coordinator)

    async_add_entities([select])
