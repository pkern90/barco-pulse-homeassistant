# Low Priority Tasks - Nice-to-Have

**Priority**: LOW - Optional for v0.0.2 release
**Total Tasks**: 1 (Task 3)
**Estimated Effort**: 30 minutes

---

## Task 3: Unique ID Fallback

**File**: `coordinator.py`
**Estimated Time**: 30 minutes

### Problem
- [ ] Ensure `unique_id` never returns None if serial number unavailable
- [ ] Need stable fallback mechanism
- [ ] Fallback should be deterministic for same device

**Note**: This is partially addressed by Task 8 (Critical). This task is for additional validation and audit.

### Implementation Checklist

#### Verify Task 8 Implementation
- [ ] Check that `_fallback_id` is created in `__init__`
- [ ] Verify fallback uses `hashlib.md5`
- [ ] Verify input is `f"{device.host}:{device.port}"`
- [ ] Verify hash is truncated to 16 characters
- [ ] Confirm `unique_id` property returns fallback when serial unavailable

#### Additional Fallback Logic (if needed)
- [ ] Consider adding device MAC address to fallback if available
- [ ] Consider using entry_id as ultimate fallback
- [ ] Add logging when fallback ID is used
- [ ] Document fallback behavior in docstring

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
- [ ] Search all entity files for `unique_id` construction
- [ ] Verify all entities use `f"{coordinator.unique_id}_{suffix}"`
- [ ] Check no entities construct ID before coordinator ready
- [ ] Verify no entities use `entry_id` in unique_id
- [ ] Confirm no entities have hardcoded device identifiers

#### Entity ID Stability Testing
- [ ] Test entity unique_ids before first coordinator refresh
- [ ] Test entity unique_ids after first coordinator refresh
- [ ] Test entity unique_ids after coordinator restart
- [ ] Test entity unique_ids with serial number available
- [ ] Test entity unique_ids without serial number
- [ ] Verify no "None" appears in any entity unique_id
- [ ] Verify unique_ids don't change across restarts

#### Documentation
- [ ] Add comment explaining fallback mechanism
- [ ] Document when fallback is used vs serial number
- [ ] Note that fallback changes if host/port changes
- [ ] Explain implications for entity registry

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
- [ ] `scripts/lint` passes
- [ ] `unique_id` property never returns None
- [ ] Fallback ID is deterministic
- [ ] Test with projector that doesn't provide serial number
- [ ] Test with projector that does provide serial number
- [ ] Verify entities use coordinator.unique_id correctly
- [ ] Check entity registry for stable IDs
- [ ] No "None_suffix" patterns in entity unique_ids
- [ ] Restart integration 10 times, verify IDs stable
- [ ] Change host (via reconfigure), verify new fallback generated

### Edge Cases
- [ ] What if host is hostname vs IP? (hash will differ)
- [ ] What if port changes? (hash will differ, expected)
- [ ] What if serial number becomes available later? (ID will change, potential issue)
- [ ] Document ID stability requirements in README

### Optional Enhancements
- [ ] Consider caching serial number in config entry
- [ ] Consider warning user if using fallback ID
- [ ] Add diagnostics data showing which ID type is used
- [ ] Consider supporting manual unique_id override in config

---

## Low Priority Tasks Summary

### Completion Checklist
- [ ] Task 3: Unique ID Fallback - COMPLETE

### Verification
- [ ] Unique ID mechanism robust
- [ ] No cases where unique_id returns None
- [ ] Entity unique_ids stable across restarts
- [ ] Fallback mechanism tested
- [ ] Documentation complete

### Integration with Critical Tasks
- [ ] Verify Task 8 implementation covers core requirements
- [ ] This task adds validation and edge case handling
- [ ] No conflicts with Task 8 changes

### Final Verification
- [ ] `scripts/lint` passes
- [ ] All entity unique_ids stable
- [ ] Fallback works when needed
- [ ] Serial number preferred when available
- [ ] Edge cases documented

### Release Readiness
- [ ] Low priority task completed (optional)
- [ ] Additional stability for unique_id system
- [ ] No impact if skipped for v0.0.2
- [ ] Can defer to v0.0.3 if needed
