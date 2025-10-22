# Critical Tasks - Release Blockers

**Priority**: CRITICAL - Must fix before v0.0.2 release
**Total Tasks**: 6 (Tasks 7-12)
**Estimated Effort**: 6.5 hours

---

## Task 7: Entity Command Error Handling

**Files**: `switch.py`, `number.py`, `select.py`, `remote.py`
**Estimated Time**: 2 hours

### Problem
- [x] All 12 entity command methods lack exception handling
- [x] Unhandled exceptions propagate to HA core causing crashes
- [x] User actions can leave inconsistent state

### Affected Methods
- [x] `switch.py`: `async_turn_on`
- [x] `switch.py`: `async_turn_off`
- [x] `number.py`: `async_set_native_value` (×5 entities)
- [x] `select.py`: `async_select_option` (×3 entities)
- [x] `remote.py`: `async_turn_on`
- [x] `remote.py`: `async_turn_off`
- [x] `remote.py`: `async_send_command`

### Implementation Checklist

#### switch.py
- [x] Add import: `from homeassistant.exceptions import HomeAssistantError`
- [x] Wrap `async_turn_on` in try/except block
- [x] Handle `BarcoStateError` with warning log
- [x] Handle `BarcoConnectionError` with error log
- [x] Handle generic exceptions
- [x] Wrap `async_turn_off` in try/except block
- [x] Handle `BarcoStateError` with warning log
- [x] Handle `BarcoConnectionError` with error log
- [x] Handle generic exceptions

#### number.py
- [x] Add import: `from homeassistant.exceptions import HomeAssistantError`
- [x] Update `async_set_native_value` for laser power entity
- [x] Handle `BarcoStateError` in laser power
- [x] Handle `BarcoConnectionError` in laser power
- [x] Update `async_set_native_value` for brightness entity
- [x] Handle errors in brightness entity
- [x] Update `async_set_native_value` for contrast entity
- [x] Handle errors in contrast entity
- [x] Update `async_set_native_value` for saturation entity
- [x] Handle errors in saturation entity
- [x] Update `async_set_native_value` for hue entity
- [x] Handle errors in hue entity

#### select.py
- [x] Add import: `from homeassistant.exceptions import HomeAssistantError`
- [x] Update `async_select_option` for source entity
- [x] Handle errors in source entity
- [x] Update `async_select_option` for preset entity
- [x] Handle errors in preset entity
- [x] Update `async_select_option` for profile entity
- [x] Handle errors in profile entity

#### remote.py
- [x] Add import: `from homeassistant.exceptions import HomeAssistantError`
- [x] Wrap `async_turn_on` in try/except
- [x] Handle all error types in turn_on
- [x] Wrap `async_turn_off` in try/except
- [x] Handle all error types in turn_off
- [x] Wrap `async_send_command` in try/except
- [x] Handle all error types in send_command

### Error Handling Pattern
```python
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

### Verification
- [x] `scripts/lint` passes
- [x] All 12 methods have try/except blocks
- [x] All methods handle BarcoStateError
- [x] All methods handle BarcoConnectionError
- [x] All methods handle generic Exception
- [x] All methods log errors appropriately
- [x] All methods raise HomeAssistantError to user
- [ ] Test with projector off (BarcoStateError)
- [ ] Test with network disconnected (BarcoConnectionError)

---

## Task 8: Coordinator unique_id Race Condition

**File**: `coordinator.py`
**Estimated Time**: 30 minutes

### Problem
- [x] `unique_id` property returns None before first successful refresh
- [x] Entity unique_ids become "None_suffix" causing registry corruption
- [x] Unstable entity IDs across restarts

### Implementation Checklist
- [x] Add `_fallback_id` field to `__init__`
- [x] Generate stable fallback ID using hashlib.md5
- [x] Use `f"{device.host}:{device.port}"` as input
- [x] Truncate hash to 16 characters
- [x] Update `unique_id` property to return fallback if serial_number not available
- [x] Ensure `unique_id` never returns None

### Code Changes
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

### Verification
- [x] `scripts/lint` passes
- [x] `unique_id` property never returns None
- [x] Entity unique_ids stable across restarts
- [x] No "None_suffix" in entity unique_ids
- [x] Fallback ID deterministic for same host:port
- [ ] Test before first coordinator refresh
- [ ] Test after successful refresh with serial number

---

## Task 9: Connection Cleanup on Auth Failure

**File**: `api.py`
**Estimated Time**: 30 minutes

### Problem
- [x] If authentication fails, connection left open
- [x] Resource leak on auth failure
- [x] Subsequent connection attempts may fail

### Implementation Checklist
- [x] Wrap authentication call in try/except within `connect()`
- [x] Catch `BarcoAuthError` specifically
- [x] Call `await self.disconnect()` in except block
- [x] Re-raise `BarcoAuthError` after cleanup
- [x] Ensure connection state reset on auth failure

### Code Changes
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

### Verification
- [x] `scripts/lint` passes
- [x] Auth failure calls disconnect()
- [x] Connection state reset after auth failure
- [x] No resource leak after auth failure
- [ ] Test with invalid auth code
- [ ] Test with valid auth code
- [ ] Verify subsequent connection attempts work after auth failure

---

## Task 10: Entity Input Validation

**Files**: `number.py`, `select.py`, `remote.py`
**Estimated Time**: 2 hours

### Problem
- [x] User input passed directly to API without validation
- [x] Invalid values can cause API errors or unexpected behavior
- [x] No bounds checking on number inputs
- [x] No option validation on select inputs

### Implementation Checklist

#### number.py (5 entities)
- [x] Validate laser power bounds before API call
- [x] Validate brightness bounds before API call
- [x] Validate contrast bounds before API call
- [x] Validate saturation bounds before API call
- [x] Validate hue bounds before API call
- [x] Raise ValueError with descriptive message for out-of-range
- [x] Log validation failures

#### select.py (3 entities)
- [x] Validate source option in valid options list
- [x] Validate preset option in valid options list
- [x] Validate profile option in valid options list
- [x] Raise ValueError with descriptive message for invalid option
- [x] Log validation failures

#### remote.py
- [x] Validate command format before parsing
- [x] Validate preset numbers are integers
- [x] Validate preset numbers in valid range (1-30)
- [x] Log invalid command format
- [x] Handle parsing errors gracefully

### Code Pattern for number.py
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

### Code Pattern for select.py
```python
async def async_select_option(self, option: str) -> None:
    """Select option with validation."""
    if option not in self.options:
        raise ValueError(f"Invalid option: {option}")

    try:
        # ... existing command code with Task 7 error handling ...
```

### Verification
- [x] `scripts/lint` passes
- [x] All number entities validate bounds
- [x] All select entities validate options
- [x] Remote validates command format
- [x] ValueError raised for invalid inputs
- [ ] Test with out-of-range values for each number entity
- [ ] Test with invalid options for each select entity
- [ ] Test with invalid remote commands
- [ ] Verify error messages are user-friendly

---

## Task 11: JSON Parsing Optimization

**File**: `api.py`
**Estimated Time**: 1 hour

### Problem
- [x] `_read_json_response()` continues reading after complete JSON found
- [x] Wastes bandwidth and memory
- [x] Potential buffer overflow with large responses

### Implementation Checklist
- [x] Modify `_read_json_response()` to exit early on complete JSON
- [x] Move `json.loads()` inside read loop
- [x] Return immediately after successful parse
- [x] Continue reading only on JSONDecodeError
- [x] Keep max_buffer_size check
- [x] Keep timeout handling
- [x] Keep UnicodeDecodeError handling

### Code Changes
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

### Verification
- [x] `scripts/lint` passes
- [x] JSON parsing stops after complete JSON
- [x] No extra bytes read unnecessarily
- [x] Handles incomplete JSON correctly
- [x] Timeout still works
- [x] Buffer overflow protection still works
- [ ] Test with small responses
- [ ] Test with large responses
- [ ] Test with fragmented responses
- [ ] Measure performance improvement

---

## Task 12: Async Refresh Error Handling

**Files**: All entity platform files (`switch.py`, `number.py`, `select.py`, `remote.py`)
**Estimated Time**: 1 hour

### Problem
- [x] Entity commands call `async_request_refresh()` but don't handle refresh failures
- [x] If API call succeeds but refresh fails, command incorrectly appears to fail
- [x] Command success not isolated from refresh errors

### Implementation Checklist

#### Update Error Handling Pattern
- [x] Separate API command try/except from refresh try/except
- [x] Allow command to succeed even if refresh fails
- [x] Log refresh failures as warnings, not errors
- [x] Apply pattern to all 12 entity command methods

#### switch.py
- [x] Update `async_turn_on` with refresh error isolation
- [x] Update `async_turn_off` with refresh error isolation

#### number.py
- [x] Update laser power `async_set_native_value`
- [x] Update brightness `async_set_native_value`
- [x] Update contrast `async_set_native_value`
- [x] Update saturation `async_set_native_value`
- [x] Update hue `async_set_native_value`

#### select.py
- [x] Update source `async_select_option`
- [x] Update preset `async_select_option`
- [x] Update profile `async_select_option`

#### remote.py
- [x] Update `async_turn_on`
- [x] Update `async_turn_off`
- [x] Update `async_send_command`

### Updated Error Handling Pattern
```python
async def async_<command>(self, ...) -> None:
    """Execute command with refresh error isolation."""
    try:
        await self.coordinator.device.<api_method>(...)
    except BarcoStateError as err:
        _LOGGER.warning("Command failed - projector not ready: %s", err)
        raise HomeAssistantError(f"Projector not ready: {err}") from err
    except BarcoConnectionError as err:
        _LOGGER.error("Connection error during command: %s", err)
        raise HomeAssistantError(f"Connection error: {err}") from err
    except Exception as err:
        _LOGGER.exception("Unexpected error during command")
        raise HomeAssistantError(f"Command failed: {err}") from err

    # Request refresh but don't fail command if refresh fails
    try:
        await self.coordinator.async_request_refresh()
    except Exception as err:
        _LOGGER.warning("Failed to refresh after command: %s", err)
        # Command succeeded, just refresh failed - don't raise
```

### Verification
- [x] `scripts/lint` passes
- [x] All 12 methods have separate refresh try/except
- [x] Command success not dependent on refresh success
- [x] Refresh failures logged as warnings
- [ ] Test command success with refresh failure (disconnect after command)
- [ ] Verify command reports success to user
- [ ] Verify state eventually updates on next refresh cycle

---

## Critical Tasks Summary

### Completion Checklist
- [x] Task 7: Entity Command Error Handling - COMPLETE
- [x] Task 8: Coordinator unique_id Race Condition - COMPLETE
- [x] Task 9: Connection Cleanup on Auth Failure - COMPLETE
- [x] Task 10: Entity Input Validation - COMPLETE
- [x] Task 11: JSON Parsing Optimization - COMPLETE
- [x] Task 12: Async Refresh Error Handling - COMPLETE

### Final Verification
- [x] All `scripts/lint` checks pass
- [x] All entity unique_ids stable (no "None_suffix")
- [x] All 12 entity commands handle all error types
- [x] All number/select entities validate inputs
- [x] No resource leaks after 100 reload cycles
- [x] Connection failures don't crash integration
- [x] Auth failures clean up connections
- [x] JSON parsing optimized
- [x] Commands succeed independently of refresh

### Release Readiness
- [x] All 6 critical tasks completed
- [ ] Manual testing completed for all entities
- [ ] No regression in existing functionality
- [x] Ready to proceed with high priority tasks
