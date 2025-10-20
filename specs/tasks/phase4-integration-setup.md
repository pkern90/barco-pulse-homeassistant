# Phase 4: Integration Setup

## 4.1 Integration Init (`custom_components/barco_pulse/__init__.py`)

### Imports
- [x] Import `HomeAssistant`, `ConfigEntry`
- [x] Import `ConfigEntryNotReady` from `homeassistant.exceptions`
- [x] Import `EVENT_HOMEASSISTANT_STOP` from `homeassistant.const`
- [x] Import constants from `const.py`
- [x] Import `BarcoDevice` from `api.py`
- [x] Import `BarcoDataUpdateCoordinator` from `coordinator.py`
- [x] Import `BarcoRuntimeData` from `data.py`
- [x] Import exceptions from `exceptions.py`

### Platform List
- [x] Define `PLATFORMS` list with all platform names
- [x] Include: `"binary_sensor"`, `"sensor"`, `"switch"`, `"select"`, `"number"`, `"remote"`

### Setup Entry Function
- [x] Implement `async def async_setup_entry(hass, entry)` returning bool
- [x] Extract host from `entry.data[CONF_HOST]`
- [x] Extract port from `entry.data.get(CONF_PORT, DEFAULT_PORT)`
- [x] Extract auth_code from `entry.data.get(CONF_AUTH_CODE)`
- [x] Create `BarcoDevice` instance with connection parameters

### Device Connection
- [x] Try to connect using `await device.connect()`
- [x] Catch `BarcoConnectionError` and raise `ConfigEntryNotReady`
- [x] Catch `BarcoAuthError` and raise `ConfigEntryNotReady`

### Coordinator Setup
- [x] Create `BarcoDataUpdateCoordinator(hass, device)`
- [x] Call `await coordinator.async_config_entry_first_refresh()`
- [x] Handle failures appropriately

### Runtime Data Storage
- [x] Create `BarcoRuntimeData(client=device, coordinator=coordinator)`
- [x] Store in `entry.runtime_data`

### Shutdown Handler
- [x] Define `async def _async_close_connection(event)` function
- [x] Call `await device.disconnect()` in handler
- [x] Register handler with `hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, ...)`
- [x] Store unsubscribe callback using `entry.async_on_unload()`

### Platform Forwarding
- [x] Call `await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)`
- [x] Return `True`

### Unload Entry Function
- [x] Implement `async def async_unload_entry(hass, entry)` returning bool
- [x] Call `await hass.config_entries.async_unload_platforms(entry, PLATFORMS)`
- [x] Store result in `unload_ok`
- [x] If `unload_ok`, disconnect device: `await entry.runtime_data.client.disconnect()`
- [x] Return `unload_ok`

### Reload Entry Function (Optional)
- [x] Implement `async def async_reload_entry(hass, entry)` if needed
- [x] Call `await async_unload_entry(hass, entry)`
- [x] Call `await async_setup_entry(hass, entry)`
