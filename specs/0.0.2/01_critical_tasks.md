# Critical Tasks - Release Blockers

**Priority**: CRITICAL - Must fix before v0.0.2 release
**Total Tasks**: 6 (Tasks 7-12)
**Estimated Effort**: 6.5 hours

---

## Task 7: Entity Command Error Handling

**Files**: `switch.py`, `number.py`, `select.py`, `remote.py`
**Estimated Time**: 2 hours

### Problem
- [ ] All 12 entity command methods lack exception handling
- [ ] Unhandled exceptions propagate to HA core causing crashes
- [ ] User actions can leave inconsistent state

### Affected Methods
- [ ] `switch.py`: `async_turn_on`
- [ ] `switch.py`: `async_turn_off`
- [ ] `number.py`: `async_set_native_value` (×5 entities)
- [ ] `select.py`: `async_select_option` (×3 entities)
- [ ] `remote.py`: `async_turn_on`
- [ ] `remote.py`: `async_turn_off`
- [ ] `remote.py`: `async_send_command`

### Implementation Checklist

#### switch.py
- [ ] Add import: `from homeassistant.exceptions import HomeAssistantError`
- [ ] Wrap `async_turn_on` in try/except block
- [ ] Handle `BarcoStateError` with warning log
- [ ] Handle `BarcoConnectionError` with error log
- [ ] Handle generic exceptions
- [ ] Wrap `async_turn_off` in try/except block
- [ ] Handle `BarcoStateError` with warning log
- [ ] Handle `BarcoConnectionError` with error log
- [ ] Handle generic exceptions

#### number.py
- [ ] Add import: `from homeassistant.exceptions import HomeAssistantError`
- [ ] Update `async_set_native_value` for laser power entity
- [ ] Handle `BarcoStateError` in laser power
- [ ] Handle `BarcoConnectionError` in laser power
- [ ] Update `async_set_native_value` for brightness entity
- [ ] Handle errors in brightness entity
- [ ] Update `async_set_native_value` for contrast entity
- [ ] Handle errors in contrast entity
- [ ] Update `async_set_native_value` for saturation entity
- [ ] Handle errors in saturation entity
- [ ] Update `async_set_native_value` for hue entity
- [ ] Handle errors in hue entity

#### select.py
- [ ] Add import: `from homeassistant.exceptions import HomeAssistantError`
- [ ] Update `async_select_option` for source entity
- [ ] Handle errors in source entity
- [ ] Update `async_select_option` for preset entity
- [ ] Handle errors in preset entity
- [ ] Update `async_select_option` for profile entity
- [ ] Handle errors in profile entity

#### remote.py
- [ ] Add import: `from homeassistant.exceptions import HomeAssistantError`
- [ ] Wrap `async_turn_on` in try/except
- [ ] Handle all error types in turn_on
- [ ] Wrap `async_turn_off` in try/except
- [ ] Handle all error types in turn_off
- [ ] Wrap `async_send_command` in try/except
- [ ] Handle all error types in send_command

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
- [ ] `scripts/lint` passes
- [ ] All 12 methods have try/except blocks
- [ ] All methods handle BarcoStateError
- [ ] All methods handle BarcoConnectionError
- [ ] All methods handle generic Exception
- [ ] All methods log errors appropriately
- [ ] All methods raise HomeAssistantError to user
- [ ] Test with projector off (BarcoStateError)
- [ ] Test with network disconnected (BarcoConnectionError)

---

## Task 8: Coordinator unique_id Race Condition

**File**: `coordinator.py`
**Estimated Time**: 30 minutes

### Problem
- [ ] `unique_id` property returns None before first successful refresh
- [ ] Entity unique_ids become "None_suffix" causing registry corruption
- [ ] Unstable entity IDs across restarts

### Implementation Checklist
- [ ] Add `_fallback_id` field to `__init__`
- [ ] Generate stable fallback ID using hashlib.md5
- [ ] Use `f"{device.host}:{device.port}"` as input
- [ ] Truncate hash to 16 characters
- [ ] Update `unique_id` property to return fallback if serial_number not available
- [ ] Ensure `unique_id` never returns None

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
- [ ] `scripts/lint` passes
- [ ] `unique_id` property never returns None
- [ ] Entity unique_ids stable across restarts
- [ ] No "None_suffix" in entity unique_ids
- [ ] Fallback ID deterministic for same host:port
- [ ] Test before first coordinator refresh
- [ ] Test after successful refresh with serial number

---

## Task 9: Connection Cleanup on Auth Failure

**File**: `api.py`
**Estimated Time**: 30 minutes

### Problem
- [ ] If authentication fails, connection left open
- [ ] Resource leak on auth failure
- [ ] Subsequent connection attempts may fail

### Implementation Checklist
- [ ] Wrap authentication call in try/except within `connect()`
- [ ] Catch `BarcoAuthError` specifically
- [ ] Call `await self.disconnect()` in except block
- [ ] Re-raise `BarcoAuthError` after cleanup
- [ ] Ensure connection state reset on auth failure

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
- [ ] `scripts/lint` passes
- [ ] Auth failure calls disconnect()
- [ ] Connection state reset after auth failure
- [ ] No resource leak after auth failure
- [ ] Test with invalid auth code
- [ ] Test with valid auth code
- [ ] Verify subsequent connection attempts work after auth failure

---

## Task 10: Entity Input Validation

**Files**: `number.py`, `select.py`, `remote.py`
**Estimated Time**: 2 hours

### Problem
- [ ] User input passed directly to API without validation
- [ ] Invalid values can cause API errors or unexpected behavior
- [ ] No bounds checking on number inputs
- [ ] No option validation on select inputs

### Implementation Checklist

#### number.py (5 entities)
- [ ] Validate laser power bounds before API call
- [ ] Validate brightness bounds before API call
- [ ] Validate contrast bounds before API call
- [ ] Validate saturation bounds before API call
- [ ] Validate hue bounds before API call
- [ ] Raise ValueError with descriptive message for out-of-range
- [ ] Log validation failures

#### select.py (3 entities)
- [ ] Validate source option in valid options list
- [ ] Validate preset option in valid options list
- [ ] Validate profile option in valid options list
- [ ] Raise ValueError with descriptive message for invalid option
- [ ] Log validation failures

#### remote.py
- [ ] Validate command format before parsing
- [ ] Validate preset numbers are integers
- [ ] Validate preset numbers in valid range (1-30)
- [ ] Log invalid command format
- [ ] Handle parsing errors gracefully

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
- [ ] `scripts/lint` passes
- [ ] All number entities validate bounds
- [ ] All select entities validate options
- [ ] Remote validates command format
- [ ] ValueError raised for invalid inputs
- [ ] Test with out-of-range values for each number entity
- [ ] Test with invalid options for each select entity
- [ ] Test with invalid remote commands
- [ ] Verify error messages are user-friendly

---

## Task 11: JSON Parsing Optimization

**File**: `api.py`
**Estimated Time**: 1 hour

### Problem
- [ ] `_read_json_response()` continues reading after complete JSON found
- [ ] Wastes bandwidth and memory
- [ ] Potential buffer overflow with large responses

### Implementation Checklist
- [ ] Modify `_read_json_response()` to exit early on complete JSON
- [ ] Move `json.loads()` inside read loop
- [ ] Return immediately after successful parse
- [ ] Continue reading only on JSONDecodeError
- [ ] Keep max_buffer_size check
- [ ] Keep timeout handling
- [ ] Keep UnicodeDecodeError handling

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
- [ ] `scripts/lint` passes
- [ ] JSON parsing stops after complete JSON
- [ ] No extra bytes read unnecessarily
- [ ] Handles incomplete JSON correctly
- [ ] Timeout still works
- [ ] Buffer overflow protection still works
- [ ] Test with small responses
- [ ] Test with large responses
- [ ] Test with fragmented responses
- [ ] Measure performance improvement

---

## Task 12: Async Refresh Error Handling

**Files**: All entity platform files (`switch.py`, `number.py`, `select.py`, `remote.py`)
**Estimated Time**: 1 hour

### Problem
- [ ] Entity commands call `async_request_refresh()` but don't handle refresh failures
- [ ] If API call succeeds but refresh fails, command incorrectly appears to fail
- [ ] Command success not isolated from refresh errors

### Implementation Checklist

#### Update Error Handling Pattern
- [ ] Separate API command try/except from refresh try/except
- [ ] Allow command to succeed even if refresh fails
- [ ] Log refresh failures as warnings, not errors
- [ ] Apply pattern to all 12 entity command methods

#### switch.py
- [ ] Update `async_turn_on` with refresh error isolation
- [ ] Update `async_turn_off` with refresh error isolation

#### number.py
- [ ] Update laser power `async_set_native_value`
- [ ] Update brightness `async_set_native_value`
- [ ] Update contrast `async_set_native_value`
- [ ] Update saturation `async_set_native_value`
- [ ] Update hue `async_set_native_value`

#### select.py
- [ ] Update source `async_select_option`
- [ ] Update preset `async_select_option`
- [ ] Update profile `async_select_option`

#### remote.py
- [ ] Update `async_turn_on`
- [ ] Update `async_turn_off`
- [ ] Update `async_send_command`

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
- [ ] `scripts/lint` passes
- [ ] All 12 methods have separate refresh try/except
- [ ] Command success not dependent on refresh success
- [ ] Refresh failures logged as warnings
- [ ] Test command success with refresh failure (disconnect after command)
- [ ] Verify command reports success to user
- [ ] Verify state eventually updates on next refresh cycle

---

## Critical Tasks Summary

### Completion Checklist
- [ ] Task 7: Entity Command Error Handling - COMPLETE
- [ ] Task 8: Coordinator unique_id Race Condition - COMPLETE
- [ ] Task 9: Connection Cleanup on Auth Failure - COMPLETE
- [ ] Task 10: Entity Input Validation - COMPLETE
- [ ] Task 11: JSON Parsing Optimization - COMPLETE
- [ ] Task 12: Async Refresh Error Handling - COMPLETE

### Final Verification
- [ ] All `scripts/lint` checks pass
- [ ] All entity unique_ids stable (no "None_suffix")
- [ ] All 12 entity commands handle all error types
- [ ] All number/select entities validate inputs
- [ ] No resource leaks after 100 reload cycles
- [ ] Connection failures don't crash integration
- [ ] Auth failures clean up connections
- [ ] JSON parsing optimized
- [ ] Commands succeed independently of refresh

### Release Readiness
- [ ] All 6 critical tasks completed
- [ ] Manual testing completed for all entities
- [ ] No regression in existing functionality
- [ ] Ready to proceed with high priority tasks
