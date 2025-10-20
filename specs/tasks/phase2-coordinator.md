# Phase 2: Data Update Coordinator

## 2.1 Coordinator Implementation (`custom_components/barco_pulse/coordinator.py`)

### Class Structure
- [x] Import `DataUpdateCoordinator`, `UpdateFailed`, `ConfigEntryAuthFailed`
- [x] Import constants from `const.py`
- [x] Import `BarcoDevice` from `api.py`
- [x] Import exceptions from `exceptions.py`
- [x] Create `BarcoDataUpdateCoordinator` extending `DataUpdateCoordinator[dict[str, Any]]`

### Initialization
- [x] Implement `__init__(hass, device)` calling super with initial slow interval
- [x] Store `device: BarcoDevice` reference
- [x] Initialize `_connection_lock: asyncio.Lock`
- [x] Initialize `_update_lock: asyncio.Lock`
- [x] Initialize `_last_update: float = 0.0`

### Rate Limiting
- [x] Implement `async def _enforce_rate_limit()` with 1-second minimum interval
- [x] Calculate elapsed time since last update
- [x] Sleep if elapsed < 1.0 seconds
- [x] Update `_last_update` timestamp

### Info Properties Fetching
- [x] Implement `async def _get_info_properties()` returning dict
- [x] Get `system.serialnumber`, `system.modelname`, `system.firmwareversion`
- [x] Use batch `get_properties()` for efficiency
- [x] Return property dict

### Active State Properties Fetching
- [x] Implement `async def _get_active_properties()` returning dict
- [x] Wrap all calls in try/except for `BarcoStateError`
- [x] Get laser power using `get_laser_power()`
- [x] Get laser limits using `get_laser_limits()`
- [x] Get current source using `get_source()`
- [x] Get available sources using `get_available_sources()`
- [x] Get brightness using `get_brightness()`
- [x] Get contrast using `get_contrast()`
- [x] Get saturation using `get_saturation()`
- [x] Get hue using `get_hue()`
- [x] Return property dict (skip properties that raise `BarcoStateError`)

### Main Update Logic
- [x] Implement `async def _async_update_data()` returning `dict[str, Any]`
- [x] Acquire `_update_lock` for thread safety
- [x] Call `_enforce_rate_limit()`
- [x] Get system state using `device.get_state()`
- [x] Initialize data dict with state
- [x] Get info properties using `_get_info_properties()`
- [x] Check if state in `POWER_STATES_ACTIVE`
- [x] If active, get active properties and set update interval to `INTERVAL_FAST`
- [x] If not active, set update interval to `INTERVAL_SLOW`
- [x] Return complete data dict

### Error Handling
- [x] Catch `BarcoConnectionError` and raise `UpdateFailed`
- [x] Catch `BarcoAuthError` and raise `ConfigEntryAuthFailed`
- [x] Catch `BarcoStateError` and return partial data (don't fail)
- [x] Catch generic `Exception` and raise `UpdateFailed`

### Properties
- [x] Add `@property def unique_id()` returning device serial number
- [x] Add `@property def device()` returning `BarcoDevice` instance
