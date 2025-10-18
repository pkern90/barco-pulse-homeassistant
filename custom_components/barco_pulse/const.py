"""Constants for barco_pulse."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "barco_pulse"
ATTRIBUTION = "Data provided by Barco Pulse projector"

# Configuration constants
CONF_HOST = "host"
CONF_PORT = "port"
CONF_AUTH_CODE = "auth_code"

# Default values
DEFAULT_PORT = 9090
DEFAULT_TIMEOUT = 10.0
