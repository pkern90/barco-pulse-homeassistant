"""Constants for Barco Pulse integration."""

from __future__ import annotations

from datetime import timedelta

# Integration metadata
DOMAIN = "barco_pulse"
NAME = "Barco Pulse"
ATTRIBUTION = "Data provided by Barco Pulse Projector"

# Network configuration
DEFAULT_PORT = 9090
DEFAULT_TIMEOUT = 10

# Update intervals
INTERVAL_FAST = timedelta(seconds=10)
INTERVAL_SLOW = timedelta(seconds=60)

# Configuration keys
CONF_AUTH_CODE = "auth_code"

# Power states
POWER_STATES_ACTIVE = ["on", "ready"]
POWER_STATES_TRANSITIONAL = ["conditioning", "deconditioning"]
POWER_STATES_STANDBY = ["standby", "eco", "boot"]

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
