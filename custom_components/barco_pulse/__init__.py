"""The Barco Pulse integration."""

# ruff: noqa: TRY003, EM102

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT, EVENT_HOMEASSISTANT_STOP
from homeassistant.exceptions import ConfigEntryNotReady

from .api import BarcoDevice
from .const import CONF_AUTH_CODE, DEFAULT_PORT, DEFAULT_TIMEOUT
from .coordinator import BarcoDataUpdateCoordinator
from .data import BarcoRuntimeData
from .exceptions import BarcoAuthError, BarcoConnectionError

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Platforms to set up
PLATFORMS = ["binary_sensor", "sensor", "switch", "select", "number", "remote"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Barco Pulse from a config entry."""
    # Extract configuration
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    # Convert empty string to None for auth_code
    auth_code = entry.data.get(CONF_AUTH_CODE) or None

    # Create device instance
    device = BarcoDevice(
        host=host,
        port=port,
        auth_code=auth_code,
        timeout=DEFAULT_TIMEOUT,
    )

    # Try to connect
    try:
        await device.connect()
    except BarcoConnectionError as err:
        raise ConfigEntryNotReady(f"Failed to connect to {host}:{port}") from err
    except BarcoAuthError as err:
        raise ConfigEntryNotReady(f"Authentication failed for {host}:{port}") from err

    # Create coordinator
    coordinator = BarcoDataUpdateCoordinator(hass, device)

    # Perform initial refresh
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        await device.disconnect()
        raise ConfigEntryNotReady(f"Failed to fetch initial data: {err}") from err

    # Store runtime data
    entry.runtime_data = BarcoRuntimeData(client=device, coordinator=coordinator)

    # Register shutdown handler
    async def _async_close_connection(_event: Event) -> None:
        """Close connection on shutdown."""
        await device.disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_close_connection)
    )

    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Disconnect device if unload successful
    if unload_ok:
        try:
            await entry.runtime_data.client.disconnect()
        except (BarcoConnectionError, OSError) as err:
            _LOGGER.debug("Error disconnecting during unload: %s", err)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
