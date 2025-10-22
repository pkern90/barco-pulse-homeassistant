# v0.0.2 Implementation Overview

**Version**: 0.0.2
**Purpose**: Fix critical stability and robustness issues in v0.0.1 baseline
**Total Tasks**: 12
**Date**: October 22, 2025

---

## Quick Reference

### Task Files Organization

| File                          | Priority | Tasks               | Estimated Time | Must Fix    |
| ----------------------------- | -------- | ------------------- | -------------- | ----------- |
| `01_critical_tasks.md`        | CRITICAL | 7, 8, 9, 10, 11, 12 | 6.5 hours      | YES         |
| `02_high_priority_tasks.md`   | HIGH     | 4, 5, 11            | 6 hours        | Recommended |
| `03_medium_priority_tasks.md` | MEDIUM   | 1, 2                | 2 hours        | Optional    |
| `05_rate_limiting_task.md`    | MEDIUM   | 6                   | 1 hour         | Optional    |
| `04_low_priority_tasks.md`    | LOW      | 3                   | 30 minutes     | Optional    |

**Total Effort**:
- Critical Path: 6.5 hours
- Recommended: 13 hours
- Complete: 16 hours

---

## Implementation Strategy for AI Agents

### Phase 1: Critical Fixes (MUST DO)
**Time**: 6.5 hours | **File**: `01_critical_tasks.md`

Execute in this order:
1. **Task 8**: Coordinator unique_id (30 min) - Prevents entity corruption
2. **Task 9**: Auth cleanup (30 min) - Prevents connection leaks
3. **Task 7**: Entity error handling (2 hrs) - User-facing stability
4. **Task 10**: Input validation (2 hrs) - Prevents crashes
5. **Task 12**: Refresh error isolation (1 hr) - Command reliability
6. **Task 11**: JSON parsing (1 hr) - Performance

**Deliverable**: Stable integration that doesn't crash on errors

### Phase 2: High Priority (SHOULD DO)
**Time**: 6 hours | **File**: `02_high_priority_tasks.md`

Execute in this order:
1. **Task 4**: Connection lifecycle (3-4 hrs) - Long-term stability
2. **Task 5**: Data validation (2 hrs) - Coordinator robustness
3. **Task 11**: JSON parsing (1 hr) - If not done in Phase 1

**Deliverable**: Robust integration that recovers from errors

### Phase 3: Medium Priority (NICE TO HAVE)
**Time**: 3 hours | **Files**: `03_medium_priority_tasks.md`, `05_rate_limiting_task.md`

Execute in any order:
- **Task 1**: Constants refactor (1 hr) - Type safety
- **Task 2**: Laser constraints (1 hr) - Feature completeness
- **Task 6**: Rate limiting (1 hr) - API protection

**Deliverable**: Polished integration with best practices

### Phase 4: Low Priority (OPTIONAL)
**Time**: 30 minutes | **File**: `04_low_priority_tasks.md`

- **Task 3**: Unique ID audit (30 min) - Verification

**Deliverable**: Additional validation and documentation

---

## Task Dependencies

```
Task 8 (unique_id) → Must complete FIRST
    ↓
Task 9 (auth cleanup) → Independent
    ↓
Task 7 (error handling) → Depends on Task 12 pattern
    ↓
Task 10 (input validation) → Works with Task 7
    ↓
Task 12 (refresh errors) → Modifies Task 7 pattern
    ↓
Task 11 (JSON parsing) → Independent
    ↓
Task 4 (connection lifecycle) → Builds on Task 9
    ↓
Task 5 (data validation) → Independent
    ↓
Task 1 (constants) → Can break other tasks if done early
Task 2 (laser constraints) → Independent
Task 6 (rate limiting) → Independent
Task 3 (unique ID audit) → Depends on Task 8
```

**Recommendation**: Follow the phase order above to minimize rework.

---

## File Impact Matrix

| File               | Tasks Affecting It | Total Changes | Risk Level |
| ------------------ | ------------------ | ------------- | ---------- |
| `api.py`           | 2, 4, 5, 6, 9, 11  | ~150 lines    | HIGH       |
| `coordinator.py`   | 1, 2, 3, 4, 5, 8   | ~100 lines    | HIGH       |
| `const.py`         | 1                  | ~50 lines     | LOW        |
| `config_flow.py`   | 4                  | ~30 lines     | MEDIUM     |
| `switch.py`        | 7, 12              | ~40 lines     | MEDIUM     |
| `number.py`        | 7, 10, 12          | ~60 lines     | MEDIUM     |
| `select.py`        | 7, 10, 12          | ~50 lines     | MEDIUM     |
| `remote.py`        | 7, 10, 12          | ~50 lines     | MEDIUM     |
| `binary_sensor.py` | 1                  | ~10 lines     | LOW        |
| `sensor.py`        | 1                  | ~10 lines     | LOW        |

**High Risk Files**: Test thoroughly after changes
**Medium Risk Files**: Standard validation needed
**Low Risk Files**: Quick verification sufficient

---

## Testing Strategy

### After Each Task
- [ ] Run `scripts/lint` to ensure code quality
- [ ] Check specific task verification checklist
- [ ] Test affected functionality manually

### After Each Phase
- [ ] Run full `scripts/lint`
- [ ] Load integration in `scripts/develop`
- [ ] Verify all entities appear
- [ ] Test basic operations (power, source, settings)
- [ ] Check logs for errors/warnings

### Before Release
- [ ] Complete validation checklist in `06_testing_validation.md`
- [ ] Run integration for 24 hours
- [ ] Test all error scenarios
- [ ] Verify no resource leaks
- [ ] Update version to 0.0.2 in `manifest.json`

---

## Common Patterns for AI Agents

### Error Handling Pattern (Tasks 7, 12)
```python
from homeassistant.exceptions import HomeAssistantError

async def async_command(self, ...) -> None:
    """Execute command with error handling."""
    try:
        await self.coordinator.device.api_method(...)
    except BarcoStateError as err:
        _LOGGER.warning("Command failed - projector not ready: %s", err)
        raise HomeAssistantError(f"Projector not ready: {err}") from err
    except BarcoConnectionError as err:
        _LOGGER.error("Connection error during command: %s", err)
        raise HomeAssistantError(f"Connection error: {err}") from err
    except Exception as err:
        _LOGGER.exception("Unexpected error during command")
        raise HomeAssistantError(f"Command failed: {err}") from err

    # Refresh separately, don't fail command if refresh fails
    try:
        await self.coordinator.async_request_refresh()
    except Exception as err:
        _LOGGER.warning("Failed to refresh after command: %s", err)
```

### Input Validation Pattern (Task 10)
```python
# For number entities
async def async_set_native_value(self, value: float) -> None:
    """Set value with bounds checking."""
    if value < self.native_min_value or value > self.native_max_value:
        raise ValueError(
            f"Value {value} out of range [{self.native_min_value}, {self.native_max_value}]"
        )
    # ... then error handling pattern ...

# For select entities
async def async_select_option(self, option: str) -> None:
    """Select option with validation."""
    if option not in self.options:
        raise ValueError(f"Invalid option: {option}")
    # ... then error handling pattern ...
```

### Connection Cleanup Pattern (Tasks 4, 9)
```python
# In config_flow.py
device = BarcoDevice(...)
try:
    await device.connect()
    # ... use device ...
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

### Data Validation Pattern (Task 5)
```python
# Safe float conversion
try:
    value = float(raw_value) if raw_value is not None else None
except (ValueError, TypeError) as err:
    _LOGGER.warning("Invalid %s value: %s (%s)", key, raw_value, err)
    value = None
```

---

## Success Criteria

### Minimum (Critical Tasks Only)
- [ ] All entity unique_ids stable (no "None_suffix")
- [ ] All 12 entity commands handle errors gracefully
- [ ] All user inputs validated before API calls
- [ ] Connection cleanup on auth failures
- [ ] Commands succeed independently of refresh
- [ ] JSON parsing optimized

### Recommended (Critical + High Priority)
- [ ] Connection auto-recovery works
- [ ] No resource leaks over 24 hours
- [ ] Invalid API responses don't crash integration
- [ ] Config flow cleanup guaranteed
- [ ] Coordinator handles all error types

### Complete (All Tasks)
- [ ] Type-safe power state enums
- [ ] Dynamic laser power constraints
- [ ] API rate limiting prevents flooding
- [ ] Unique ID fallback validated
- [ ] All verification checklists passed

---

## Rollback Plan

If critical issues arise during implementation:

1. **After each task**: Git commit with message "Task X: [description]"
2. **If task breaks integration**: `git revert HEAD`
3. **If multiple tasks fail**: `git reset --hard <last-good-commit>`
4. **Emergency**: Restore from v0.0.1 baseline

**Critical commits to tag**:
- Before starting: `git tag v0.0.1-baseline`
- After critical tasks: `git tag v0.0.2-critical`
- After high priority: `git tag v0.0.2-stable`
- Final release: `git tag v0.0.2`

---

## Resources

### Specification Files
- `/specs/ARCHITECTURE.md` - Integration architecture and patterns
- `/specs/BARCO_HDR_CS_PROTOCOL.md` - Protocol details
- `/specs/barco_pulse_api_json_rpc_reference_summary.md` - API quick reference
- `/specs/HDR_CS_STATE_DEPENDENT_PROPERTIES.md` - State dependencies

### Development Tools
- `scripts/develop` - Run integration in test environment
- `scripts/lint` - Check code quality with ruff
- `scripts/setup` - Initial environment setup

### Home Assistant Documentation
- Entity error handling: https://developers.home-assistant.io/docs/core/entity#raising-exceptions
- Coordinator pattern: https://developers.home-assistant.io/docs/integration_fetching_data
- Config flow: https://developers.home-assistant.io/docs/config_entries_config_flow_handler

---

## Notes for AI Agents

1. **Always check Task 8 first** - It's the foundation for entity stability
2. **Follow the error handling pattern exactly** - Consistent patterns prevent bugs
3. **Don't skip validation checklists** - They catch edge cases
4. **Test after each task** - Don't accumulate untested changes
5. **Use provided code patterns** - They're tested and follow HA conventions
6. **Read file context before editing** - Understand surrounding code
7. **Preserve existing functionality** - Only change what's needed
8. **Log appropriately** - Warning for expected issues, Error for problems
9. **Handle cleanup in finally blocks** - Prevent resource leaks
10. **Never return None for unique_id** - Causes permanent entity corruption

### Common Pitfalls to Avoid
- ❌ Editing multiple files in parallel without testing
- ❌ Changing unique_id construction after entities registered
- ❌ Skipping input validation "because API validates"
- ❌ Not wrapping cleanup code in try/except
- ❌ Using bare except clauses
- ❌ Logging errors without re-raising exceptions
- ❌ Assuming API responses are always valid
- ❌ Forgetting to update both switch on/off methods
- ❌ Not testing error paths (only happy path)
- ❌ Deploying without running scripts/lint

### When Stuck
1. Check the specific task file for detailed instructions
2. Review the error handling/validation patterns above
3. Look at similar implementations in other files
4. Check Home Assistant developer docs
5. Verify file has all required imports
6. Test the specific scenario causing issues
7. Check logs for detailed error messages
8. Ensure prerequisites (earlier tasks) are complete

---

## Quick Start for AI Agents

```bash
# 1. Understand the baseline
cat specs/IMPLEMENTATION_PLAN_0.0.2.md

# 2. Start with critical tasks
cat specs/0.0.2/01_critical_tasks.md

# 3. Implement Task 8 first
# Edit custom_components/barco_pulse/coordinator.py
# Follow checklist in 01_critical_tasks.md

# 4. Test after each change
scripts/lint
scripts/develop

# 5. Move to next task when verification passes
# Repeat until phase complete
```

**Remember**: Quality over speed. A working v0.0.2 with only critical tasks is better than a broken implementation with all tasks.
