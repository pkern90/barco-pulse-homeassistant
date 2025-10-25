# Connection Leak in connect() Method - Bug Fix #5

## Problem

The `connect()` method in `api.py` had a **critical connection leak** when authentication failed after a successful TCP connection was established.

### Code Flow

```python
async def connect(self) -> None:
    # 1. Open TCP connection
    self._reader, self._writer = await asyncio.wait_for(
        asyncio.open_connection(self.host, self.port),
        timeout=self.timeout,
    )

    # 2. Authenticate if PIN provided
    if self.auth_code:
        await self.authenticate()  # ⚠️ If this fails, connection leaks!
```

### The Bug

1. **Connection opened** at line 69: TCP socket created, `_reader` and `_writer` assigned
2. **Authentication attempted** at line 78: `authenticate()` called
3. **If authentication fails**: Exception propagates up, method exits
4. **Connection never cleaned up**: Socket left open, resources leaked

### Why This Is Critical

This bug triggers on **every authentication failure**:

- **Wrong PIN entered in config**: Leak on every connection attempt
- **Projector requires auth but none provided**: Leak on every poll
- **Network issues during auth**: Leak on timeout/interruption
- **State transition during auth**: Leak if projector becomes busy

With coordinator polling every 2-30 seconds, this could leak hundreds of sockets per day if authentication starts failing.

### Impact Chain

```
Auth failure → Socket leak → File descriptor exhaustion →
Network stack degradation → DNS failures → HA unavailable
```

This is the **same root cause** as bugs #1 and #4, just in a different code path.

## Solution

Wrap authentication in try/except to ensure cleanup on failure:

```python
async def connect(self) -> None:
    """Establish connection to Barco Pulse device."""
    if self._reader and self._writer:
        return

    try:
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port),
            timeout=self.timeout,
        )

        # Authenticate if PIN provided
        # Wrapped in try/except to ensure cleanup on auth failure
        if self.auth_code:
            try:
                await self.authenticate()
            except Exception:
                # Auth failed after connection opened - must cleanup
                await self.disconnect()
                raise

    except TimeoutError as err:
        raise BarcoConnectionError(
            f"Connection to {self.host}:{self.port} timed out"
        ) from err
    except OSError as err:
        raise BarcoConnectionError(
            f"Failed to connect to {self.host}:{self.port}: {err}"
        ) from err
```

### Key Changes

1. **Inner try/except block**: Catches any authentication exception
2. **Explicit cleanup**: Calls `disconnect()` before re-raising
3. **Proper error propagation**: Re-raises original exception after cleanup
4. **TimeoutError modernization**: Uses built-in `TimeoutError` instead of `asyncio.TimeoutError`

## Testing Scenarios

This fix handles:

1. **Wrong authentication code**: Connection cleaned up, BarcoAuthError propagated
2. **Network interruption during auth**: Connection cleaned up, BarcoConnectionError propagated
3. **Projector busy during auth**: Connection cleaned up, BarcoStateError propagated
4. **Any other auth failure**: Connection always cleaned up, original exception preserved

## Related Bugs

This is part of a systematic fix for connection lifecycle issues:

- **Bug #1**: `_ensure_connected()` didn't cleanup stale connections → Fixed
- **Bug #2**: Timeout multiplication allowed 2560s hangs → Fixed
- **Bug #3**: `-32009` not recognized as expected busy state → Fixed
- **Bug #4**: Read timeouts left connections in broken state → Fixed
- **Bug #5**: Auth failures leaked connections (this fix) → Fixed

All five bugs contributed to socket exhaustion causing HA crashes.

## Verification

After this fix:

1. **Monitor file descriptors**: Should stay stable even with auth failures
2. **Check logs for auth errors**: Should show proper error without leaks
3. **Test wrong PIN scenario**: Restart with incorrect auth_code, verify no leaks
4. **Monitor network connections**: `netstat -an | grep 9090` should show clean closes

## Timeline

- **Discovered**: During comprehensive audit after user's 3rd crash
- **Fixed**: Same session as bugs #1-4
- **Status**: Awaiting HA restart for validation
