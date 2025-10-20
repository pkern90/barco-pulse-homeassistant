"""Data update coordinator for Barco Pulse integration."""

# ruff: noqa: TRY003, EM102, TRY300

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    INTERVAL_FAST,
    INTERVAL_SLOW,
    NAME,
    POWER_STATES_ACTIVE,
)
from .exceptions import (
    BarcoAuthError,
    BarcoConnectionError,
    BarcoStateError,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .api import BarcoDevice

_LOGGER = logging.getLogger(__name__)


class BarcoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data update coordinator for Barco Pulse projector."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, device: BarcoDevice) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=NAME,
            update_interval=INTERVAL_SLOW,
        )
        self.device = device
        self._connection_lock = asyncio.Lock()
        self._update_lock = asyncio.Lock()
        self._last_update = 0.0

    async def _enforce_rate_limit(self) -> None:
        """Enforce minimum 1-second interval between updates."""
        elapsed = time.time() - self._last_update
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
        self._last_update = time.time()

    async def _get_info_properties(self) -> dict[str, Any]:
        """Get device info properties (always available)."""
        properties = [
            "system.serialnumber",
            "system.modelname",
            "system.firmwareversion",
        ]
        result = await self.device.get_properties(properties)
        return {
            "serial_number": result.get("system.serialnumber"),
            "model": result.get("system.modelname"),
            "firmware_version": result.get("system.firmwareversion"),
        }

    async def _get_active_properties(self) -> dict[str, Any]:
        """Get properties only available when projector is active (on/ready)."""
        data: dict[str, Any] = {}

        # Laser power
        try:
            data["laser_power"] = await self.device.get_laser_power()
        except BarcoStateError:
            _LOGGER.debug("Laser power not available in current state")

        # Laser limits
        try:
            min_power, max_power = await self.device.get_laser_limits()
            data["laser_power_min"] = min_power
            data["laser_power_max"] = max_power
        except BarcoStateError:
            _LOGGER.debug("Laser limits not available in current state")

        # Current source
        try:
            data["source"] = await self.device.get_source()
        except BarcoStateError:
            _LOGGER.debug("Source not available in current state")

        # Available sources
        try:
            data["available_sources"] = await self.device.get_available_sources()
        except BarcoStateError:
            _LOGGER.debug("Available sources not available in current state")

        # Brightness
        try:
            data["brightness"] = await self.device.get_brightness()
        except BarcoStateError:
            _LOGGER.debug("Brightness not available in current state")

        # Contrast
        try:
            data["contrast"] = await self.device.get_contrast()
        except BarcoStateError:
            _LOGGER.debug("Contrast not available in current state")

        # Saturation
        try:
            data["saturation"] = await self.device.get_saturation()
        except BarcoStateError:
            _LOGGER.debug("Saturation not available in current state")

        # Hue
        try:
            data["hue"] = await self.device.get_hue()
        except BarcoStateError:
            _LOGGER.debug("Hue not available in current state")

        # Preset assignments and profiles
        try:
            preset_assignments = await self.device.get_preset_assignments()
            data["preset_assignments"] = preset_assignments
            # Create list of available presets (only those with assigned profiles)
            data["available_presets"] = sorted(preset_assignments.keys())
        except BarcoStateError:
            _LOGGER.debug("Preset assignments not available in current state")

        try:
            profiles = await self.device.get_profiles()
            data["profiles"] = profiles
        except BarcoStateError:
            _LOGGER.debug("Profiles not available in current state")

        return data

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the projector."""
        async with self._update_lock:
            try:
                # Enforce rate limiting
                await self._enforce_rate_limit()

                # Get system state (always available)
                state = await self.device.get_state()
                data: dict[str, Any] = {"state": state}

                # Get device info properties (always available)
                info = await self._get_info_properties()
                data.update(info)

                # If projector is active, get additional properties
                if state in POWER_STATES_ACTIVE:
                    active_data = await self._get_active_properties()
                    data.update(active_data)
                    # Use fast polling when active
                    self.update_interval = INTERVAL_FAST
                else:
                    # Use slow polling when not active
                    self.update_interval = INTERVAL_SLOW

                _LOGGER.debug("Updated data: %s", data)
                return data

            except BarcoAuthError as err:
                raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
            except BarcoConnectionError as err:
                raise UpdateFailed(f"Connection error: {err}") from err
            except Exception as err:
                raise UpdateFailed(f"Unexpected error: {err}") from err

    @property
    def unique_id(self) -> str | None:
        """Return unique ID for this coordinator."""
        if self.data:
            return self.data.get("serial_number")
        return None
