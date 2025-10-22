"""Barco Pulse remote platform."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.remote import RemoteEntity

from .const import POWER_STATES_ACTIVE, PRESET_MAX_NUMBER
from .entity import BarcoEntity
from .helpers import handle_api_errors, safe_refresh

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoDataUpdateCoordinator
    from .data import BarcoRuntimeData

_LOGGER = logging.getLogger(__name__)


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
        """Turn the projector on with error handling."""
        await self._turn_on_with_refresh()

    @handle_api_errors
    async def _turn_on_with_refresh(self) -> None:
        """Execute power on command."""
        await self.coordinator.device.power_on()
        await safe_refresh(self.coordinator, "power on")

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the projector off with error handling."""
        await self._turn_off_with_refresh()

    @handle_api_errors
    async def _turn_off_with_refresh(self) -> None:
        """Execute power off command."""
        await self.coordinator.device.power_off()
        await safe_refresh(self.coordinator, "power off")

    @handle_api_errors
    async def _execute_command(self, cmd: str) -> None:
        """Execute a single command with validation and error handling."""
        if cmd.startswith("source_"):
            # Extract source name (e.g., "source_HDMI 1" -> "HDMI 1")
            source_name = cmd[7:]
            if not source_name:
                _LOGGER.warning("Empty source name in command: %s", cmd)
                return
            await self.coordinator.device.set_source(source_name)

        elif cmd.startswith("preset_"):
            # Extract preset number (e.g., "preset_5" -> 5)
            try:
                preset_str = cmd[7:]
                preset_num = int(preset_str)

                # Validate preset number range
                if preset_num < 0 or preset_num > PRESET_MAX_NUMBER:
                    _LOGGER.warning(
                        "Preset number %d out of range [0, %d]",
                        preset_num,
                        PRESET_MAX_NUMBER,
                    )
                    return

                await self.coordinator.device.activate_preset(preset_num)

            except (ValueError, IndexError):
                _LOGGER.warning("Invalid preset number in command: %s", cmd)
                return

        elif cmd.startswith("profile_"):
            # Extract profile name (e.g., "profile_Cinema" -> "Cinema")
            profile_name = cmd[8:]
            if not profile_name:
                _LOGGER.warning("Empty profile name in command: %s", cmd)
                return
            await self.coordinator.device.activate_profile(profile_name)

        else:
            _LOGGER.warning("Unknown command format: %s", cmd)

    async def async_send_command(self, command: Iterable[str], **_kwargs: Any) -> None:
        """
        Send a command to the projector with validation and error handling.

        Supported command formats:
        - source_<name>: Switch to input source (e.g., "source_HDMI 1")
        - preset_<number>: Activate preset by number (e.g., "preset_5")
        - profile_<name>: Activate profile by name (e.g., "profile_Cinema")
        """
        for cmd in command:
            if not isinstance(cmd, str):
                _LOGGER.warning("Invalid command type: %s (expected str)", type(cmd))
                continue

            await self._execute_command(cmd)

        await safe_refresh(self.coordinator, "send command")


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
