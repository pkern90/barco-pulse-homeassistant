"""Data update coordinator for Barco Pulse integration."""

# ruff: noqa: TRY003, EM102, TRY300

from __future__ import annotations

import asyncio
import hashlib
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
    PRESET_ASSIGNMENT_TUPLE_SIZE,
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
        """Initialize the coordinator with fallback unique_id."""
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
        # Generate stable fallback ID immediately (never None)
        self._fallback_id = hashlib.md5(  # noqa: S324
            f"{device.host}:{device.port}".encode()
        ).hexdigest()[:16]

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

        # Build list of properties to fetch in batch
        property_names = [
            "illumination.sources.laser.power",
            "image.window.main.source",
            "image.brightness",
            "image.contrast",
            "image.saturation",
            "profile.presetassignments",
            "profile.profiles",
        ]

        try:
            # Fetch properties in a single batch request
            results = await self.device.get_properties(property_names)

            # Parse laser power
            if "illumination.sources.laser.power" in results:
                data["laser_power"] = float(results["illumination.sources.laser.power"])

            # Parse source
            if "image.window.main.source" in results:
                data["source"] = results["image.window.main.source"]

            # Parse picture settings
            if "image.brightness" in results:
                data["brightness"] = float(results["image.brightness"])
            if "image.contrast" in results:
                data["contrast"] = float(results["image.contrast"])
            if "image.saturation" in results:
                data["saturation"] = float(results["image.saturation"])

            # Parse preset assignments (returned as array of arrays)
            if "profile.presetassignments" in results:
                data.update(
                    self._parse_preset_assignments(results["profile.presetassignments"])
                )

            # Parse profiles
            if "profile.profiles" in results:
                profiles = results["profile.profiles"]
                if isinstance(profiles, list):
                    data["profiles"] = profiles

        except BarcoStateError:
            _LOGGER.debug("Some properties not available in current state")

        # Get available sources separately (uses different method)
        try:
            data["available_sources"] = await self.device.get_available_sources()
        except BarcoStateError:
            _LOGGER.debug("Available sources not available in current state")

        return data

    def _parse_preset_assignments(self, preset_data: Any) -> dict[str, Any]:
        """Parse preset assignments from API response."""
        result: dict[str, Any] = {}
        if not isinstance(preset_data, list):
            return result

        assignments = {}
        for item in preset_data:
            if isinstance(item, list) and len(item) >= PRESET_ASSIGNMENT_TUPLE_SIZE:
                preset_num, profile_name = item[0], item[1]
                if profile_name:  # Only include assigned presets
                    assignments[int(preset_num)] = profile_name

        result["preset_assignments"] = assignments
        result["available_presets"] = sorted(assignments.keys())
        return result

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
    def unique_id(self) -> str:
        """Return unique ID for this coordinator, never None."""
        if self.data and self.data.get("serial_number"):
            return self.data["serial_number"]
        return self._fallback_id
