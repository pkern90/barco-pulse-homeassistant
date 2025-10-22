# Additional Medium Priority Task - Rate Limiting

**Priority**: MEDIUM - Optional for v0.0.2 release
**Total Tasks**: 1 (Task 6)
**Estimated Effort**: 1 hour

---

## Task 6: Rate Limiting Enhancement

**Files**: `api.py`
**Estimated Time**: 1 hour

### Problem
- [ ] Rate limit only enforced between coordinator updates
- [ ] Entity commands can flood API
- [ ] Multiple rapid entity commands not throttled
- [ ] No protection against command spam

### Current State
- [ ] Coordinator has rate limiting for periodic updates
- [ ] Individual API calls from entities not rate limited
- [ ] User can trigger multiple commands simultaneously
- [ ] Projector may reject or queue excessive commands

### Implementation Checklist

#### api.py - Add Request-Level Rate Limiting
- [ ] Add `_last_request_time` field to `__init__`
- [ ] Initialize to `0.0`
- [ ] Add `_min_request_interval` constant
- [ ] Set minimum interval to `0.1` seconds (100ms)
- [ ] Calculate elapsed time since last request in `_send_request`
- [ ] Use `time.time()` for timing
- [ ] Sleep if elapsed < min_request_interval
- [ ] Update `_last_request_time` after sleep
- [ ] Apply rate limit inside lock to prevent races

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
- [ ] Add rate limiting at start of `_send_request`
- [ ] Calculate elapsed time: `time.time() - self._last_request_time`
- [ ] Check if elapsed < `_min_request_interval`
- [ ] If too soon, sleep for remaining interval
- [ ] Use `await asyncio.sleep(interval - elapsed)`
- [ ] Update `_last_request_time = time.time()` after enforcement
- [ ] Keep rate limiting inside lock
- [ ] Log debug message when rate limiting applied

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
- [ ] Some methods may need different limits
- [ ] Power on/off might need longer intervals
- [ ] Property queries can be faster
- [ ] Consider dict mapping method to interval
- [ ] Implement method-specific rate limiting if needed

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
- [ ] Consider making rate limit configurable
- [ ] Add to config flow as advanced option
- [ ] Store in config entry options
- [ ] Allow per-device rate limit customization
- [ ] Default to conservative 100ms

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
- [ ] `scripts/lint` passes
- [ ] Rate limiting enforced on all API calls
- [ ] Minimum 100ms gap between requests
- [ ] No API flooding possible
- [ ] Entity commands still responsive
- [ ] Coordinator updates not impacted
- [ ] Logs show rate limiting when applied
- [ ] No deadlocks from rate limiting
- [ ] Performance acceptable

### Monitoring & Observability
- [ ] Add debug logging for rate limiting events
- [ ] Log when requests are delayed
- [ ] Consider adding metrics for throttled requests
- [ ] Track average request interval
- [ ] Identify if rate limit too aggressive/lenient

### Documentation
- [ ] Document rate limiting behavior
- [ ] Explain why 100ms interval chosen
- [ ] Note method-specific limits if implemented
- [ ] Describe configuration options if added
- [ ] Update README with rate limit info

---

## Rate Limiting Task Summary

### Completion Checklist
- [ ] Task 6: Rate Limiting Enhancement - COMPLETE

### Implementation Approach
- [ ] Basic global rate limiting implemented
- [ ] OR method-specific rate limiting implemented
- [ ] OR configurable rate limiting implemented

### Testing Complete
- [ ] Basic functionality verified
- [ ] Entity commands tested
- [ ] Performance acceptable
- [ ] Edge cases handled

### Final Verification
- [ ] `scripts/lint` passes
- [ ] No API flooding possible
- [ ] User experience not degraded
- [ ] Projector protected from command spam

### Optional Enhancements for Future
- [ ] Dynamic rate limiting based on projector response
- [ ] Adaptive intervals based on error rates
- [ ] Per-entity rate limiting
- [ ] Rate limit statistics in diagnostics
- [ ] Circuit breaker pattern integration

### Release Readiness
- [ ] Medium priority task completed (optional)
- [ ] API protection improved
- [ ] No impact if deferred to v0.0.3
- [ ] Safe to skip if time constrained
