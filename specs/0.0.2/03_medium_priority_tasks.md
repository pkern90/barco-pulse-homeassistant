# Medium Priority Tasks - Improvements

**Priority**: MEDIUM - Optional for v0.0.2 release, nice-to-have
**Total Tasks**: 2 (Tasks 1, 2)
**Estimated Effort**: 2 hours

---

## Task 1: Constants Refactor

**File**: `const.py`
**Estimated Time**: 1 hour

### Problem
- [ ] Power states use string literals instead of type-safe enums
- [ ] State comparisons prone to typos
- [ ] No centralized state groupings
- [ ] Magic strings scattered throughout codebase

### Implementation Checklist

#### const.py - Create PowerState Enum
- [ ] Import `StrEnum` from `enum`
- [ ] Create `PowerState(StrEnum)` class
- [ ] Add `ON = "on"` constant
- [ ] Add `READY = "ready"` constant
- [ ] Add `CONDITIONING = "conditioning"` constant
- [ ] Add `DECONDITIONING = "deconditioning"` constant
- [ ] Add `STANDBY = "standby"` constant
- [ ] Add `ECO = "eco"` constant
- [ ] Add `BOOT = "boot"` constant

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
- [ ] Create `ACTIVE_STATES: frozenset[PowerState]`
- [ ] Include `PowerState.ON` in active states
- [ ] Include `PowerState.READY` in active states
- [ ] Include `PowerState.CONDITIONING` in active states
- [ ] Include `PowerState.DECONDITIONING` in active states
- [ ] Create `STANDBY_STATES: frozenset[PowerState]`
- [ ] Include `PowerState.STANDBY` in standby states
- [ ] Include `PowerState.ECO` in standby states
- [ ] Include `PowerState.BOOT` in standby states

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
- [ ] Import `timedelta` from `datetime`
- [ ] Create `POLLING_INTERVALS: dict[PowerState, timedelta]`
- [ ] Map `PowerState.ON` to fast interval (2 seconds)
- [ ] Map `PowerState.READY` to fast interval
- [ ] Map `PowerState.CONDITIONING` to medium interval (5 seconds)
- [ ] Map `PowerState.DECONDITIONING` to medium interval
- [ ] Map `PowerState.STANDBY` to slow interval (30 seconds)
- [ ] Map `PowerState.ECO` to slow interval
- [ ] Map `PowerState.BOOT` to medium interval
- [ ] Add `DEFAULT_POLLING_INTERVAL` for unknown states

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
- [ ] Add `MANUFACTURER = "Barco"`
- [ ] Add `MODEL_PREFIX = "Pulse"`
- [ ] Update any existing string-based state constants

```python
MANUFACTURER = "Barco"
MODEL_PREFIX = "Pulse"
```

#### coordinator.py - Update State Comparisons
- [ ] Import `PowerState` from `.const`
- [ ] Import `ACTIVE_STATES` from `.const`
- [ ] Import `POLLING_INTERVALS` from `.const`
- [ ] Import `DEFAULT_POLLING_INTERVAL` from `.const`
- [ ] Replace `state == "on"` with `state == PowerState.ON`
- [ ] Replace `state == "ready"` with `state == PowerState.READY`
- [ ] Replace `state in ["on", "ready"]` with `state in ACTIVE_STATES`
- [ ] Update polling interval logic to use `POLLING_INTERVALS` dict
- [ ] Use `POLLING_INTERVALS.get(state, DEFAULT_POLLING_INTERVAL)`

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
- [ ] Import `PowerState` from `.const`
- [ ] Import `ACTIVE_STATES` from `.const`
- [ ] Replace string comparisons with enum comparisons
- [ ] Update `is_on` logic to use `PowerState` enum

#### switch.py - Update State Checks
- [ ] Import `PowerState` from `.const`
- [ ] Import `ACTIVE_STATES` from `.const`
- [ ] Replace string comparisons with enum comparisons

#### Other Files - Update State Comparisons
- [ ] Review `sensor.py` for string state comparisons
- [ ] Review `select.py` for string state comparisons
- [ ] Review `number.py` for string state comparisons
- [ ] Review `remote.py` for string state comparisons
- [ ] Replace all string literals with enum values

### Verification
- [ ] `scripts/lint` passes
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
- [ ] `number.py` expects `laser_min`/`laser_max` in coordinator data
- [ ] Constraints are not fetched from projector
- [ ] Hardcoded min/max values may be incorrect
- [ ] Constraints can change based on lens configuration

### Implementation Checklist

#### api.py - Add Laser Constraints Method
- [ ] Create `async def get_laser_constraints(self) -> dict[str, float]`
- [ ] Define property list: `["illumination.sources.laser.power.min", "illumination.sources.laser.power.max"]`
- [ ] Call `await self.get_properties(properties)`
- [ ] Extract min value from result dict
- [ ] Convert min to float with default 0.0
- [ ] Extract max value from result dict
- [ ] Convert max to float with default 100.0
- [ ] Return dict with "min" and "max" keys
- [ ] Add docstring explaining method purpose

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
- [ ] Locate `_get_active_properties()` method
- [ ] Find where active state properties are fetched
- [ ] Add try/except block for laser constraints
- [ ] Call `await self.device.get_laser_constraints()`
- [ ] Assign `constraints["min"]` to `data["laser_min"]`
- [ ] Assign `constraints["max"]` to `data["laser_max"]`
- [ ] Handle `BarcoStateError` in except block
- [ ] Set default `data["laser_min"] = 0.0` on error
- [ ] Set default `data["laser_max"] = 100.0` on error
- [ ] Log when constraints retrieved successfully
- [ ] Log when using default constraints

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
- [ ] Check laser power entity uses `native_min_value` property
- [ ] Verify property returns `coordinator.data.get("laser_min", 0.0)`
- [ ] Check laser power entity uses `native_max_value` property
- [ ] Verify property returns `coordinator.data.get("laser_max", 100.0)`
- [ ] Ensure constraints update when coordinator data updates
- [ ] Add logging to show when constraints change

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
- [ ] Ensure `get_laser_constraints()` can raise `BarcoStateError`
- [ ] Handle case where properties not available
- [ ] Add type conversion error handling
- [ ] Log warnings for unexpected constraint values
- [ ] Consider adding validation (min < max)

### Verification
- [ ] `scripts/lint` passes
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
- [ ] Task 1: Constants Refactor - COMPLETE
- [ ] Task 2: Dynamic Laser Power Constraints - COMPLETE

### Code Quality Improvements
- [ ] Type safety improved with enums
- [ ] No magic strings in codebase
- [ ] Polling intervals centralized
- [ ] State comparisons type-safe
- [ ] Laser constraints dynamic

### Integration Testing
- [ ] All power state transitions work correctly
- [ ] Polling intervals adjust properly
- [ ] Laser constraints fetched correctly
- [ ] Defaults used when appropriate
- [ ] No regression in functionality

### Final Verification
- [ ] All `scripts/lint` checks pass
- [ ] Type hints correct with enum usage
- [ ] No string literals for states
- [ ] Autocomplete works for power states
- [ ] Constraints update dynamically
- [ ] Test all scenarios documented

### Optional Enhancements
- [ ] Add validation: laser min < max
- [ ] Add enum for source types
- [ ] Add enum for preset/profile types
- [ ] Consider enums for other string constants
- [ ] Document constraint behavior in README

### Release Readiness
- [ ] Both medium priority tasks completed
- [ ] Code quality improved
- [ ] Type safety enhanced
- [ ] Ready to proceed with testing
