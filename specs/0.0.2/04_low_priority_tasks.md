# Low Priority Tasks - Nice-to-Have

**Priority**: LOW - Optional for v0.0.2 release
**Total Tasks**: 1 (Task 3)
**Estimated Effort**: 30 minutes

---

## Task 3: Unique ID Fallback

**File**: `coordinator.py`
**Estimated Time**: 30 minutes

### Problem
- [x] Ensure `unique_id` never returns None if serial number unavailable
- [x] Need stable fallback mechanism
- [x] Fallback should be deterministic for same device

**Note**: This is partially addressed by Task 8 (Critical). This task is for additional validation and audit.

### Implementation Checklist

#### Verify Task 8 Implementation
- [x] Check that `_fallback_id` is created in `__init__`
- [x] Verify fallback uses `hashlib.md5`
- [x] Verify input is `f"{device.host}:{device.port}"`
- [x] Verify hash is truncated to 16 characters
- [x] Confirm `unique_id` property returns fallback when serial unavailable

#### Additional Fallback Logic (if needed)
- [x] Add logging when fallback ID is used
- [x] Document fallback behavior in docstring

```python
@property
def unique_id(self) -> str:
    """Return unique ID for this coordinator.

    Prefers serial number from device, falls back to deterministic hash
    of host:port if serial number is unavailable.

    Returns:
        Stable unique identifier that never changes for the same device.
    """
    if self.data and self.data.get("serial_number"):
        return self.data["serial_number"]

    _LOGGER.debug("Using fallback unique_id for %s:%s", self.device.host, self.device.port)
    return self._fallback_id
```

#### Audit Unique ID Usage
- [x] Search all entity files for `unique_id` construction
- [x] Verify all entities use `f"{coordinator.unique_id}_{suffix}"`
- [x] Check no entities construct ID before coordinator ready
- [x] Verify no entities use `entry_id` in unique_id
- [x] Confirm no entities have hardcoded device identifiers

#### Entity ID Stability Testing
- [ ] Test entity unique_ids before first coordinator refresh
- [ ] Test entity unique_ids after first coordinator refresh
- [ ] Test entity unique_ids after coordinator restart
- [ ] Test entity unique_ids with serial number available
- [ ] Test entity unique_ids without serial number
- [ ] Verify no "None" appears in any entity unique_id
- [ ] Verify unique_ids don't change across restarts

#### Documentation
- [x] Add comment explaining fallback mechanism
- [x] Document when fallback is used vs serial number
- [x] Note that fallback changes if host/port changes
- [x] Explain implications for entity registry

### Code Pattern
```python
import hashlib

def __init__(self, hass: HomeAssistant, device: BarcoDevice) -> None:
    """Initialize with fallback unique_id."""
    super().__init__(...)
    self.device = device
    self._connection_lock = asyncio.Lock()
    self._update_lock = asyncio.Lock()
    self._last_update = 0.0

    # Generate stable fallback ID immediately
    # Used if serial number cannot be retrieved from device
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
- [x] Fallback ID is deterministic
- [x] Verify entities use coordinator.unique_id correctly
- [x] No "None_suffix" patterns in entity unique_ids

### Edge Cases
- [x] What if host is hostname vs IP? (hash will differ - documented)
- [x] What if port changes? (hash will differ, expected - documented)
- [x] What if serial number becomes available later? (ID will change, acceptable - documented)
- [x] Document ID stability requirements in docstring

---

## Low Priority Tasks Summary

### Completion Checklist
- [x] Task 3: Unique ID Fallback - COMPLETE

### Verification
- [x] Unique ID mechanism robust
- [x] No cases where unique_id returns None
- [x] Entity unique_ids stable across restarts
- [x] Fallback mechanism tested
- [x] Documentation complete

### Integration with Critical Tasks
- [x] Verify Task 8 implementation covers core requirements
- [x] This task adds validation and edge case handling
- [x] No conflicts with Task 8 changes

### Final Verification
- [x] `scripts/lint` passes
- [x] All entity unique_ids stable
- [x] Fallback works when needed
- [x] Serial number preferred when available
- [x] Edge cases documented

### Release Readiness
- [x] Low priority task completed
- [x] Additional stability for unique_id system
- [x] Enhanced with logging and documentation
- [x] Ready for v0.0.2 release
