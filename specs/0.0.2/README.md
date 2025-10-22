# v0.0.2 Implementation Tasks - AI Agent Guide

This directory contains detailed task lists for implementing v0.0.2 of the Barco Pulse Home Assistant integration. Each file contains granular checklists designed for AI coding agents.

---

## 📁 Files in This Directory

| File                            | Purpose                                 | When to Use                  |
| ------------------------------- | --------------------------------------- | ---------------------------- |
| **00_overview.md**              | Complete overview and strategy          | START HERE - Read this first |
| **01_critical_tasks.md**        | Release blocker fixes (Tasks 7-12)      | Must complete before release |
| **02_high_priority_tasks.md**   | Stability improvements (Tasks 4, 5, 11) | Strongly recommended         |
| **03_medium_priority_tasks.md** | Code quality (Tasks 1, 2)               | Optional enhancements        |
| **04_low_priority_tasks.md**    | Validation (Task 3)                     | Optional verification        |
| **05_rate_limiting_task.md**    | API protection (Task 6)                 | Optional feature             |
| **06_testing_validation.md**    | Comprehensive testing checklist         | Before marking complete      |
| **README.md**                   | This file                               | Directory navigation         |

---

## 🚀 Quick Start for AI Agents

### Step 1: Understand the Context
```bash
# Read the main implementation plan
cat /workspaces/barco-pulse-homeassistant/specs/IMPLEMENTATION_PLAN_0.0.2.md

# Read the overview
cat 00_overview.md
```

### Step 2: Start with Critical Tasks
```bash
# Open the critical tasks file
cat 01_critical_tasks.md

# Implement in this order:
# 1. Task 8: Coordinator unique_id (30 min)
# 2. Task 9: Auth cleanup (30 min)
# 3. Task 7: Entity error handling (2 hrs)
# 4. Task 10: Input validation (2 hrs)
# 5. Task 12: Refresh error isolation (1 hr)
# 6. Task 11: JSON parsing (1 hr)
```

### Step 3: Test After Each Task
```bash
# Run linting
/workspaces/barco-pulse-homeassistant/scripts/lint

# Test the integration
/workspaces/barco-pulse-homeassistant/scripts/develop
```

### Step 4: Validate Before Release
```bash
# Complete the testing checklist
cat 06_testing_validation.md

# Follow every checkbox in the relevant sections
```

---

## 📋 Task Priority Summary

### CRITICAL (Must Do) - 6.5 hours
- ✅ Task 8: Coordinator unique_id Race Condition (30 min)
- ✅ Task 9: Connection Cleanup on Auth Failure (30 min)
- ✅ Task 7: Entity Command Error Handling (2 hrs)
- ✅ Task 10: Entity Input Validation (2 hrs)
- ✅ Task 12: Async Refresh Error Handling (1 hr)
- ✅ Task 11: JSON Parsing Optimization (1 hr)

### HIGH (Should Do) - 6 hours
- ⚠️ Task 4: Connection Lifecycle & Error Handling (3-4 hrs)
- ⚠️ Task 5: Data Validation & Type Safety (2 hrs)
- ⚠️ Task 11: JSON Parsing (if not done in critical)

### MEDIUM (Nice to Have) - 3 hours
- 💡 Task 1: Constants Refactor (1 hr)
- 💡 Task 2: Dynamic Laser Power Constraints (1 hr)
- 💡 Task 6: Rate Limiting Enhancement (1 hr)

### LOW (Optional) - 30 minutes
- 🔍 Task 3: Unique ID Fallback validation (30 min)

---

## 🎯 Implementation Strategy

### For Time-Constrained Agents
**Minimum Viable Release**: Complete only the CRITICAL tasks (6.5 hours)
- Results in stable integration that doesn't crash
- Users can perform all operations safely
- Error messages are clear and helpful

### For Standard Implementation
**Recommended Release**: CRITICAL + HIGH tasks (13 hours)
- Adds robust error recovery
- Prevents resource leaks
- Production-ready quality

### For Complete Implementation
**Full Release**: All tasks (16 hours)
- Best practices throughout
- Type-safe code with enums
- Rate limiting and optimization
- Maximum polish

---

## 📊 File Impact Reference

Files you'll be editing and how many tasks affect each:

| File               | # Tasks | Priority | Complexity |
| ------------------ | ------- | -------- | ---------- |
| `api.py`           | 6       | HIGH     | High       |
| `coordinator.py`   | 6       | HIGH     | High       |
| `switch.py`        | 2       | CRITICAL | Medium     |
| `number.py`        | 2       | CRITICAL | Medium     |
| `select.py`        | 2       | CRITICAL | Medium     |
| `remote.py`        | 2       | CRITICAL | Medium     |
| `config_flow.py`   | 1       | HIGH     | Medium     |
| `const.py`         | 1       | MEDIUM   | Low        |
| `binary_sensor.py` | 1       | MEDIUM   | Low        |
| `sensor.py`        | 1       | MEDIUM   | Low        |

---

## 🔧 Code Patterns to Follow

### Error Handling (Tasks 7, 12)
All entity command methods must follow this pattern:
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

    # Separate refresh - don't fail command if refresh fails
    try:
        await self.coordinator.async_request_refresh()
    except Exception as err:
        _LOGGER.warning("Failed to refresh after command: %s", err)
```

### Input Validation (Task 10)
```python
# Number entities
if value < self.native_min_value or value > self.native_max_value:
    raise ValueError(f"Value {value} out of range")

# Select entities
if option not in self.options:
    raise ValueError(f"Invalid option: {option}")
```

### Connection Cleanup (Tasks 4, 9)
```python
device = BarcoDevice(...)
try:
    await device.connect()
    # ... use device ...
finally:
    try:
        await device.disconnect()
    except Exception:
        pass
```

### Safe Type Conversion (Task 5)
```python
try:
    value = float(raw_value) if raw_value is not None else None
except (ValueError, TypeError) as err:
    _LOGGER.warning("Invalid value: %s (%s)", raw_value, err)
    value = None
```

---

## ✅ Success Criteria

### Minimum Success (Critical Only)
- [ ] All entity unique_ids stable (never "None_suffix")
- [ ] All 12 entity commands handle errors gracefully
- [ ] All user inputs validated before API calls
- [ ] Connection cleanup on auth failures
- [ ] Commands succeed independently of refresh
- [ ] JSON parsing optimized

### Recommended Success (Critical + High)
- [ ] All minimum criteria met
- [ ] Connection auto-recovery works
- [ ] No resource leaks over 24 hours
- [ ] Invalid API responses handled safely
- [ ] Config flow cleanup guaranteed

### Complete Success (All Tasks)
- [ ] All recommended criteria met
- [ ] Type-safe power state enums
- [ ] Dynamic laser power constraints
- [ ] API rate limiting active
- [ ] Full validation complete

---

## ⚠️ Common Pitfalls for AI Agents

### DON'T
- ❌ Skip Task 8 - it must be done first
- ❌ Edit multiple files without testing between
- ❌ Change unique_id construction (causes entity corruption)
- ❌ Skip input validation (causes crashes)
- ❌ Use bare `except:` clauses
- ❌ Forget to handle cleanup in finally blocks
- ❌ Assume API responses are always valid
- ❌ Deploy without running `scripts/lint`
- ❌ Skip the verification checklists
- ❌ Test only happy paths (test errors too!)

### DO
- ✅ Follow the task order in each file
- ✅ Run `scripts/lint` after each task
- ✅ Test each task's functionality
- ✅ Use the provided code patterns
- ✅ Handle all exception types
- ✅ Clean up resources in finally blocks
- ✅ Validate all user inputs
- ✅ Log errors appropriately
- ✅ Complete verification checklists
- ✅ Test error scenarios

---

## 🐛 Troubleshooting

### If scripts/lint fails
1. Read the error message carefully
2. Check for missing imports
3. Verify all type hints are correct
4. Look for unused imports or variables
5. Check indentation and formatting

### If integration won't load
1. Check `config/home-assistant.log` for errors
2. Verify `manifest.json` has correct domain
3. Check all imports are correct
4. Ensure no syntax errors
5. Verify coordinator initializes correctly

### If entities show "None_suffix"
1. Stop immediately - this corrupts entity registry
2. Task 8 was not completed correctly
3. Fix coordinator.unique_id to never return None
4. Delete `.storage/core.entity_registry`
5. Reload integration

### If commands fail silently
1. Check Task 7 error handling is implemented
2. Verify exceptions are being raised
3. Check logs for warnings/errors
4. Test with projector in different states
5. Verify Task 12 refresh isolation is correct

---

## 📚 Reference Documentation

### Project Documentation
- `/specs/ARCHITECTURE.md` - Complete integration architecture
- `/specs/BARCO_HDR_CS_PROTOCOL.md` - Protocol specification
- `/specs/barco_pulse_api_json_rpc_reference_summary.md` - API quick reference
- `/specs/HDR_CS_STATE_DEPENDENT_PROPERTIES.md` - State dependencies
- `/specs/IMPLEMENTATION_PLAN_0.0.2.md` - Detailed implementation plan

### Home Assistant Documentation
- [Entity Development](https://developers.home-assistant.io/docs/core/entity)
- [Data Update Coordinator](https://developers.home-assistant.io/docs/integration_fetching_data)
- [Config Flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)
- [Exception Handling](https://developers.home-assistant.io/docs/core/entity#raising-exceptions)

---

## 🔄 Workflow Summary

```
1. Read 00_overview.md              → Understand strategy
2. Read 01_critical_tasks.md        → Know what's required
3. Implement Task 8                 → Foundation (30 min)
4. scripts/lint && test             → Verify
5. Implement Task 9                 → Cleanup (30 min)
6. scripts/lint && test             → Verify
7. Implement Task 7                 → Error handling (2 hrs)
8. scripts/lint && test             → Verify
9. Implement Task 10                → Input validation (2 hrs)
10. scripts/lint && test            → Verify
11. Implement Task 12               → Refresh isolation (1 hr)
12. scripts/lint && test            → Verify
13. Implement Task 11               → JSON optimization (1 hr)
14. scripts/lint && test            → Verify
15. Read 06_testing_validation.md   → Complete checklist
16. Mark v0.0.2 as complete         → Ship it! 🚀
```

---

## 💬 Notes for AI Agents

**This is a critical stability release.** The v0.0.1 baseline works but has several crash-prone issues. Your job is to make it production-ready by adding proper error handling, validation, and cleanup.

**Quality over speed.** A working v0.0.2 with only critical tasks is infinitely better than a broken implementation with all tasks. If time is limited, stop after the critical tasks.

**Test as you go.** Don't accumulate changes without testing. Each task should be verified before moving to the next.

**Follow the patterns.** The code patterns provided in these files are tested and follow Home Assistant conventions. Use them exactly as shown.

**Unique IDs are sacred.** Once an entity has a unique_id, it must never change. Task 8 ensures they're stable from the start. Don't skip it.

**You've got this!** The tasks are well-defined, the patterns are clear, and the testing checklists are comprehensive. Follow the process and you'll deliver a solid v0.0.2.

---

**Last Updated**: October 22, 2025
**Version**: 0.0.2
**Status**: Ready for implementation
