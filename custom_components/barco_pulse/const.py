"""Constants for Barco Pulse integration."""

from __future__ import annotations

from datetime import timedelta
from enum import StrEnum

# Integration metadata
DOMAIN = "barco_pulse"
NAME = "Barco Pulse"
ATTRIBUTION = "Data provided by Barco Pulse Projector"
MANUFACTURER = "Barco"
MODEL_PREFIX = "Pulse"

# Network configuration
DEFAULT_PORT = 9090
DEFAULT_TIMEOUT = 10


class PowerState(StrEnum):
    """Power states for Barco Pulse projector."""

    ON = "on"
    READY = "ready"
    CONDITIONING = "conditioning"
    DECONDITIONING = "deconditioning"
    STANDBY = "standby"
    ECO = "eco"
    BOOT = "boot"


# State groups
ACTIVE_STATES: frozenset[PowerState] = frozenset(
    {
        PowerState.ON,
        PowerState.READY,
        PowerState.CONDITIONING,
        PowerState.DECONDITIONING,
    }
)

STANDBY_STATES: frozenset[PowerState] = frozenset(
    {
        PowerState.STANDBY,
        PowerState.ECO,
        PowerState.BOOT,
    }
)

# Polling intervals per state
POLLING_INTERVALS: dict[PowerState, timedelta] = {
    PowerState.ON: timedelta(seconds=2),
    PowerState.READY: timedelta(seconds=2),
    PowerState.CONDITIONING: timedelta(seconds=5),
    PowerState.DECONDITIONING: timedelta(seconds=5),
    PowerState.STANDBY: timedelta(seconds=30),
    PowerState.ECO: timedelta(seconds=30),
    PowerState.BOOT: timedelta(seconds=5),
}

DEFAULT_POLLING_INTERVAL = timedelta(seconds=10)

# Legacy constants (deprecated, use ACTIVE_STATES instead)
INTERVAL_FAST = timedelta(seconds=10)
INTERVAL_SLOW = timedelta(seconds=60)
POWER_STATES_ACTIVE = ["on", "ready"]
POWER_STATES_TRANSITIONAL = ["conditioning", "deconditioning"]
POWER_STATES_STANDBY = ["standby", "eco", "boot"]

# Configuration keys
CONF_AUTH_CODE = "auth_code"

# API constants
PRESET_ASSIGNMENT_TUPLE_SIZE = 2  # [preset_num, profile_name]
PRESET_MAX_NUMBER = 29  # Presets range from 0 to 29 (30 total)

# Entity attribute keys
ATTR_LASER_POWER = "laser_power"
ATTR_SOURCE = "source"
ATTR_STATE = "state"
ATTR_MODEL = "model"
ATTR_SERIAL_NUMBER = "serial_number"
ATTR_FIRMWARE_VERSION = "firmware_version"
ATTR_BRIGHTNESS = "brightness"
ATTR_CONTRAST = "contrast"
ATTR_SATURATION = "saturation"
ATTR_HUE = "hue"
