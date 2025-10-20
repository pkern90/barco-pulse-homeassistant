"""Barco Pulse remote platform."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.remote import RemoteEntity

from .const import POWER_STATES_ACTIVE
from .entity import BarcoEntity

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoDataUpdateCoordinator
    from .data import BarcoRuntimeData


class BarcoRemote(BarcoEntity, RemoteEntity):
    """Barco Pulse remote entity."""

    _attr_translation_key = "remote"

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the remote."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_remote"

    @property
    def is_on(self) -> bool:
        """Return True if the projector is on."""
        return self.coordinator.data.get("state") in POWER_STATES_ACTIVE

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the projector on."""
        await self.coordinator.device.power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the projector off."""
        await self.coordinator.device.power_off()
        await self.coordinator.async_request_refresh()

    async def async_send_command(self, command: Iterable[str], **_kwargs: Any) -> None:
        """Send a command to the projector."""
        for cmd in command:
            if cmd.startswith("source_"):
                # Extract source name from command (e.g., "source_HDMI 1" -> "HDMI 1")
                source_name = cmd[7:]  # Remove "source_" prefix
                await self.coordinator.device.set_source(source_name)

        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Barco Pulse remote from a config entry."""
    runtime_data: BarcoRuntimeData = entry.runtime_data
    coordinator = runtime_data.coordinator

    remote = BarcoRemote(coordinator)

    async_add_entities([remote])
