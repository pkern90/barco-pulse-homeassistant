"""Adds config flow for Barco Pulse."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers import selector

from .api import (
    BarcoPulseApiClient,
    BarcoPulseApiError,
    BarcoPulseAuthenticationError,
    BarcoPulseConnectionError,
)
from .const import CONF_AUTH_CODE, CONF_PORT, DEFAULT_PORT, DOMAIN, LOGGER


class BarcoPulseFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Barco Pulse."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                # Get system info to validate connection and get serial number
                info = await self._test_connection(
                    host=user_input[CONF_HOST],
                    port=user_input.get(CONF_PORT, DEFAULT_PORT),
                    auth_code=user_input.get(CONF_AUTH_CODE),
                )
            except BarcoPulseAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except BarcoPulseConnectionError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except BarcoPulseApiError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                # Use serial number as unique ID
                serial_number = info.get("serial_number", "")
                if serial_number:
                    await self.async_set_unique_id(serial_number)
                    self._abort_if_unique_id_configured()

                # Use model name + serial for title
                title = f"{info.get('model_name', 'Barco Pulse')} ({serial_number})"
                return self.async_create_entry(
                    title=title,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_PORT,
                        default=(user_input or {}).get(CONF_PORT, DEFAULT_PORT),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        CONF_AUTH_CODE,
                        default=(user_input or {}).get(CONF_AUTH_CODE, vol.UNDEFINED),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=10000,
                            max=99999,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_connection(
        self, host: str, port: int, auth_code: int | None
    ) -> dict:
        """Validate connection and return system info."""
        client = BarcoPulseApiClient(
            host=host,
            port=port,
            auth_code=auth_code,
        )
        try:
            await client.connect()
            return await client.get_system_info()
        finally:
            await client.disconnect()
