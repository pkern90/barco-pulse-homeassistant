# Testing & Validation Checklist

**Version**: 0.0.2
**Purpose**: Comprehensive testing checklist for AI coding agents
**Use**: Complete before marking v0.0.2 as release-ready

---

## Pre-Release Validation

### Code Quality Checks

#### Linting & Formatting
- [ ] `scripts/lint` passes with zero errors
- [ ] `scripts/lint` passes with zero warnings
- [ ] All files have proper imports
- [ ] All functions have type hints
- [ ] All classes have docstrings
- [ ] All public methods have docstrings
- [ ] No unused imports remain
- [ ] No commented-out code blocks
- [ ] No debug print statements
- [ ] No TODO comments for critical issues

#### Code Patterns
- [ ] All async functions use `async def`
- [ ] All I/O operations are async
- [ ] No blocking calls in async context
- [ ] All exceptions inherit from base exception classes
- [ ] All error handling uses proper exception types
- [ ] All resources cleaned up in finally blocks
- [ ] All locks properly acquired and released

#### Type Safety
- [ ] All function parameters have type hints
- [ ] All return types specified
- [ ] All class attributes type-hinted
- [ ] No use of `Any` where specific type possible
- [ ] PowerState enum used (if Task 1 complete)
- [ ] No string literals for power states (if Task 1 complete)

---

## Critical Tasks Verification

### Task 7: Entity Command Error Handling

#### switch.py
- [ ] `async_turn_on` has try/except block
- [ ] `async_turn_on` handles BarcoStateError
- [ ] `async_turn_on` handles BarcoConnectionError
- [ ] `async_turn_on` handles generic Exception
- [ ] `async_turn_on` raises HomeAssistantError
- [ ] `async_turn_off` has try/except block
- [ ] `async_turn_off` handles all error types
- [ ] `async_turn_off` raises HomeAssistantError

#### number.py (5 entities)
- [ ] Laser power `async_set_native_value` has error handling
- [ ] Brightness `async_set_native_value` has error handling
- [ ] Contrast `async_set_native_value` has error handling
- [ ] Saturation `async_set_native_value` has error handling
- [ ] Hue `async_set_native_value` has error handling
- [ ] All handle BarcoStateError
- [ ] All handle BarcoConnectionError
- [ ] All handle generic Exception
- [ ] All raise HomeAssistantError

#### select.py (3 entities)
- [ ] Source `async_select_option` has error handling
- [ ] Preset `async_select_option` has error handling
- [ ] Profile `async_select_option` has error handling
- [ ] All handle BarcoStateError
- [ ] All handle BarcoConnectionError
- [ ] All handle generic Exception
- [ ] All raise HomeAssistantError

#### remote.py
- [ ] `async_turn_on` has error handling
- [ ] `async_turn_off` has error handling
- [ ] `async_send_command` has error handling
- [ ] All handle all error types
- [ ] All raise HomeAssistantError

### Task 8: Coordinator unique_id Race Condition
- [ ] `_fallback_id` created in `__init__`
- [ ] Fallback uses md5 hash of host:port
- [ ] Hash truncated to 16 characters
- [ ] `unique_id` property never returns None
- [ ] `unique_id` returns serial if available
- [ ] `unique_id` returns fallback if serial unavailable
- [ ] Property has docstring

### Task 9: Connection Cleanup on Auth Failure
- [ ] `connect()` wraps auth in try/except
- [ ] Auth failure calls `disconnect()`
- [ ] BarcoAuthError re-raised after cleanup
- [ ] Connection state reset on auth failure
- [ ] No resource leak on auth failure

### Task 10: Entity Input Validation

#### number.py
- [ ] All 5 entities validate bounds
- [ ] Bounds checked against native_min_value/max_value
- [ ] ValueError raised for out-of-range
- [ ] Error messages are descriptive

#### select.py
- [ ] All 3 entities validate options
- [ ] Options checked against self.options
- [ ] ValueError raised for invalid option
- [ ] Error messages are descriptive

#### remote.py
- [ ] Commands validated before processing
- [ ] Preset numbers validated as integers
- [ ] Preset range validated (1-30)
- [ ] Invalid commands handled gracefully

### Task 11: JSON Parsing Optimization
- [ ] `_read_json_response()` parses in loop
- [ ] Returns immediately on successful parse
- [ ] Continues reading only on JSONDecodeError
- [ ] Max buffer size check still present
- [ ] Timeout handling still works
- [ ] UnicodeDecodeError handling still works

### Task 12: Async Refresh Error Handling
- [ ] All 12 entity commands separate refresh try/except
- [ ] API command success not dependent on refresh
- [ ] Refresh failures logged as warnings
- [ ] Refresh failures don't raise to user
- [ ] Command completion status accurate

---

## High Priority Tasks Verification

### Task 4: Connection Lifecycle & Error Handling

#### api.py
- [ ] `_ensure_connected()` method exists
- [ ] Checks if writer is closing
- [ ] Resets connection state if stale
- [ ] `_send_request()` calls `_ensure_connected()`
- [ ] Connection errors reset state
- [ ] Connection errors clean up reader/writer
- [ ] Writer closed in except block with try/except

#### coordinator.py
- [ ] `_async_update_data()` handles BarcoAuthError
- [ ] Raises ConfigEntryAuthFailed for auth errors
- [ ] Handles BarcoConnectionError
- [ ] Calls `disconnect()` on connection errors
- [ ] Disconnect wrapped in try/except
- [ ] Handles generic exceptions
- [ ] Calls `disconnect()` on generic errors

#### config_flow.py
- [ ] Device creation in try/finally
- [ ] Connection attempt in try block
- [ ] BarcoConnectionError handled
- [ ] BarcoAuthError handled
- [ ] Disconnect in finally block
- [ ] Disconnect wrapped in try/except
- [ ] Pattern applied to both step_user and step_reconfigure

### Task 5: Data Validation & Type Safety

#### coordinator.py
- [ ] Response type validated (isinstance dict)
- [ ] Warning logged for invalid type
- [ ] All float conversions wrapped in try/except
- [ ] ValueError caught and handled
- [ ] TypeError caught and handled
- [ ] Conversion errors logged with context
- [ ] Invalid values set to None
- [ ] Pattern applied to all 6 float fields
- [ ] Integer conversions validated
- [ ] String values checked before use

---

## Medium Priority Tasks Verification

### Task 1: Constants Refactor (if completed)
- [ ] PowerState enum defined
- [ ] All 7 states in enum (ON, READY, etc.)
- [ ] ACTIVE_STATES frozenset defined
- [ ] STANDBY_STATES frozenset defined
- [ ] POLLING_INTERVALS dict defined
- [ ] MANUFACTURER constant added
- [ ] MODEL_PREFIX constant added
- [ ] coordinator.py imports PowerState
- [ ] All state comparisons use enum
- [ ] Polling interval logic uses dict
- [ ] No string literals for states remain

### Task 2: Dynamic Laser Power Constraints (if completed)
- [ ] `get_laser_constraints()` method in api.py
- [ ] Method returns dict with min/max
- [ ] Method has docstring
- [ ] Coordinator calls method in `_get_active_properties()`
- [ ] Constraints stored in data dict
- [ ] BarcoStateError handled with defaults
- [ ] ValueError/TypeError handled
- [ ] number.py uses dynamic constraints
- [ ] native_min_value returns coordinator data
- [ ] native_max_value returns coordinator data

### Task 6: Rate Limiting Enhancement (if completed)
- [ ] `_last_request_time` field added
- [ ] `_min_request_interval` constant defined
- [ ] Rate limiting in `_send_request()`
- [ ] Elapsed time calculated
- [ ] Sleep if too soon
- [ ] Last request time updated
- [ ] Rate limiting inside lock
- [ ] Debug logging for rate limiting

### Task 3: Unique ID Fallback (if completed)
- [ ] Task 8 implementation verified
- [ ] Additional logging added
- [ ] Docstring explains fallback
- [ ] All entity unique_id usage audited
- [ ] No entities use entry_id in unique_id
- [ ] Documentation added

---

## Functional Testing

### Integration Loading
- [ ] Run `scripts/develop` successfully
- [ ] Integration loads without errors
- [ ] No exceptions in home-assistant.log
- [ ] Config entry created successfully
- [ ] Device appears in device registry

### Entity Verification
- [ ] All 17+ entities appear in UI
- [ ] Binary sensor: Power state appears
- [ ] Sensor: State, source, preset, profile appear
- [ ] Switch: Power switch appears
- [ ] Number: Laser power, brightness, contrast, saturation, hue appear
- [ ] Select: Source, preset, profile appear
- [ ] Remote: Remote entity appears
- [ ] All entity unique_ids stable (check entity registry)
- [ ] No "None_suffix" in any unique_id
- [ ] All entity names correct
- [ ] All entity icons appropriate

### Power Control
- [ ] Power switch turns projector on
- [ ] Power switch turns projector off
- [ ] Remote turn_on command works
- [ ] Remote turn_off command works
- [ ] Power state sensor updates
- [ ] Binary sensor reflects power state
- [ ] Polling interval changes with power state

### Source Selection
- [ ] Source select shows available sources
- [ ] Selecting source changes input
- [ ] Current source sensor updates
- [ ] Invalid source shows error to user

### Preset/Profile Management
- [ ] Preset select shows presets
- [ ] Selecting preset switches preset
- [ ] Current preset sensor updates
- [ ] Profile select shows profiles
- [ ] Selecting profile switches profile
- [ ] Current profile sensor updates

### Picture Controls
- [ ] Laser power slider appears
- [ ] Laser power changes value
- [ ] Laser power shows correct min/max
- [ ] Brightness slider works
- [ ] Contrast slider works
- [ ] Saturation slider works
- [ ] Hue slider works
- [ ] All number entities validate bounds

### Remote Commands
- [ ] Remote sends preset commands
- [ ] Format "preset_<number>" works
- [ ] Invalid formats show error
- [ ] Out-of-range presets rejected

---

## Error Handling Testing

### Projector Off Scenarios
- [ ] Trying to change source shows appropriate error
- [ ] Trying to adjust laser power shows error
- [ ] Trying to change picture settings shows error
- [ ] Errors are user-friendly (not stack traces)
- [ ] Integration remains stable after errors

### Network Issues
- [ ] Disconnect network during operation
- [ ] Coordinator marks unavailable
- [ ] Connection auto-recovers when network returns
- [ ] No resource leaks after disconnection
- [ ] All entities become available again

### Invalid Input Testing
- [ ] Number entity with value below min rejected
- [ ] Number entity with value above max rejected
- [ ] Select entity with invalid option rejected
- [ ] Remote with invalid command handled
- [ ] All show appropriate error messages

### Authentication Errors
- [ ] Invalid auth code during setup shows error
- [ ] Auth error during operation triggers reauth
- [ ] Connection cleaned up on auth failure
- [ ] Config flow shows correct error message

### API Errors
- [ ] Malformed API response doesn't crash
- [ ] Missing properties handled gracefully
- [ ] Wrong type values don't cause ValueError
- [ ] Incomplete JSON handled correctly
- [ ] Timeout handled appropriately

---

## Stability Testing

### Resource Leak Detection
- [ ] Run integration for 24 hours
- [ ] Monitor memory usage (should be stable)
- [ ] Check open file descriptors (should not grow)
- [ ] Check open network connections (should be 1 or 0)
- [ ] No errors in logs over time
- [ ] CPU usage remains low

### Repeated Operations
- [ ] Toggle power 100 times - no issues
- [ ] Change source 50 times - no issues
- [ ] Adjust laser power 50 times - no issues
- [ ] Reload integration 20 times - entities stable
- [ ] Restart Home Assistant - integration loads cleanly

### Concurrent Operations
- [ ] Multiple rapid entity commands handled
- [ ] Rate limiting prevents API flooding
- [ ] Commands queue properly
- [ ] All commands eventually execute
- [ ] No deadlocks or hangs

### State Transitions
- [ ] ON → STANDBY transition tracked
- [ ] STANDBY → ON transition tracked
- [ ] Polling interval adjusts correctly
- [ ] State-dependent properties handled
- [ ] Entities unavailable when appropriate

---

## Configuration Testing

### Initial Setup
- [ ] Config flow discovers device
- [ ] Host/port entry works
- [ ] Optional auth code works
- [ ] Setup without auth code works
- [ ] Invalid host shows error
- [ ] Connection timeout shows error
- [ ] Duplicate device prevented

### Reconfiguration
- [ ] Can change host address
- [ ] Can change port
- [ ] Can add auth code
- [ ] Can remove auth code
- [ ] Entities preserved after reconfig
- [ ] unique_ids remain stable

### Options Flow
- [ ] Options flow available (if implemented)
- [ ] Can adjust update interval (if implemented)
- [ ] Can adjust rate limit (if implemented)
- [ ] Changes take effect immediately

---

## Documentation Verification

### Code Documentation
- [ ] All modules have docstrings
- [ ] All classes have docstrings
- [ ] All public methods have docstrings
- [ ] Complex logic has inline comments
- [ ] Error handling rationale documented
- [ ] Edge cases documented

### User Documentation
- [ ] README.md updated with features
- [ ] README.md lists all entities
- [ ] README.md explains setup process
- [ ] Known limitations documented
- [ ] Troubleshooting section present
- [ ] Examples provided

### Developer Documentation
- [ ] Architecture documented
- [ ] API usage patterns explained
- [ ] Error handling patterns documented
- [ ] Testing procedures documented
- [ ] Contribution guidelines present

---

## Release Preparation

### Version Updates
- [ ] `manifest.json` version set to "0.0.2"
- [ ] Version number consistent across files
- [ ] Changelog/release notes prepared
- [ ] Breaking changes documented (if any)

### Git & Repository
- [ ] All changes committed
- [ ] Commit messages descriptive
- [ ] No uncommitted files
- [ ] No merge conflicts
- [ ] Tag created: `git tag v0.0.2`

### HACS Compatibility
- [ ] `hacs.json` present and valid
- [ ] `manifest.json` has all required fields
- [ ] Repository structure correct
- [ ] README.md formatted correctly
- [ ] License file present

---

## Final Checklist

### Must Have (Critical)
- [ ] All 6 critical tasks completed
- [ ] All entity commands have error handling
- [ ] All entity unique_ids stable
- [ ] Input validation on all user inputs
- [ ] Connection cleanup guaranteed
- [ ] JSON parsing optimized
- [ ] Refresh errors isolated from commands

### Should Have (High Priority)
- [ ] Connection lifecycle management
- [ ] Data validation on API responses
- [ ] Config flow cleanup
- [ ] Stale connection detection
- [ ] Error recovery functional

### Nice to Have (Medium/Low)
- [ ] PowerState enum implemented
- [ ] Dynamic laser constraints
- [ ] Rate limiting active
- [ ] Unique ID fallback validated

### Quality Gates
- [ ] Zero linting errors
- [ ] Zero linting warnings
- [ ] All functional tests pass
- [ ] All error scenarios tested
- [ ] 24-hour stability test passed
- [ ] No resource leaks detected
- [ ] Documentation complete

---

## Sign-Off

### AI Agent Verification
```
- [ ] I have completed all tasks in my assigned phase
- [ ] I have run scripts/lint with zero errors
- [ ] I have tested all changes manually
- [ ] I have verified error handling works
- [ ] I have checked for resource leaks
- [ ] I have updated documentation as needed
- [ ] I have committed all changes with clear messages
- [ ] I confirm the integration is stable and ready
```

### Testing Evidence
```
- [ ] Attached: scripts/lint output (clean)
- [ ] Attached: 24-hour stability test logs
- [ ] Attached: Error scenario test results
- [ ] Attached: Resource usage monitoring data
- [ ] Attached: Entity registry showing stable unique_ids
```

### Known Issues
```
Document any remaining issues here:
-
-
-
```

### Deferred to v0.0.3
```
List features/fixes deferred to next version:
-
-
-
```

---

## Post-Release Monitoring

### Week 1
- [ ] Monitor GitHub issues for bug reports
- [ ] Check Home Assistant logs from users
- [ ] Verify no widespread stability issues
- [ ] Address critical bugs immediately

### Week 2-4
- [ ] Collect user feedback
- [ ] Prioritize enhancements for v0.0.3
- [ ] Plan next iteration
- [ ] Update documentation based on questions

---

**Testing Status**: ⬜ Not Started | 🟨 In Progress | ✅ Complete

**Ready for Release**: ⬜ NO | ✅ YES

**Release Date**: _________________

**Released By**: _________________
