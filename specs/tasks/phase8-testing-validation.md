# Phase 8: Testing and Validation

## 8.1 Code Quality

### Linting
- [ ] Run `scripts/lint` to execute ruff format and check
- [ ] Fix all ruff formatting issues
- [ ] Fix all ruff lint issues
- [ ] Ensure no errors or warnings remain

### Type Hints
- [ ] Verify all files have `from __future__ import annotations`
- [ ] Check all function signatures have type hints
- [ ] Check all return types are specified
- [ ] Use modern type syntax: `dict[str, Any]` not `Dict[str, Any]`
- [ ] Use `| None` not `Optional[...]`
- [ ] Use `TYPE_CHECKING` for circular imports

### Documentation
- [ ] Add docstrings to all public methods
- [ ] Add docstrings to all classes
- [ ] Add inline comments for complex logic
- [ ] Verify all entity descriptions are clear

## 8.2 Manual Testing

### Connection Testing
- [ ] Test connection to real projector
- [ ] Test connection failure handling
- [ ] Test authentication with valid code
- [ ] Test authentication with invalid code
- [ ] Test connection timeout handling

### Config Flow Testing
- [ ] Test initial setup flow
- [ ] Test duplicate device prevention
- [ ] Test reconfigure flow
- [ ] Test error message display

### Power State Testing
- [ ] Test power on command
- [ ] Test power off command
- [ ] Test state updates during transitions
- [ ] Test fast polling when on
- [ ] Test slow polling when standby

### Entity Testing
- [ ] Test all binary sensors show correct state
- [ ] Test all sensors show correct values
- [ ] Test power switch works
- [ ] Test source select shows available sources
- [ ] Test source select changes input
- [ ] Test laser power number entity
- [ ] Test brightness/contrast/saturation/hue controls
- [ ] Test remote entity commands

### State Dependency Testing
- [ ] Verify properties unavailable in standby don't cause errors
- [ ] Verify graceful handling of -32601 error code
- [ ] Verify partial data updates work correctly
- [ ] Verify coordinator doesn't fail when properties unavailable

### Error Recovery Testing
- [ ] Test connection loss during operation
- [ ] Test network timeout handling
- [ ] Test malformed response handling
- [ ] Test coordinator retry logic

## 8.3 Integration Testing

### Home Assistant Integration
- [ ] Start HA using `scripts/develop`
- [ ] Add integration through UI
- [ ] Verify all entities appear
- [ ] Verify device info is correct
- [ ] Verify entity states update
- [ ] Test entity controls work
- [ ] Check HA logs for errors or warnings

### Reload Testing
- [ ] Test integration reload
- [ ] Verify entities persist correctly
- [ ] Test reconfigure flow
- [ ] Test integration removal and cleanup

### Performance Testing
- [ ] Monitor update coordinator performance
- [ ] Verify rate limiting works (1 second minimum)
- [ ] Check polling intervals adjust correctly
- [ ] Verify no excessive API calls

## 8.4 Pre-Release Checklist

### Code Review
- [ ] Review all exception handling
- [ ] Review all async/await usage
- [ ] Review all lock usage
- [ ] Review coordinator update logic
- [ ] Review entity unique ID generation

### Documentation Review
- [ ] Verify README has setup instructions
- [ ] Verify HACS compatibility
- [ ] Check all translation strings present
- [ ] Verify manifest.json is correct

### Final Validation
- [ ] All platforms load without errors
- [ ] No errors in Home Assistant logs
- [ ] All entities functional
- [ ] Connection cleanup works properly
- [ ] Integration unloads cleanly

### Version Control
- [ ] Commit all changes
- [ ] Tag release version
- [ ] Update CHANGELOG if present
- [ ] Push to repository
