# Phase 3: Configuration Flow

## 3.1 Config Flow Implementation (`custom_components/barco_pulse/config_flow.py`)

### Imports and Setup
- [x] Import `ConfigFlow`, `ConfigEntry`, `OptionsFlow`
- [x] Import `voluptuous as vol`
- [x] Import constants from `const.py`
- [x] Import `BarcoDevice` from `api.py`
- [x] Import exceptions from `exceptions.py`
- [x] Import `CONF_HOST`, `CONF_PORT` from `homeassistant.const`

### Config Flow Class
- [x] Create `BarcoConfigFlow` extending `ConfigFlow, domain=DOMAIN`
- [x] Set `VERSION = 1`

### User Step Schema
- [x] Define schema with `vol.Required(CONF_HOST): str`
- [x] Add `vol.Optional(CONF_PORT, default=DEFAULT_PORT): int`
- [x] Add `vol.Optional(CONF_AUTH_CODE): int`

### User Step Implementation
- [x] Implement `async def async_step_user(user_input)` method
- [x] Initialize empty `errors` dict
- [x] If `user_input is None`, show form with schema
- [x] If `user_input` provided, create `BarcoDevice` instance
- [x] Try to connect to device
- [x] Get serial number using `get_serial_number()`
- [x] Set unique ID using `async_set_unique_id(serial)`
- [x] Abort if already configured using `_abort_if_unique_id_configured()`
- [x] Get model name using `get_model_name()`
- [x] Disconnect from device
- [x] Create entry with title `{model} ({host})`
- [x] Return `async_create_entry(title, data=user_input)`

### Error Handling in User Step
- [x] Catch `BarcoConnectionError` and set `errors["base"] = "cannot_connect"`
- [x] Catch `BarcoAuthError` and set `errors["base"] = "invalid_auth"`
- [x] Catch generic `Exception` and set `errors["base"] = "unknown"`
- [x] Show form again with errors if any exception occurs

### Reconfigure Step
- [x] Implement `async def async_step_reconfigure(user_input)` method
- [x] Get existing config entry data
- [x] Create schema with current values as defaults
- [x] Validate connection similar to user step
- [x] Update entry using `self.hass.config_entries.async_update_entry()`
- [x] Reload entry using `await self.hass.config_entries.async_reload(entry.entry_id)`
- [x] Return `async_abort(reason="reconfigure_successful")`

### Import Step (Optional)
- [x] Implement `async def async_step_import(user_input)` if YAML support needed
- [x] Call `async_step_user(user_input)` to handle import

### Form Display
- [x] Ensure all forms use `async_show_form()` with proper step_id
- [x] Include data_schema with voluptuous schema
- [x] Include errors dict
- [x] Add description_placeholders if needed
