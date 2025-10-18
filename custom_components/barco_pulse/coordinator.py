"""DataUpdateCoordinator for barco_pulse."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    BarcoPulseApiClient,
    BarcoPulseApiError,
    BarcoPulseAuthenticationError,
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
            - source: active, available
            - illumination: laser_power

        """
        try:
            # Fetch all data from projector
            system_state = await self.client.get_system_state()
            system_info = await self.client.get_system_info()
            active_source = await self.client.get_active_source()
            available_sources = await self.client.list_sources()
            laser_power = await self.client.get_laser_power()

            # Determine if projector is "on" (operational states)
            # States: boot, eco, standby, ready, conditioning, on, deconditioning
            is_on = system_state in ("ready", "on", "conditioning")

            return {
                "system": {
                    "state": system_state,
                    "serial_number": system_info.get("serial_number", ""),
                    "model_name": system_info.get("model_name", ""),
                    "firmware_version": system_info.get("firmware_version", ""),
                },
                "power": {
                    "is_on": is_on,
                },
                "source": {
                    "active": active_source,
                    "available": available_sources,
                },
                "illumination": {
                    "laser_power": laser_power,
                },
            }
        except BarcoPulseAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except BarcoPulseApiError as exception:
            raise UpdateFailed(exception) from exception
