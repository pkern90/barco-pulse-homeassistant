# Implementation Plan v0.0.2

## Overview

**Purpose**: Fix critical stability and robustness issues in v0.0.1 baseline.

**Status**: 12 tasks total
- 6 CRITICAL (release blockers)
- 3 HIGH (stability issues)
- 2 MEDIUM (improvements)
- 1 LOW (nice-to-have)

**v0.0.1 Baseline**: Working integration with coordinator, config flow, 7 platform types (17+ entities), preset/profile management, picture controls.

## Task Priority Matrix

| Priority | Count | Tasks               | Must Fix Before Release |
| -------- | ----- | ------------------- | ----------------------- |
| CRITICAL | 6     | 7, 8, 9, 10, 11, 12 | YES                     |
| HIGH     | 3     | 4, 5                | Recommended             |
| MEDIUM   | 2     | 1, 2                | Optional                |
| LOW      | 1     | 3                   | Optional                |

## Tasks

### Task 1: Constants Refactor (MEDIUM)

**File**: `const.py`

**Issue**: Power states use string literals instead of type-safe enums.

**Changes**:
1. Create `PowerState(StrEnum)` with: `ON`, `READY`, `CONDITIONING`, `DECONDITIONING`, `STANDBY`, `ECO`, `BOOT`
2. Convert state groups to `frozenset[PowerState]`
3. Add `POLLING_INTERVALS: dict[PowerState, timedelta]` mapping
4. Add `MANUFACTURER = "Barco"`, `MODEL_PREFIX = "Pulse"`
5. Update all string comparisons to use enum

### Task 2: Dynamic Laser Power Constraints (MEDIUM)

**Files**: `api.py`, `coordinator.py`

**Issue**: `number.py` expects `laser_min`/`laser_max` in coordinator data but they're not fetched.

**Changes**:

In `api.py`, add:
```python
async def get_laser_constraints(self) -> dict[str, float]:
    """Get laser power min/max constraints."""
    properties = ["illumination.sources.laser.power.min", "illumination.sources.laser.power.max"]
    result = await self.get_properties(properties)
    return {
        "min": float(result.get("illumination.sources.laser.power.min", 0.0)),
        "max": float(result.get("illumination.sources.laser.power.max", 100.0)),
    }
```

In `coordinator.py` `_get_active_properties()`, add:
```python
try:
    constraints = await self.device.get_laser_constraints()
    data["laser_min"] = constraints["min"]
    data["laser_max"] = constraints["max"]
except BarcoStateError:
    data["laser_min"] = 0.0
    data["laser_max"] = 100.0
```

### Task 3: Unique ID Fallback (LOW)

**File**: `coordinator.py`

**Issue**: Ensure unique_id never returns None if serial number unavailable.

**Changes**:

Add fallback in `coordinator.py`:
```python
@property
def unique_id(self) -> str:
    """Return unique ID for this coordinator."""
    if self.data and self.data.get("serial_number"):
        return self.data["serial_number"]
    # Fallback to stable hash
    import hashlib
    return hashlib.md5(f"{self.device.host}:{self.device.port}".encode()).hexdigest()[:16]
```

### Task 4: Connection Lifecycle & Error Handling (HIGH)

**Files**: `api.py`, `coordinator.py`, `config_flow.py`

**Issues**:
1. `_connected` flag inconsistent with actual connection state
2. No stale connection detection
3. Coordinator doesn't reset connection on errors
4. Config flow creates temporary devices without cleanup guarantee
5. No timeout on individual property fetches

**Changes**:

In `api.py`:
```python
async def _ensure_connected(self) -> None:
    """Ensure connection is active, reconnect if needed."""
    if self._connected and self._reader and self._writer:
        if self._writer.is_closing():
            _LOGGER.warning("Connection closed, reconnecting...")
            self._connected = False
            self._reader = None
            self._writer = None
    if not self._connected:
        await self.connect()

async def _send_request(self, method: str, params: Any = None) -> Any:
    """Send JSON-RPC request with connection validation."""
    async with self._lock:
        await self._ensure_connected()
        # ... existing code ...
        except (ConnectionError, OSError) as err:
            self._connected = False
            self._reader = None
            self._writer = None
            if self._writer:
                try:
                    self._writer.close()
                    await self._writer.wait_closed()
                except Exception:
                    pass
            raise BarcoConnectionError(f"Failed to send request: {err}") from err
```

In `coordinator.py`:
```python
async def _async_update_data(self) -> dict[str, Any]:
    """Fetch data with connection error recovery."""
    async with self._update_lock:
        try:
            # ... existing code ...
        except BarcoAuthError as err:
            raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
        except BarcoConnectionError as err:
            try:
                await self.device.disconnect()
            except Exception:
                pass
            raise UpdateFailed(f"Connection error: {err}") from err
        except Exception as err:
            try:
                await self.device.disconnect()
            except Exception:
                pass
            raise UpdateFailed(f"Unexpected error: {err}") from err
```

In `config_flow.py`, wrap device operations in try/finally:
```python
device = BarcoDevice(...)
try:
    await device.connect()
    serial_number = await device.get_serial_number()
    # ... validation ...
except BarcoConnectionError:
    errors["base"] = "cannot_connect"
except BarcoAuthError:
    errors["base"] = "invalid_auth"
finally:
    try:
        await device.disconnect()
    except Exception:
        pass
```

### Task 5: Data Validation & Type Safety (HIGH)

**Files**: `coordinator.py`, `api.py`

**Issues**:
1. No validation on API responses (could be None or wrong type)
2. Unsafe `float()` conversions can raise ValueError
3. Missing null checks before type conversions

**Changes**:

In `coordinator.py` `_get_active_properties()`:
```python
async def _get_active_properties(self) -> dict[str, Any]:
    """Get properties with validation."""
    data: dict[str, Any] = {}

    try:
        results = await self.device.get_properties(property_names)

        if not isinstance(results, dict):
            _LOGGER.warning("Invalid properties response type: %s", type(results))
            return data

        # Parse with validation
        for key, result_key in [
            ("laser_power", "illumination.sources.laser.power"),
            ("brightness", "image.brightness"),
            ("contrast", "image.contrast"),
            ("saturation", "image.saturation"),
            ("hue", "image.hue"),
        ]:
            if result_key in results:
                value = results[result_key]
                try:
                    data[key] = float(value) if value is not None else None
                except (ValueError, TypeError) as err:
                    _LOGGER.warning("Invalid %s value: %s (%s)", key, value, err)

        # Similar validation for all fields
        # ...
```

### Task 6: Rate Limiting Enhancement (MEDIUM)

**Files**: `api.py`

**Issue**: Rate limit only enforced between coordinator updates. Entity commands can flood API.

**Changes**:

In `api.py`:
```python
def __init__(self, host: str, port: int = 9090, auth_code: str | None = None, timeout: int = 10) -> None:
    """Initialize with rate limiting."""
    # ... existing code ...
    self._last_request_time = 0.0
    self._min_request_interval = 0.1  # 100ms minimum between any requests

async def _send_request(self, method: str, params: Any = None) -> Any:
    """Send request with rate limiting."""
    async with self._lock:
        # Enforce minimum interval between all requests
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

        # ... rest of existing code ...
```

### Task 7: Entity Command Error Handling (CRITICAL)

**Files**: `switch.py`, `number.py`, `select.py`, `remote.py`

**Issue**: All 12 entity command methods lack exception handling. Unhandled exceptions propagate to HA core.

**Affected Methods**:
- `switch.py`: `async_turn_on`, `async_turn_off`
- `number.py`: `async_set_native_value` (×5 entities)
- `select.py`: `async_select_option` (×3 entities)
- `remote.py`: `async_turn_on`, `async_turn_off`, `async_send_command`

**Changes**:

Apply this pattern to all entity command methods:
```python
from homeassistant.exceptions import HomeAssistantError

async def async_<command>(self, ...) -> None:
    """Execute command with error handling."""
    try:
        await self.coordinator.device.<api_method>(...)
        await self.coordinator.async_request_refresh()
    except BarcoStateError as err:
        _LOGGER.warning("Command failed - projector not ready: %s", err)
        raise HomeAssistantError(f"Projector not ready: {err}") from err
    except BarcoConnectionError as err:
        _LOGGER.error("Connection error during command: %s", err)
        raise HomeAssistantError(f"Connection error: {err}") from err
    except Exception as err:
        _LOGGER.exception("Unexpected error during command")
        raise HomeAssistantError(f"Command failed: {err}") from err
```

### Task 8: Coordinator unique_id Race Condition (CRITICAL)

**File**: `coordinator.py`

**Issue**: `unique_id` property returns None before first successful refresh, causing entity unique_ids to be "None_suffix".

**Changes**:

```python
def __init__(self, hass: HomeAssistant, device: BarcoDevice) -> None:
    """Initialize with fallback unique_id."""
    super().__init__(...)
    self.device = device
    self._connection_lock = asyncio.Lock()
    self._update_lock = asyncio.Lock()
    self._last_update = 0.0
    # Generate stable fallback ID immediately
    import hashlib
    self._fallback_id = hashlib.md5(
        f"{device.host}:{device.port}".encode()
    ).hexdigest()[:16]

@property
def unique_id(self) -> str:
    """Return unique ID, never None."""
    if self.data and self.data.get("serial_number"):
        return self.data["serial_number"]
    return self._fallback_id
```

### Task 9: Connection Cleanup on Auth Failure (CRITICAL)

**File**: `api.py`

**Issue**: If authentication fails, connection is left open causing resource leak.

**Changes**:

```python
async def connect(self) -> None:
    """Establish TCP connection with auth cleanup."""
    try:
        _LOGGER.debug("Connecting to %s:%s", self.host, self.port)
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port),
            timeout=self.timeout,
        )
        self._connected = True
        _LOGGER.debug("Connected to %s:%s", self.host, self.port)

        # Authenticate if auth code provided
        if self.auth_code:
            try:
                await self.authenticate(self.auth_code)
            except BarcoAuthError:
                # Auth failed - clean up connection
                await self.disconnect()
                raise

    except TimeoutError as err:
        msg = f"Connection timeout to {self.host}:{self.port}"
        raise BarcoConnectionError(msg) from err
    except (ConnectionError, OSError) as err:
        msg = f"Failed to connect to {self.host}:{self.port}: {err}"
        raise BarcoConnectionError(msg) from err
```

### Task 10: Entity Input Validation (CRITICAL)

**Files**: `number.py`, `select.py`, `remote.py`

**Issue**: User input passed directly to API without validation.

**Changes**:

In `number.py` for all number entities:
```python
async def async_set_native_value(self, value: float) -> None:
    """Set value with bounds checking."""
    if value < self.native_min_value or value > self.native_max_value:
        raise ValueError(
            f"Value {value} out of range [{self.native_min_value}, {self.native_max_value}]"
        )

    try:
        await self.coordinator.device.set_<property>(value)
        await self.coordinator.async_request_refresh()
    except ... # (Task 7 error handling)
```

In `select.py` for all select entities:
```python
async def async_select_option(self, option: str) -> None:
    """Select option with validation."""
    if option not in self.options:
        raise ValueError(f"Invalid option: {option}")

    try:
        # ... existing command code with Task 7 error handling ...
```

### Task 11: JSON Parsing Optimization (CRITICAL)

**File**: `api.py`

**Issue**: `_read_json_response()` continues reading after complete JSON found, wasting bandwidth.

**Changes**:

```python
async def _read_json_response(self) -> dict[str, Any]:
    """Read JSON with early exit on complete parse."""
    if not self._reader:
        raise BarcoConnectionError("Not connected")

    try:
        buffer = b""
        max_buffer_size = 1024 * 1024

        while True:
            chunk = await asyncio.wait_for(
                self._reader.read(4096),
                timeout=self.timeout,
            )

            if not chunk:
                raise BarcoConnectionError("Connection closed by projector")

            buffer += chunk

            if len(buffer) > max_buffer_size:
                raise BarcoApiError(-1, f"Response too large (>{max_buffer_size} bytes)")

            try:
                result = json.loads(buffer.decode("utf-8"))
                # Successfully parsed - return immediately
                return result
            except json.JSONDecodeError:
                # Need more data
                continue

    except TimeoutError as err:
        raise BarcoConnectionError("Response timeout") from err
    except UnicodeDecodeError as err:
        raise BarcoApiError(-1, f"Invalid response encoding: {err}") from err
```

### Task 12: Async Refresh Error Handling (CRITICAL)

**Files**: All entity platform files

**Issue**: Entity commands call `async_request_refresh()` but don't handle refresh failures. If API call succeeds but refresh fails, command incorrectly appears to fail.

**Changes**:

Update error handling pattern from Task 7:
```python
async def async_<command>(self, ...) -> None:
    """Execute command with refresh error isolation."""
    try:
        await self.coordinator.device.<api_method>(...)
    except ... # (error handling from Task 7)

    # Request refresh but don't fail command if refresh fails
    try:
        await self.coordinator.async_request_refresh()
    except Exception as err:
        _LOGGER.warning("Failed to refresh after command: %s", err)
        # Command succeeded, just refresh failed - don't raise
```

## Testing Requirements## Testing Requirements

### Critical Path Tests (Required for Release)

1. **Connection Lifecycle**: Network interruption recovery, no resource leaks, config flow cleanup
2. **State Transitions**: Verify polling intervals adjust based on power state
3. **Error Handling**: Entity commands handle all exception types gracefully
4. **Data Validation**: Invalid API responses don't crash integration
5. **Entity Validation**: All unique_ids stable (never "None_suffix"), commands validate inputs
6. **Edge Cases**: Auth failure cleanup, incomplete JSON handling, simultaneous commands

### Validation Checklist

**Code Quality**:
- [ ] `scripts/lint` passes
- [ ] All imports use PowerState enum (if Task 1 completed)
- [ ] Type hints correct throughout
- [ ] All try/finally blocks ensure cleanup
- [ ] All entity commands have try/except with HomeAssistantError

**Functionality**:
- [ ] `scripts/develop` loads without errors
- [ ] All 17+ entities appear in HA UI
- [ ] Unique IDs stable across restarts (never "None_suffix")
- [ ] Dynamic polling confirmed in logs

**Robustness**:
- [ ] All 12 entity commands handle BarcoStateError, BarcoConnectionError, exceptions
- [ ] Number entities validate bounds before API call
- [ ] Select entities validate options before API call
- [ ] Connection health check implemented
- [ ] Coordinator disconnects on errors
- [ ] Config flow cleanup in finally blocks
- [ ] No resource leaks over 24h operation

**Release Preparation**:
- [ ] Version bumped to 0.0.2 in `manifest.json`
- [ ] README.md updated with features
- [ ] Known limitations documented

## Deferred to v0.0.3

- Introspection for picture setting constraints
- Subscription/notification support
- Automated test suite (pytest)
- Connection retry with exponential backoff
- Mock projector server
- Circuit breaker pattern
- Metrics/telemetry

## Validation Checklist

**Code Quality**:
- [ ] `scripts/lint` passes
- [ ] All imports updated to use PowerState enum
- [ ] No string literals for power states remain
- [ ] Type hints correct throughout
- [ ] All try/finally blocks ensure cleanup
- [ ] No bare except clauses
- [ ] All entity commands have try/except with HomeAssistantError

**Functionality**:
- [ ] `scripts/develop` loads integration without errors
- [ ] All 17+ entities appear in HA UI
- [ ] Laser power entity shows correct min/max
- [ ] Unique IDs stable across restarts (never "None_suffix")
- [ ] Dynamic polling confirmed in logs

**Entity Command Robustness** (NEW):
- [ ] All 12 entity commands handle BarcoStateError
- [ ] All 12 entity commands handle BarcoConnectionError
- [ ] All 12 entity commands handle unexpected exceptions
- [ ] Number entities validate bounds before API call
- [ ] Select entities validate options before API call
- [ ] Remote commands log errors for invalid input
- [ ] Command success even if refresh fails

**Stability & Robustness**:
- [ ] Connection health check implemented
- [ ] Stale connection detection works
- [ ] Coordinator disconnects on errors
- [ ] Config flow cleanup in finally blocks
- [ ] Data validation prevents ValueError crashes
- [ ] Rate limiting prevents API flooding
- [ ] No resource leaks over 24h operation
- [ ] Proper error recovery from all failure modes

**Release Preparation**:
- [ ] Version bumped to 0.0.2 in `manifest.json`
- [ ] README.md updated with all features
- [ ] Known limitations documented
- [ ] Troubleshooting section added

## Deferred to v0.0.3
- Introspection for picture setting constraints
- Subscription/notification support
- Automated test suite (pytest with mock projector)
- Connection retry with exponential backoff
- Mock projector server for testing
- Circuit breaker pattern for repeated failures
- Metrics/telemetry for performance monitoring
- Property caching to reduce API calls

## Critical Issues Summary

**CRITICAL** (must fix before release):
1. **No error handling in entity command methods** - All 12 entity command methods (power on/off, set values, select options) can propagate unhandled exceptions to HA core
2. **Race condition in coordinator.unique_id** - Property returns None during initialization, causes entity unique_id to be "None_suffix"
3. **Connection leak in connect() authentication** - If auth fails after connection established, connection never closed
4. **No validation on entity command inputs** - Invalid values passed directly to API without bounds checking
5. **Buffer incomplete JSON parsing** - `_read_json_response` continues reading after valid JSON, wasting bandwidth and memory
6. **async_request_refresh() not awaited in error paths** - Entity commands may leave stale data after API errors

**High Priority** (blocks v0.0.2 release):
7. Connection lifecycle management (Task 4) - prevents resource leaks
8. Data validation (Task 5) - prevents crashes on malformed responses
9. Config flow cleanup (Task 4) - prevents connection leaks during setup
10. **Float conversion without validation in coordinator** - 6 locations where float() can raise ValueError

**Medium Priority** (should fix):
11. Rate limiting enhancement (Task 6) - prevents API overload
12. Stale connection detection (Task 4) - improves recovery time
13. **No timeout on auth request** - connect() can hang indefinitely during authentication
14. **Remote command parsing errors silently ignored** - Invalid preset numbers swallowed without logging

**Low Priority** (nice to have):
15. Per-method rate limits - optimization
16. Connection health monitoring - observability
17. **Preset select shows all 30 presets** - Should filter to only assigned presets for better UX

---

## Deep Analysis Summary

### Code Quality Assessment

**Lines of Code Reviewed**: 1,856 lines across 11 Python files

**Architecture**: Well-structured with clean separation of concerns. Coordinator pattern correctly implemented.

**Type Safety**: Good - comprehensive type hints throughout, proper use of TYPE_CHECKING

**Exception Hierarchy**: Well-designed with specific exception types

### Critical Findings by Category

#### 1. **Error Handling** (12 Critical Issues)
- **Root Cause**: Entity platform methods lack exception handling
- **Impact**: User actions can crash integration or leave inconsistent state
- **Affected Code**: 12 methods across 4 files
- **Fix Complexity**: Medium - requires consistent pattern across all entities
- **Estimated Effort**: 2-3 hours

#### 2. **Connection Management** (4 High Issues)
- **Root Cause**: Incomplete connection lifecycle with edge case leaks
- **Impact**: Resource exhaustion over time, zombie connections
- **Affected Code**: api.py (5 locations), __init__.py (2 locations)
- **Fix Complexity**: Medium-High - requires careful state tracking
- **Estimated Effort**: 3-4 hours

#### 3. **Data Validation** (6 High Issues)
- **Root Cause**: Trust user and API inputs without validation
- **Impact**: ValueError crashes, unexpected behavior
- **Affected Code**: coordinator.py (6 float conversions), entities (12 input paths)
- **Fix Complexity**: Low-Medium - add validation checks
- **Estimated Effort**: 2 hours

#### 4. **Race Conditions** (1 Critical Issue)
- **Root Cause**: Property access before initialization complete
- **Impact**: Entity registry corruption with None in unique_ids
- **Affected Code**: coordinator.py unique_id property
- **Fix Complexity**: Low - add fallback value
- **Estimated Effort**: 30 minutes

### Risk Assessment

**Release Blocker Severity**: **HIGH**

- 6 CRITICAL issues that will cause visible user-facing errors
- 10 HIGH issues that cause reliability problems
- Without fixes, integration unsuitable for production use

**Testing Coverage**: Currently **0%** - no automated tests

**Recommended Action**: Fix all CRITICAL (Tasks 7-12) before any release

### Implementation Sequence

**Phase 1 - Critical Fixes** (Required before release):
1. Task 8: Coordinator unique_id (30 min) - Prevents entity corruption
2. Task 9: Auth cleanup (30 min) - Prevents connection leaks
3. Task 7: Entity error handling (2 hrs) - User-facing stability
4. Task 10: Input validation (2 hrs) - Prevents crashes
5. Task 12: Refresh error isolation (1 hr) - Command reliability

**Phase 2 - High Priority** (Should complete):
6. Task 4: Connection lifecycle (3 hrs) - Long-term stability
7. Task 5: Data validation (2 hrs) - Coordinator robustness
8. Task 11: JSON parsing (1 hr) - Performance

**Phase 3 - Medium/Low** (Nice to have):
9. Task 1: StrEnum (1 hr) - Type safety
10. Task 2: Laser constraints (1 hr) - Feature completeness
11. Task 6: Rate limiting (1 hr) - API protection
12. Task 3: Unique ID audit (30 min) - Verification

**Total Critical Path**: ~6.5 hours
**Total Recommended**: ~13 hours

### Code Patterns Requiring Attention

1. **Exception Propagation**: All async entity methods need consistent error handling
2. **Resource Cleanup**: All connection operations need try/finally
3. **Input Validation**: All user inputs need bounds/type checking before API calls
4. **State Validation**: All state-dependent operations need availability checks
5. **Logging**: Critical errors need ERROR level, state mismatches need WARNING

### Post-Fix Verification

**Must verify after fixes**:
1. Entity unique_ids never contain "None"
2. All entity commands handle all error types
3. No resource leaks after 100 reload cycles
4. Invalid inputs rejected before API calls
5. Connection failures don't crash integration
6. All API errors produce clear user messages

**Regression risks**:
- Error handling changes might hide legitimate issues
- Connection cleanup might break reconnection logic
- Input validation might be too strict for edge cases

Recommend incremental testing after each task completion.
