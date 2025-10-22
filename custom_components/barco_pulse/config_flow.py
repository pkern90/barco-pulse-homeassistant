"""Config flow for Barco Pulse integration."""

from __future__ import annotations

import contextlib
import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT

from .api import BarcoDevice
from .const import CONF_AUTH_CODE, DEFAULT_PORT, DEFAULT_TIMEOUT, DOMAIN
from .exceptions import BarcoAuthError, BarcoConnectionError

_LOGGER = logging.getLogger(__name__)


class BarcoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Barco Pulse."""

    VERSION = 1

    def _get_user_schema(self, defaults: dict[str, Any] | None = None) -> vol.Schema:
        """Get user configuration schema."""
        if defaults is None:
            defaults = {}

        return vol.Schema(
            {
                vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): str,
                vol.Optional(
                    CONF_PORT, default=defaults.get(CONF_PORT, DEFAULT_PORT)
                ): int,
                vol.Optional(
                    CONF_AUTH_CODE, default=defaults.get(CONF_AUTH_CODE, "")
                ): str,
            }
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Extract configuration
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            auth_code = user_input.get(CONF_AUTH_CODE)

            # Create device instance
            device = BarcoDevice(
                host=host,
                port=port,
                auth_code=auth_code,
                timeout=DEFAULT_TIMEOUT,
            )

            try:
                # Try to connect and get device info
                await device.connect()
                serial_number = await device.get_serial_number()
                model_name = await device.get_model_name()

                # Set unique ID based on serial number
                await self.async_set_unique_id(serial_number)
                self._abort_if_unique_id_configured()

                # Create entry with model and host as title
                title = f"{model_name} ({host})"
                return self.async_create_entry(title=title, data=user_input)

            except BarcoConnectionError:
                errors["base"] = "cannot_connect"
            except BarcoAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            finally:
                with contextlib.suppress(BarcoConnectionError, OSError):
                    await device.disconnect()

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_user_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        errors: dict[str, str] = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        if entry is None:
            return self.async_abort(reason="reconfigure_failed")

        if user_input is not None:
            # Extract configuration
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            auth_code = user_input.get(CONF_AUTH_CODE)

            # Create device instance
            device = BarcoDevice(
                host=host,
                port=port,
                auth_code=auth_code,
                timeout=DEFAULT_TIMEOUT,
            )

            try:
                # Validate connection
                await device.connect()
                await device.get_state()

                # Update entry
                self.hass.config_entries.async_update_entry(entry, data=user_input)

                # Reload entry
                await self.hass.config_entries.async_reload(entry.entry_id)

                return self.async_abort(reason="reconfigure_successful")

            except BarcoConnectionError:
                errors["base"] = "cannot_connect"
            except BarcoAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception during reconfigure")
                errors["base"] = "unknown"
            finally:
                with contextlib.suppress(BarcoConnectionError, OSError):
                    await device.disconnect()

        # Use existing entry data as defaults if no user input yet
        defaults = entry.data if user_input is None else user_input

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self._get_user_schema(defaults),
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        """Handle import from YAML configuration."""
        return await self.async_step_user(user_input)
