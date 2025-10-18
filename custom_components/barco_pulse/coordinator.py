"""DataUpdateCoordinator for barco_pulse."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    BarcoPulseApiClient,
    BarcoPulseApiError,
    BarcoPulseAuthenticationError,
    BarcoPulseCommandError,
)

if TYPE_CHECKING:
    from datetime import timedelta
    from logging import Logger

    from homeassistant.core import HomeAssistant

    from .data import BarcoPulseConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class BarcoPulseDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: BarcoPulseConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        name: str,
        update_interval: timedelta,
        client: BarcoPulseApiClient,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(hass, logger, name=name, update_interval=update_interval)
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Update data via library.

        Returns:
            Dictionary with projector state organized by categories:
            - system: state, serial_number, model_name, firmware_version
            - power: is_on (derived from state)
            - source: active, available (None when projector is off)
            - illumination: laser_power (None when projector is off)

        Note: Some properties are only available when the projector is powered on.
        These will return None when the projector is in standby or other off states.

        """
        try:
            # Always fetch system state and info (available in all states)
            system_state = await self.client.get_system_state()
            system_info = await self.client.get_system_info()

            # Determine if projector is "on" (operational states)
            # States: boot, eco, standby, ready, conditioning, on, deconditioning
            is_on = system_state in ("ready", "on", "conditioning")

            data: dict[str, Any] = {
                "system": {
                    "state": system_state,
                    "serial_number": system_info.get("serial_number", ""),
                    "model_name": system_info.get("model_name", ""),
                    "firmware_version": system_info.get("firmware_version", ""),
                },
                "power": {
                    "is_on": is_on,
                },
            }

            # Only fetch state-dependent properties when projector is on
            # These properties may not be available when projector is in standby
            if is_on:
                # Try to get laser power (only available when on)
                try:
                    laser_power = await self.client.get_laser_power()
                    data["illumination"] = {"laser_power": laser_power}
                except BarcoPulseCommandError:
                    # Property not available even when on (model-specific)
                    self.logger.debug(
                        "Laser power not available even when projector is on"
                    )
                    data["illumination"] = {"laser_power": None}

                # Try to get active source and available sources
                try:
                    active_source = await self.client.get_active_source()
                    available_sources = await self.client.list_sources()
                    data["source"] = {
                        "active": active_source,
                        "available": available_sources,
                    }
                except BarcoPulseCommandError:
                    # Property not available even when on (model-specific)
                    self.logger.debug(
                        "Source information not available even when projector is on"
                    )
                    data["source"] = {"active": None, "available": []}
            else:
                # Projector is off - state-dependent properties are unavailable
                data["illumination"] = {"laser_power": None}
                data["source"] = {"active": None, "available": []}

        except BarcoPulseAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except BarcoPulseApiError as exception:
            raise UpdateFailed(exception) from exception

        return data
