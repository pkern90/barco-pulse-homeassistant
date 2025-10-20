# Phase 4: Integration Setup

## 4.1 Integration Init (`custom_components/barco_pulse/__init__.py`)

### Imports
- [ ] Import `HomeAssistant`, `ConfigEntry`
- [ ] Import `ConfigEntryNotReady` from `homeassistant.exceptions`
- [ ] Import `EVENT_HOMEASSISTANT_STOP` from `homeassistant.const`
- [ ] Import constants from `const.py`
- [ ] Import `BarcoDevice` from `api.py`
- [ ] Import `BarcoDataUpdateCoordinator` from `coordinator.py`
- [ ] Import `BarcoRuntimeData` from `data.py`
- [ ] Import exceptions from `exceptions.py`

### Platform List
- [ ] Define `PLATFORMS` list with all platform names
- [ ] Include: `"binary_sensor"`, `"sensor"`, `"switch"`, `"select"`, `"number"`, `"remote"`

### Setup Entry Function
- [ ] Implement `async def async_setup_entry(hass, entry)` returning bool
- [ ] Extract host from `entry.data[CONF_HOST]`
- [ ] Extract port from `entry.data.get(CONF_PORT, DEFAULT_PORT)`
- [ ] Extract auth_code from `entry.data.get(CONF_AUTH_CODE)`
- [ ] Create `BarcoDevice` instance with connection parameters

### Device Connection
- [ ] Try to connect using `await device.connect()`
- [ ] Catch `BarcoConnectionError` and raise `ConfigEntryNotReady`
- [ ] Catch `BarcoAuthError` and raise `ConfigEntryNotReady`

### Coordinator Setup
- [ ] Create `BarcoDataUpdateCoordinator(hass, device)`
- [ ] Call `await coordinator.async_config_entry_first_refresh()`
- [ ] Handle failures appropriately

### Runtime Data Storage
- [ ] Create `BarcoRuntimeData(client=device, coordinator=coordinator)`
- [ ] Store in `entry.runtime_data`

### Shutdown Handler
- [ ] Define `async def _async_close_connection(event)` function
- [ ] Call `await device.disconnect()` in handler
- [ ] Register handler with `hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, ...)`
- [ ] Store unsubscribe callback using `entry.async_on_unload()`

### Platform Forwarding
- [ ] Call `await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)`
- [ ] Return `True`

### Unload Entry Function
- [ ] Implement `async def async_unload_entry(hass, entry)` returning bool
- [ ] Call `await hass.config_entries.async_unload_platforms(entry, PLATFORMS)`
- [ ] Store result in `unload_ok`
- [ ] If `unload_ok`, disconnect device: `await entry.runtime_data.client.disconnect()`
- [ ] Return `unload_ok`

### Reload Entry Function (Optional)
- [ ] Implement `async def async_reload_entry(hass, entry)` if needed
- [ ] Call `await async_unload_entry(hass, entry)`
- [ ] Call `await async_setup_entry(hass, entry)`
