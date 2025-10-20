# Phase 2: Data Update Coordinator

## 2.1 Coordinator Implementation (`custom_components/barco_pulse/coordinator.py`)

### Class Structure
- [ ] Import `DataUpdateCoordinator`, `UpdateFailed`, `ConfigEntryAuthFailed`
- [ ] Import constants from `const.py`
- [ ] Import `BarcoDevice` from `api.py`
- [ ] Import exceptions from `exceptions.py`
- [ ] Create `BarcoDataUpdateCoordinator` extending `DataUpdateCoordinator[dict[str, Any]]`

### Initialization
- [ ] Implement `__init__(hass, device)` calling super with initial slow interval
- [ ] Store `device: BarcoDevice` reference
- [ ] Initialize `_connection_lock: asyncio.Lock`
- [ ] Initialize `_update_lock: asyncio.Lock`
- [ ] Initialize `_last_update: float = 0.0`

### Rate Limiting
- [ ] Implement `async def _enforce_rate_limit()` with 1-second minimum interval
- [ ] Calculate elapsed time since last update
- [ ] Sleep if elapsed < 1.0 seconds
- [ ] Update `_last_update` timestamp

### Info Properties Fetching
- [ ] Implement `async def _get_info_properties()` returning dict
- [ ] Get `system.serialnumber`, `system.modelname`, `system.firmwareversion`
- [ ] Use batch `get_properties()` for efficiency
- [ ] Return property dict

### Active State Properties Fetching
- [ ] Implement `async def _get_active_properties()` returning dict
- [ ] Wrap all calls in try/except for `BarcoStateError`
- [ ] Get laser power using `get_laser_power()`
- [ ] Get laser limits using `get_laser_limits()`
- [ ] Get current source using `get_source()`
- [ ] Get available sources using `get_available_sources()`
- [ ] Get brightness using `get_brightness()`
- [ ] Get contrast using `get_contrast()`
- [ ] Get saturation using `get_saturation()`
- [ ] Get hue using `get_hue()`
- [ ] Return property dict (skip properties that raise `BarcoStateError`)

### Main Update Logic
- [ ] Implement `async def _async_update_data()` returning `dict[str, Any]`
- [ ] Acquire `_update_lock` for thread safety
- [ ] Call `_enforce_rate_limit()`
- [ ] Get system state using `device.get_state()`
- [ ] Initialize data dict with state
- [ ] Get info properties using `_get_info_properties()`
- [ ] Check if state in `POWER_STATES_ACTIVE`
- [ ] If active, get active properties and set update interval to `INTERVAL_FAST`
- [ ] If not active, set update interval to `INTERVAL_SLOW`
- [ ] Return complete data dict

### Error Handling
- [ ] Catch `BarcoConnectionError` and raise `UpdateFailed`
- [ ] Catch `BarcoAuthError` and raise `ConfigEntryAuthFailed`
- [ ] Catch `BarcoStateError` and return partial data (don't fail)
- [ ] Catch generic `Exception` and raise `UpdateFailed`

### Properties
- [ ] Add `@property def unique_id()` returning device serial number
- [ ] Add `@property def device()` returning `BarcoDevice` instance
