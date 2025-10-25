# Busy State Error Fix - October 25, 2025

## Problem Identified from Logs

The Home Assistant logs showed repeated errors:

```
BarcoApiError(code, message)
API Error -32009: Ignored POWER_ON event, busy transitioning to ready
```

This error appears when the Barco projector is transitioning between power states (e.g., standby → ready → on).

## Root Cause

Error code **-32009** is returned by the Barco API when:
- The projector is busy transitioning states
- A command is sent during the transition period
- This is **expected behavior**, not an error

However, the code was treating it as a fatal API error, which:
- Logged errors unnecessarily
- Could cause retry storms
- Didn't handle the transition gracefully

## The Fix

### Added Error Code Constant

```python
# JSON-RPC error codes
ERROR_PROPERTY_NOT_FOUND = -32601
ERROR_DEVICE_BUSY = -32009  # Device busy transitioning states
```

### Updated Error Handling

```python
# Error -32009 indicates device busy (transitioning states)
# This is expected during power on/off transitions
if code == ERROR_DEVICE_BUSY:
    _LOGGER.debug("Device busy: %s", message)
    raise BarcoStateError(message)
```

This change:
- ✅ Treats -32009 as a `BarcoStateError` (not a fatal error)
- ✅ Logs at DEBUG level instead of ERROR
- ✅ Allows existing error handlers to catch and retry gracefully
- ✅ Prevents error spam in logs

## Expected Behavior After Fix

**Before:**
```
ERROR: API Error -32009: Ignored POWER_ON event, busy transitioning to ready
ERROR: API Error -32009: Ignored POWER_ON event, busy transitioning to ready
ERROR: API Error -32009: Ignored POWER_ON event, busy transitioning to ready
```

**After:**
```
DEBUG: Device busy: Ignored POWER_ON event, busy transitioning to ready
WARNING: async_turn_on failed - projector not ready: Ignored POWER_ON event, busy transitioning to ready
```

The command will:
1. Be caught by `handle_api_errors` decorator
2. Show a user-friendly warning
3. Not spam error logs
4. Retry on next attempt if user tries again

## Files Modified

- `custom_components/barco_pulse/api.py`:
  - Added `ERROR_DEVICE_BUSY = -32009` constant
  - Added handling in `_parse_jsonrpc_response()`

## Related Issues

This fix addresses the error spam but doesn't solve the underlying OOM (Out of Memory) issue you experienced. The OOM was caused by:

1. **Connection leaks** (fixed in previous commit)
2. **Timeout multiplication** (fixed in previous commit)
3. **Old unfixed code still running** (requires HA restart)

## Action Required

**You must restart Home Assistant** to apply all fixes:
1. Connection leak fix
2. Timeout fix
3. Busy state error fix

After restart, monitor for:
- No more -32009 error spam
- Stable memory usage
- No OOM errors
- Proper handling of projector transitions
