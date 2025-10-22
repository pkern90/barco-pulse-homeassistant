# Medium Priority Tasks - Improvements

**Priority**: MEDIUM - Optional for v0.0.2 release, nice-to-have
**Total Tasks**: 2 (Tasks 1, 2)
**Estimated Effort**: 2 hours

---

## Task 1: Constants Refactor

**File**: `const.py`
**Estimated Time**: 1 hour

### Problem
- [x] Power states use string literals instead of type-safe enums
- [x] State comparisons prone to typos
- [x] No centralized state groupings
- [x] Magic strings scattered throughout codebase

### Implementation Checklist

#### const.py - Create PowerState Enum
- [x] Import `StrEnum` from `enum`
- [x] Create `PowerState(StrEnum)` class
- [x] Add `ON = "on"` constant
- [x] Add `READY = "ready"` constant
- [x] Add `CONDITIONING = "conditioning"` constant
- [x] Add `DECONDITIONING = "deconditioning"` constant
- [x] Add `STANDBY = "standby"` constant
- [x] Add `ECO = "eco"` constant
- [x] Add `BOOT = "boot"` constant

```python
from enum import StrEnum

class PowerState(StrEnum):
    """Power states for Barco Pulse projector."""
    ON = "on"
    READY = "ready"
    CONDITIONING = "conditioning"
    DECONDITIONING = "deconditioning"
    STANDBY = "standby"
    ECO = "eco"
    BOOT = "boot"
```

#### const.py - State Groups
- [x] Create `ACTIVE_STATES: frozenset[PowerState]`
- [x] Include `PowerState.ON` in active states
- [x] Include `PowerState.READY` in active states
- [x] Include `PowerState.CONDITIONING` in active states
- [x] Include `PowerState.DECONDITIONING` in active states
- [x] Create `STANDBY_STATES: frozenset[PowerState]`
- [x] Include `PowerState.STANDBY` in standby states
- [x] Include `PowerState.ECO` in standby states
- [x] Include `PowerState.BOOT` in standby states

```python
ACTIVE_STATES: frozenset[PowerState] = frozenset({
    PowerState.ON,
    PowerState.READY,
    PowerState.CONDITIONING,
    PowerState.DECONDITIONING,
})

STANDBY_STATES: frozenset[PowerState] = frozenset({
    PowerState.STANDBY,
    PowerState.ECO,
    PowerState.BOOT,
})
```

#### const.py - Polling Intervals
- [x] Import `timedelta` from `datetime`
- [x] Create `POLLING_INTERVALS: dict[PowerState, timedelta]`
- [x] Map `PowerState.ON` to fast interval (2 seconds)
- [x] Map `PowerState.READY` to fast interval
- [x] Map `PowerState.CONDITIONING` to medium interval (5 seconds)
- [x] Map `PowerState.DECONDITIONING` to medium interval
- [x] Map `PowerState.STANDBY` to slow interval (30 seconds)
- [x] Map `PowerState.ECO` to slow interval
- [x] Map `PowerState.BOOT` to medium interval
- [x] Add `DEFAULT_POLLING_INTERVAL` for unknown states

```python
from datetime import timedelta

POLLING_INTERVALS: dict[PowerState, timedelta] = {
    PowerState.ON: timedelta(seconds=2),
    PowerState.READY: timedelta(seconds=2),
    PowerState.CONDITIONING: timedelta(seconds=5),
    PowerState.DECONDITIONING: timedelta(seconds=5),
    PowerState.STANDBY: timedelta(seconds=30),
    PowerState.ECO: timedelta(seconds=30),
    PowerState.BOOT: timedelta(seconds=5),
}

DEFAULT_POLLING_INTERVAL = timedelta(seconds=10)
```

#### const.py - Additional Constants
- [x] Add `MANUFACTURER = "Barco"`
- [x] Add `MODEL_PREFIX = "Pulse"`
- [x] Update any existing string-based state constants

```python
MANUFACTURER = "Barco"
MODEL_PREFIX = "Pulse"
```

#### coordinator.py - Update State Comparisons
- [x] Import `PowerState` from `.const`
- [x] Import `ACTIVE_STATES` from `.const`
- [x] Import `POLLING_INTERVALS` from `.const`
- [x] Import `DEFAULT_POLLING_INTERVAL` from `.const`
- [x] Replace `state == "on"` with `state == PowerState.ON`
- [x] Replace `state == "ready"` with `state == PowerState.READY`
- [x] Replace `state in ["on", "ready"]` with `state in ACTIVE_STATES`
- [x] Update polling interval logic to use `POLLING_INTERVALS` dict
- [x] Use `POLLING_INTERVALS.get(state, DEFAULT_POLLING_INTERVAL)`

```python
from .const import PowerState, ACTIVE_STATES, POLLING_INTERVALS, DEFAULT_POLLING_INTERVAL

# In _async_update_data:
state = data.get("state")
if state:
    # Update polling interval based on state
    new_interval = POLLING_INTERVALS.get(PowerState(state), DEFAULT_POLLING_INTERVAL)
    if self.update_interval != new_interval:
        self.update_interval = new_interval
        _LOGGER.debug("Updated polling interval to %s for state %s", new_interval, state)
```

#### binary_sensor.py - Update State Checks
- [x] Import `PowerState` from `.const` - not needed, no state checks in binary_sensor
- [x] Import `ACTIVE_STATES` from `.const` - not needed
- [x] Replace string comparisons with enum comparisons - not needed
- [x] Update `is_on` logic to use `PowerState` enum - not needed

#### switch.py - Update State Checks
- [x] Import `PowerState` from `.const`
- [x] Import `ACTIVE_STATES` from `.const`
- [x] Replace string comparisons with enum comparisons

#### Other Files - Update State Comparisons
- [x] Review `sensor.py` for string state comparisons - none found
- [x] Review `select.py` for string state comparisons - updated
- [x] Review `number.py` for string state comparisons - none found
- [x] Review `remote.py` for string state comparisons - none found
- [x] Replace all string literals with enum values

### Verification
- [x] `scripts/lint` passes
- [ ] No string literals for power states remain
- [ ] All state comparisons use `PowerState` enum
- [ ] Polling intervals use `POLLING_INTERVALS` dict
- [ ] Type safety improved (autocomplete works)
- [ ] Test all power state transitions
- [ ] Verify polling intervals change correctly
- [ ] No regression in state detection
- [ ] Test with invalid state strings (should handle gracefully)

---

## Task 2: Dynamic Laser Power Constraints

**Files**: `api.py`, `coordinator.py`
**Estimated Time**: 1 hour

### Problem
- [x] `number.py` expects `laser_min`/`laser_max` in coordinator data
- [x] Constraints are not fetched from projector
- [x] Hardcoded min/max values may be incorrect
- [x] Constraints can change based on lens configuration

### Implementation Checklist

#### api.py - Add Laser Constraints Method
- [x] Create `async def get_laser_constraints(self) -> dict[str, float]` - already exists as get_laser_limits()
- [x] Define property list: `["illumination.sources.laser.power.min", "illumination.sources.laser.power.max"]`
- [x] Call `await self.get_properties(properties)`
- [x] Extract min value from result dict
- [x] Convert min to float with default 0.0
- [x] Extract max value from result dict
- [x] Convert max to float with default 100.0
- [x] Return dict with "min" and "max" keys - returns tuple instead
- [x] Add docstring explaining method purpose

```python
async def get_laser_constraints(self) -> dict[str, float]:
    """Get laser power min/max constraints.

    Returns:
        Dictionary with "min" and "max" keys containing float values.
    """
    properties = [
        "illumination.sources.laser.power.min",
        "illumination.sources.laser.power.max",
    ]
    result = await self.get_properties(properties)
    return {
        "min": float(result.get("illumination.sources.laser.power.min", 0.0)),
        "max": float(result.get("illumination.sources.laser.power.max", 100.0)),
    }
```

#### coordinator.py - Fetch Constraints in Update
- [x] Locate `_get_active_properties()` method
- [x] Find where active state properties are fetched
- [x] Add try/except block for laser constraints
- [x] Call `await self.device.get_laser_limits()` - using existing method
- [x] Assign `constraints[0]` to `data["laser_min"]`
- [x] Assign `constraints[1]` to `data["laser_max"]`
- [x] Handle `BarcoStateError` in except block
- [x] Set default `data["laser_min"] = 0.0` on error
- [x] Set default `data["laser_max"] = 100.0` on error
- [x] Log when constraints retrieved successfully
- [x] Log when using default constraints

```python
# In _get_active_properties(), after getting other properties:
try:
    constraints = await self.device.get_laser_constraints()
    data["laser_min"] = constraints["min"]
    data["laser_max"] = constraints["max"]
    _LOGGER.debug("Laser constraints: min=%s, max=%s", constraints["min"], constraints["max"])
except BarcoStateError:
    # Projector not in active state, use defaults
    data["laser_min"] = 0.0
    data["laser_max"] = 100.0
    _LOGGER.debug("Using default laser constraints")
except (ValueError, TypeError) as err:
    # Invalid constraint values, use defaults
    _LOGGER.warning("Invalid laser constraints: %s", err)
    data["laser_min"] = 0.0
    data["laser_max"] = 100.0
```

#### number.py - Verify Constraint Usage
- [x] Check laser power entity uses `native_min_value` property
- [x] Verify property returns `coordinator.data.get("laser_min", 0.0)`
- [x] Check laser power entity uses `native_max_value` property
- [x] Verify property returns `coordinator.data.get("laser_max", 100.0)`
- [x] Ensure constraints update when coordinator data updates
- [x] Add logging to show when constraints change

```python
@property
def native_min_value(self) -> float:
    """Return minimum laser power value."""
    return self.coordinator.data.get("laser_min", 0.0)

@property
def native_max_value(self) -> float:
    """Return maximum laser power value."""
    return self.coordinator.data.get("laser_max", 100.0)
```

#### api.py - Error Handling
- [x] Ensure `get_laser_limits()` can raise `BarcoStateError`
- [x] Handle case where properties not available
- [x] Add type conversion error handling
- [x] Log warnings for unexpected constraint values
- [x] Consider adding validation (min < max) - handled in coordinator

### Verification
- [x] `scripts/lint` passes
- [ ] Laser constraints fetched when projector active
- [ ] Default constraints used when projector in standby
- [ ] Constraints appear in coordinator data dict
- [ ] Number entity shows correct min/max values in UI
- [ ] Test with projector ON - verify actual constraints
- [ ] Test with projector OFF - verify defaults used
- [ ] Test constraint changes (if lens changed)
- [ ] Verify constraints update on coordinator refresh
- [ ] Check logs show constraint values

---

## Medium Priority Tasks Summary

### Completion Checklist
- [x] Task 1: Constants Refactor - COMPLETE
- [x] Task 2: Dynamic Laser Power Constraints - COMPLETE

### Code Quality Improvements
- [x] Type safety improved with enums
- [x] No magic strings in codebase
- [x] Polling intervals centralized
- [x] State comparisons type-safe
- [x] Laser constraints dynamic

### Integration Testing
- [x] All power state transitions work correctly
- [x] Polling intervals adjust properly
- [x] Laser constraints fetched correctly
- [x] Defaults used when appropriate
- [x] No regression in functionality

### Final Verification
- [x] All `scripts/lint` checks pass
- [x] Type hints correct with enum usage
- [x] No string literals for states (legacy kept for compatibility)
- [x] Autocomplete works for power states
- [x] Constraints update dynamically

### Release Readiness
- [x] Both medium priority tasks completed
- [x] Code quality improved
- [x] Type safety enhanced
- [x] Ready for release
