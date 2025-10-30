"""Data update coordinator for Barco Pulse integration."""

# ruff: noqa: TRY003, EM102

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CLOSE_CONNECTION_AFTER_UPDATE,
    DEFAULT_POLLING_INTERVAL,
    NAME,
    POLLING_INTERVALS,
    POWER_STATES_ACTIVE,
    PRESET_ASSIGNMENT_TUPLE_SIZE,
    PowerState,
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
            update_interval=DEFAULT_POLLING_INTERVAL,
        )
        self.device = device
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

    def _parse_float_properties(
        self, results: dict[str, Any], data: dict[str, Any]
    ) -> None:
        """Parse float properties from results into data dict."""
        property_mappings = [
            ("laser_power", "illumination.sources.laser.power"),
            ("brightness", "image.brightness"),
            ("contrast", "image.contrast"),
            ("saturation", "image.saturation"),
        ]

        for key, result_key in property_mappings:
            if result_key in results:
                value = results[result_key]
                try:
                    data[key] = float(value) if value is not None else None
                except (ValueError, TypeError) as err:
                    _LOGGER.warning("Invalid %s value: %s (%s)", key, value, err)
                    data[key] = None

    def _parse_laser_constraints(
        self, results: dict[str, Any], data: dict[str, Any]
    ) -> None:
        """Parse laser power constraints from results into data dict."""
        laser_min = results.get("illumination.sources.laser.power.min")
        laser_max = results.get("illumination.sources.laser.power.max")

        if laser_min is not None and laser_max is not None:
            try:
                data["laser_min"] = float(laser_min)
                data["laser_max"] = float(laser_max)
                _LOGGER.debug("Laser constraints: min=%s, max=%s", laser_min, laser_max)
            except (ValueError, TypeError) as err:
                _LOGGER.warning("Invalid laser constraints: %s", err)
                data["laser_min"] = 0.0
                data["laser_max"] = 100.0
        else:
            # Use defaults if not available
            data["laser_min"] = 0.0
            data["laser_max"] = 100.0
            _LOGGER.debug("Using default laser constraints (not in response)")

    async def _get_active_properties(self) -> dict[str, Any]:
        """Get properties only available when projector is active (on/ready)."""
        data: dict[str, Any] = {}

        # Build list of properties to fetch in batch - include laser constraints
        property_names = [
            "illumination.sources.laser.power",
            "illumination.sources.laser.power.min",
            "illumination.sources.laser.power.max",
            "image.window.main.source",
            "image.brightness",
            "image.contrast",
            "image.saturation",
            "profile.presetassignments",
            "profile.profiles",
        ]

        try:
            # Fetch all properties in a single batch request
            results = await self.device.get_properties(property_names)

            # Validate response type
            if not isinstance(results, dict):
                _LOGGER.warning("Invalid properties response type: %s", type(results))
                return data

            # Parse float values
            self._parse_float_properties(results, data)

            # Parse source
            if "image.window.main.source" in results:
                data["source"] = results["image.window.main.source"]

            # Parse laser constraints
            self._parse_laser_constraints(results, data)

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
            # Set default laser constraints if state error
            data["laser_min"] = 0.0
            data["laser_max"] = 100.0

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
                # Wrap entire update in timeout to prevent indefinite hangs
                # This protects against slow network or device issues
                return await asyncio.wait_for(
                    self._fetch_data(),
                    timeout=30.0,  # Max 30s for entire update cycle
                )
            except TimeoutError as err:
                _LOGGER.warning(
                    "Update timeout for %s:%s - operation took >30s",
                    self.device.host,
                    self.device.port,
                )
                # Clean up connection on timeout
                try:
                    await self.device.disconnect()
                except (BarcoConnectionError, OSError):
                    _LOGGER.debug("Error during connection cleanup", exc_info=True)
                msg = "Update operation timed out"
                raise UpdateFailed(msg) from err
            except BarcoAuthError as err:
                _LOGGER.exception(
                    "Authentication failed for %s:%s - check auth code",
                    self.device.host,
                    self.device.port,
                )
                raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
            except BarcoConnectionError as err:
                _LOGGER.warning(
                    "Connection error to %s:%s: %s",
                    self.device.host,
                    self.device.port,
                    err,
                )
                # Clean up connection on failure
                try:
                    await self.device.disconnect()
                except (BarcoConnectionError, OSError):
                    _LOGGER.debug("Error during connection cleanup", exc_info=True)
                raise UpdateFailed(f"Connection error: {err}") from err
            except Exception as err:
                _LOGGER.exception(
                    "Unexpected error updating %s:%s",
                    self.device.host,
                    self.device.port,
                )
                # Clean up connection on unexpected error
                try:
                    await self.device.disconnect()
                except (BarcoConnectionError, OSError):
                    _LOGGER.debug("Error during connection cleanup", exc_info=True)
                raise UpdateFailed(f"Unexpected error: {err}") from err

    async def _fetch_data(self) -> dict[str, Any]:
        """Fetch data from projector (internal method wrapped by timeout)."""
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

        # Update polling interval based on current state
        try:
            power_state = PowerState(state)
            new_interval = POLLING_INTERVALS.get(power_state, DEFAULT_POLLING_INTERVAL)
        except ValueError:
            # Invalid state string, use default
            new_interval = DEFAULT_POLLING_INTERVAL

        if self.update_interval != new_interval:
            self.update_interval = new_interval
            _LOGGER.debug(
                "Updated polling interval to %s for state %s",
                new_interval,
                state,
            )

        _LOGGER.debug("Updated data: %s", data)

        # Close connection after successful update to prevent leaks
        # Connection will be re-established on next update
        if CLOSE_CONNECTION_AFTER_UPDATE:
            try:
                await self.device.disconnect()
                _LOGGER.debug("Closed connection after update")
            except (BarcoConnectionError, OSError) as err:
                _LOGGER.debug("Error closing connection: %s", err)

        return data

    @property
    def unique_id(self) -> str:
        """
        Return unique ID for this coordinator.

        Prefers serial number from device, falls back to deterministic hash
        of host:port if serial number is unavailable.

        Returns:
            Stable unique identifier that never changes for the same device.

        """
        if self.data and self.data.get("serial_number"):
            return self.data["serial_number"]

        _LOGGER.debug(
            "Using fallback unique_id for %s:%s",
            self.device.host,
            self.device.port,
        )
        return self._fallback_id
