# Phase 3: Configuration Flow

## 3.1 Config Flow Implementation (`custom_components/barco_pulse/config_flow.py`)

### Imports and Setup
- [ ] Import `ConfigFlow`, `ConfigEntry`, `OptionsFlow`
- [ ] Import `voluptuous as vol`
- [ ] Import constants from `const.py`
- [ ] Import `BarcoDevice` from `api.py`
- [ ] Import exceptions from `exceptions.py`
- [ ] Import `CONF_HOST`, `CONF_PORT` from `homeassistant.const`

### Config Flow Class
- [ ] Create `BarcoConfigFlow` extending `ConfigFlow, domain=DOMAIN`
- [ ] Set `VERSION = 1`

### User Step Schema
- [ ] Define schema with `vol.Required(CONF_HOST): str`
- [ ] Add `vol.Optional(CONF_PORT, default=DEFAULT_PORT): int`
- [ ] Add `vol.Optional(CONF_AUTH_CODE): int`

### User Step Implementation
- [ ] Implement `async def async_step_user(user_input)` method
- [ ] Initialize empty `errors` dict
- [ ] If `user_input is None`, show form with schema
- [ ] If `user_input` provided, create `BarcoDevice` instance
- [ ] Try to connect to device
- [ ] Get serial number using `get_serial_number()`
- [ ] Set unique ID using `async_set_unique_id(serial)`
- [ ] Abort if already configured using `_abort_if_unique_id_configured()`
- [ ] Get model name using `get_model_name()`
- [ ] Disconnect from device
- [ ] Create entry with title `{model} ({host})`
- [ ] Return `async_create_entry(title, data=user_input)`

### Error Handling in User Step
- [ ] Catch `BarcoConnectionError` and set `errors["base"] = "cannot_connect"`
- [ ] Catch `BarcoAuthError` and set `errors["base"] = "invalid_auth"`
- [ ] Catch generic `Exception` and set `errors["base"] = "unknown"`
- [ ] Show form again with errors if any exception occurs

### Reconfigure Step
- [ ] Implement `async def async_step_reconfigure(user_input)` method
- [ ] Get existing config entry data
- [ ] Create schema with current values as defaults
- [ ] Validate connection similar to user step
- [ ] Update entry using `self.hass.config_entries.async_update_entry()`
- [ ] Reload entry using `await self.hass.config_entries.async_reload(entry.entry_id)`
- [ ] Return `async_abort(reason="reconfigure_successful")`

### Import Step (Optional)
- [ ] Implement `async def async_step_import(user_input)` if YAML support needed
- [ ] Call `async_step_user(user_input)` to handle import

### Form Display
- [ ] Ensure all forms use `async_show_form()` with proper step_id
- [ ] Include data_schema with voluptuous schema
- [ ] Include errors dict
- [ ] Add description_placeholders if needed
