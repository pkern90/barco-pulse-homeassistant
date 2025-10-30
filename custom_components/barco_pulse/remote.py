"""Barco Pulse remote platform."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.remote import RemoteEntity

from .const import ACTIVE_STATES, PowerState
from .entity import BarcoEntity, BarcoPowerMixin
from .helpers import handle_api_errors, parse_preset_command, safe_refresh

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoDataUpdateCoordinator
    from .data import BarcoRuntimeData

_LOGGER = logging.getLogger(__name__)


class BarcoRemote(BarcoPowerMixin, BarcoEntity, RemoteEntity):
    """Barco Pulse remote entity."""

    _attr_translation_key = "remote"

    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize the remote."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_remote"

    @property
    def is_on(self) -> bool:
        """Return True if the projector is on."""
        state = self.coordinator.data.get("state")
        try:
            return PowerState(state) in ACTIVE_STATES
        except (ValueError, TypeError):
            return False

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
            # Parse preset command (e.g., "preset_5" -> 5)
            preset_num = parse_preset_command(cmd)

            if preset_num is None:
                _LOGGER.warning("Invalid preset command: %s", cmd)
                return

            await self.coordinator.device.activate_preset(preset_num)

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
        commands_executed = 0
        for cmd in command:
            if not isinstance(cmd, str):
                _LOGGER.warning("Invalid command type: %s (expected str)", type(cmd))
                continue

            await self._execute_command(cmd)
            commands_executed += 1

        # Only refresh once after all commands are executed
        if commands_executed > 0:
            await safe_refresh(self.coordinator, f"{commands_executed} command(s)")


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
