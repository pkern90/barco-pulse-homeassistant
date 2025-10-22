# High Priority Tasks - Stability Issues

**Priority**: HIGH - Strongly recommended for v0.0.2 release
**Total Tasks**: 3 (Tasks 4, 5, 11)
**Estimated Effort**: 6 hours

---

## Task 4: Connection Lifecycle & Error Handling

**Files**: `api.py`, `coordinator.py`, `config_flow.py`
**Estimated Time**: 3-4 hours

### Problems
- [ ] `_connected` flag inconsistent with actual connection state
- [ ] No stale connection detection
- [ ] Coordinator doesn't reset connection on errors
- [ ] Config flow creates temporary devices without cleanup guarantee
- [ ] No timeout on individual property fetches

### Implementation Checklist

#### api.py - Connection Health Check
- [ ] Add `_ensure_connected()` method
- [ ] Check if `_reader` and `_writer` exist
- [ ] Check if `_writer.is_closing()` returns True
- [ ] Reset connection state if stale detected
- [ ] Log warning on stale connection
- [ ] Call `await self.connect()` if not connected

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
```

#### api.py - Enhanced _send_request
- [ ] Call `await self._ensure_connected()` at start
- [ ] Wrap connection operations in try/except
- [ ] Catch `ConnectionError` and `OSError`
- [ ] Reset `_connected` flag on connection error
- [ ] Set `_reader = None` on error
- [ ] Set `_writer = None` on error
- [ ] Close writer in except block with try/except
- [ ] Wait for writer close with error handling
- [ ] Raise `BarcoConnectionError` from caught exception

```python
async def _send_request(self, method: str, params: Any = None) -> Any:
    """Send JSON-RPC request with connection validation."""
    async with self._lock:
        await self._ensure_connected()
        # ... existing request building code ...
        try:
            # ... existing send/receive code ...
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

#### coordinator.py - Error Recovery
- [ ] Import `ConfigEntryAuthFailed` from `homeassistant.exceptions`
- [ ] Wrap coordinator update in try/except
- [ ] Handle `BarcoAuthError` specifically
- [ ] Raise `ConfigEntryAuthFailed` for auth errors
- [ ] Handle `BarcoConnectionError` specifically
- [ ] Call `await self.device.disconnect()` on connection error
- [ ] Wrap disconnect in try/except to prevent double errors
- [ ] Raise `UpdateFailed` for connection errors
- [ ] Handle generic exceptions
- [ ] Call `await self.device.disconnect()` on generic errors
- [ ] Raise `UpdateFailed` for generic errors

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

#### config_flow.py - Resource Cleanup
- [ ] Wrap device creation in try/finally for `async_step_user`
- [ ] Create BarcoDevice instance
- [ ] Call `await device.connect()` in try block
- [ ] Call `await device.get_serial_number()` in try block
- [ ] Handle `BarcoConnectionError` in except block
- [ ] Set `errors["base"] = "cannot_connect"`
- [ ] Handle `BarcoAuthError` in except block
- [ ] Set `errors["base"] = "invalid_auth"`
- [ ] Add finally block
- [ ] Call `await device.disconnect()` in finally
- [ ] Wrap disconnect in try/except in finally

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

- [ ] Apply same pattern to `async_step_reconfigure`
- [ ] Create device in try/finally
- [ ] Test connection in try block
- [ ] Clean up in finally block

#### __init__.py - Shutdown Cleanup
- [ ] Verify `async_unload_entry` calls `device.disconnect()`
- [ ] Wrap disconnect in try/except
- [ ] Log disconnect errors but don't fail unload

### Verification
- [ ] `scripts/lint` passes
- [ ] Stale connection detection works
- [ ] Connection auto-recovery on network interruption
- [ ] Config flow cleanup verified in all paths
- [ ] Coordinator disconnects on all error types
- [ ] No resource leaks after 100 config flow attempts
- [ ] Test network disconnect during operation
- [ ] Test invalid auth during config flow
- [ ] Test connection timeout during config flow
- [ ] Monitor open connections with `lsof -p <pid>`

---

## Task 5: Data Validation & Type Safety

**Files**: `coordinator.py`, `api.py`
**Estimated Time**: 2 hours

### Problems
- [ ] No validation on API responses (could be None or wrong type)
- [ ] Unsafe `float()` conversions can raise ValueError
- [ ] Missing null checks before type conversions
- [ ] 6 float conversions in `_get_active_properties()` unprotected

### Implementation Checklist

#### coordinator.py - Response Validation
- [ ] Add type check on `get_properties()` response
- [ ] Check `isinstance(results, dict)`
- [ ] Log warning if response is not dict
- [ ] Return empty dict if invalid response type

```python
async def _get_active_properties(self) -> dict[str, Any]:
    """Get properties with validation."""
    data: dict[str, Any] = {}

    try:
        results = await self.device.get_properties(property_names)

        if not isinstance(results, dict):
            _LOGGER.warning("Invalid properties response type: %s", type(results))
            return data
```

#### coordinator.py - Safe Float Conversions
- [ ] Wrap laser_power float conversion in try/except
- [ ] Handle ValueError from invalid float
- [ ] Handle TypeError from None value
- [ ] Log warning with property name and invalid value
- [ ] Set property to None on conversion error
- [ ] Apply pattern to brightness conversion
- [ ] Apply pattern to contrast conversion
- [ ] Apply pattern to saturation conversion
- [ ] Apply pattern to hue conversion
- [ ] Apply pattern to all other float conversions

```python
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
            data[key] = None
```

#### coordinator.py - Integer Validation
- [ ] Add validation for preset_id (string to int conversion)
- [ ] Wrap `int()` conversion in try/except
- [ ] Handle ValueError from invalid integer
- [ ] Log warning on conversion failure
- [ ] Default to None on error

#### coordinator.py - String Validation
- [ ] Check state value exists before using
- [ ] Validate state is in known states list
- [ ] Check source value type before assignment
- [ ] Check profile value type before assignment
- [ ] Add type hints for all validated fields

#### api.py - Response Type Checking
- [ ] Add response validation in `get_properties()`
- [ ] Check result is dict before accessing keys
- [ ] Check property values are expected types
- [ ] Add validation in `get_sources()`
- [ ] Validate sources list is actually a list
- [ ] Add validation in `get_presets()`
- [ ] Validate presets response structure

### Verification
- [ ] `scripts/lint` passes
- [ ] All float conversions wrapped in try/except
- [ ] Invalid API responses don't crash coordinator
- [ ] Conversion errors logged with context
- [ ] Test with malformed API responses
- [ ] Test with None values in responses
- [ ] Test with wrong type values
- [ ] Test with missing expected properties
- [ ] Verify entities handle None values gracefully
- [ ] No ValueError exceptions in logs during normal operation

---

## Task 11: JSON Parsing Optimization

**File**: `api.py`
**Estimated Time**: 1 hour

**Note**: This is also listed in Critical Tasks. If completed there, skip here.

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
- [ ] Measure performance improvement with timing logs

---

## High Priority Tasks Summary

### Completion Checklist
- [ ] Task 4: Connection Lifecycle & Error Handling - COMPLETE
- [ ] Task 5: Data Validation & Type Safety - COMPLETE
- [ ] Task 11: JSON Parsing Optimization - COMPLETE

### Integration Testing
- [ ] Connection recovery after network interruption
- [ ] No resource leaks over 24 hour run
- [ ] Invalid API responses handled gracefully
- [ ] Config flow cleanup verified
- [ ] Coordinator error recovery functional
- [ ] Type conversions safe from crashes

### Final Verification
- [ ] All `scripts/lint` checks pass
- [ ] No ValueError in logs during testing
- [ ] No resource leaks detected
- [ ] Connection state consistent
- [ ] All error paths clean up resources
- [ ] Manual testing with network issues
- [ ] Manual testing with invalid data

### Release Readiness
- [ ] All 3 high priority tasks completed
- [ ] Integration with critical tasks verified
- [ ] No regression in existing functionality
- [ ] System stable under error conditions
- [ ] Ready to proceed with medium priority tasks
