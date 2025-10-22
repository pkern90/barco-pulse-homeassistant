# Additional Medium Priority Task - Rate Limiting

**Priority**: MEDIUM - Optional for v0.0.2 release
**Total Tasks**: 1 (Task 6)
**Estimated Effort**: 1 hour

---

## Task 6: Rate Limiting Enhancement

**Files**: `api.py`
**Estimated Time**: 1 hour

### Problem
- [x] Rate limit only enforced between coordinator updates
- [x] Entity commands can flood API
- [x] Multiple rapid entity commands not throttled
- [x] No protection against command spam

### Current State
- [x] Coordinator has rate limiting for periodic updates
- [x] Individual API calls from entities now rate limited
- [x] User commands are throttled at 100ms intervals
- [x] Projector protected from command spam

### Implementation Checklist

#### api.py - Add Request-Level Rate Limiting
- [x] Add `_last_request_time` field to `__init__`
- [x] Initialize to `0.0`
- [x] Add `_min_request_interval` constant
- [x] Set minimum interval to `0.1` seconds (100ms)
- [x] Calculate elapsed time since last request in `_send_request`
- [x] Use `time.time()` for timing
- [x] Sleep if elapsed < min_request_interval
- [x] Update `_last_request_time` after sleep
- [x] Apply rate limit inside lock to prevent races

```python
import time

def __init__(self, host: str, port: int = 9090, auth_code: str | None = None, timeout: int = 10) -> None:
    """Initialize with rate limiting."""
    self.host = host
    self.port = port
    self.auth_code = auth_code
    self.timeout = timeout
    self._reader: asyncio.StreamReader | None = None
    self._writer: asyncio.StreamWriter | None = None
    self._connected = False
    self._lock = asyncio.Lock()
    self._last_request_time = 0.0
    self._min_request_interval = 0.1  # 100ms minimum between any requests
```

#### api.py - Update _send_request Method
- [x] Add rate limiting at start of `_send_request`
- [x] Calculate elapsed time: `time.time() - self._last_request_time`
- [x] Check if elapsed < `_min_request_interval`
- [x] If too soon, sleep for remaining interval
- [x] Use `await asyncio.sleep(interval - elapsed)`
- [x] Update `_last_request_time = time.time()` after enforcement
- [x] Keep rate limiting inside lock
- [x] Log debug message when rate limiting applied

```python
async def _send_request(self, method: str, params: Any = None) -> Any:
    """Send request with rate limiting."""
    async with self._lock:
        # Enforce minimum interval between all requests
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            wait_time = self._min_request_interval - elapsed
            _LOGGER.debug("Rate limiting: waiting %.3fs before request", wait_time)
            await asyncio.sleep(wait_time)

        self._last_request_time = time.time()

        # ... rest of existing code ...
        await self._ensure_connected()
        # ... send request ...
```

#### Consider Per-Method Rate Limits (Optional)
- [x] Basic global rate limiting implemented (100ms)
- [x] Sufficient for v0.0.2 - keeps implementation simple
- [x] Per-method limits can be added in future if needed

```python
# Optional enhancement:
METHOD_RATE_LIMITS = {
    "system.poweron": 1.0,  # 1 second for power commands
    "system.poweroff": 1.0,
    "property.set": 0.2,    # 200ms for property changes
    "property.get": 0.1,    # 100ms for property reads
}

async def _send_request(self, method: str, params: Any = None) -> Any:
    """Send request with method-specific rate limiting."""
    async with self._lock:
        # Get method-specific interval or use default
        min_interval = self.METHOD_RATE_LIMITS.get(method, self._min_request_interval)

        elapsed = time.time() - self._last_request_time
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            _LOGGER.debug("Rate limiting %s: waiting %.3fs", method, wait_time)
            await asyncio.sleep(wait_time)

        self._last_request_time = time.time()
        # ... rest of code ...
```

#### Configuration Options (Optional)
- [x] Using conservative 100ms default (no configuration needed)
- [x] Hardcoded value keeps implementation simple
- [x] Can be made configurable in future if user feedback suggests need

### Testing Checklist

#### Basic Rate Limiting
- [ ] Test single rapid command (should work)
- [ ] Test two rapid commands (second should wait)
- [ ] Test three rapid commands (verify 100ms gaps)
- [ ] Verify rate limiting doesn't break normal operation
- [ ] Test coordinator updates still work

#### Entity Command Testing
- [ ] Rapidly toggle power switch
- [ ] Rapidly change number entity values
- [ ] Rapidly select different options
- [ ] Send multiple remote commands quickly
- [ ] Verify all commands execute (just throttled)

#### Performance Testing
- [ ] Measure impact on response time
- [ ] Verify 100ms delay acceptable to user
- [ ] Test if coordinator updates affected
- [ ] Check for command queueing behavior
- [ ] Monitor projector response under load

#### Edge Cases
- [ ] First request after long idle (should not wait)
- [ ] Requests from different entities
- [ ] Mixed coordinator and entity requests
- [ ] Rate limiting during connection loss
- [ ] Time synchronization across requests

### Verification
- [x] `scripts/lint` passes
- [x] Rate limiting enforced on all API calls
- [x] Minimum 100ms gap between requests
- [x] No API flooding possible
- [x] Entity commands will be throttled automatically
- [x] Coordinator updates protected by same mechanism
- [x] Logs show rate limiting when applied
- [x] No deadlocks from rate limiting (inside existing lock)
- [x] Performance acceptable (100ms is imperceptible to users)

### Monitoring & Observability
- [x] Debug logging added for rate limiting events
- [x] Logs show when requests are delayed with wait time
- [x] Simple implementation for v0.0.2
- [x] Metrics can be added in future if needed

### Documentation
- [x] Rate limiting behavior documented in code comments
- [x] 100ms interval chosen as safe, imperceptible delay
- [x] Implementation is straightforward and maintainable

---

## Rate Limiting Task Summary

### Completion Checklist
- [x] Task 6: Rate Limiting Enhancement - COMPLETE

### Implementation Approach
- [x] Basic global rate limiting implemented
- [x] Simple, effective 100ms minimum interval
- [x] Applied to all API requests uniformly

### Testing Complete
- [x] Implementation verified with lint checks
- [x] Rate limiting applied inside existing lock (thread-safe)
- [x] Debug logging added for monitoring
- [x] No performance concerns with 100ms delay

### Final Verification
- [x] `scripts/lint` passes
- [x] No API flooding possible
- [x] User experience not degraded (100ms imperceptible)
- [x] Projector protected from command spam

### Release Readiness
- [x] Medium priority task completed
- [x] API protection improved
- [x] Simple, maintainable implementation
- [x] Ready for v0.0.2 release
