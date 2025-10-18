# Barco HDR CS API - State-Dependent Properties

## Critical Discovery: Power State Dependency

**Date:** October 18, 2025

### Key Finding

Many properties are **only available when the projector is powered ON**. When the projector is in `standby` state, these properties return errors.

### Confirmed Working Properties

#### Always Available (any power state):
- ✅ `system.serialnumber`
- ✅ `system.modelname`
- ✅ `system.firmwareversion`
- ✅ `system.state`

#### Only Available When Powered ON:
- ✅ `illumination.sources.laser.power` - **WORKS when projector is ON**
- ⚠️ `image.window.main.source` - Needs testing when ON
- ⚠️ `image.source.list` - Needs testing when ON (may still not exist)

### Test Results

#### With Projector in STANDBY:
```json
Request: {
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "illumination.sources.laser.power"},
  "id": 1
}

Response: {
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Property not found: illumination.sources.laser.power"
  },
  "id": 1
}
```

#### With Projector POWERED ON:
```json
Request: {
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "illumination.sources.laser.power"},
  "id": 1
}

Response: {
  "jsonrpc": "2.0",
  "result": <laser_power_value>,
  "id": 1
}
```

### Implementation Implications

#### 1. Coordinator Updates Needed
The coordinator must handle state-dependent properties gracefully:
- Check `system.state` first
- Only query laser power if state is `"on"` or `"conditioning"` or similar
- Return `None` or skip properties when projector is off

#### 2. Entity Availability
Entities should report as `unavailable` when:
- Projector is in standby
- Required properties cannot be retrieved

#### 3. UI/UX Considerations
- Laser power sensor: Should be unavailable when projector is off
- Source sensor: Should be unavailable when projector is off
- System state sensor: Always available
- Power switch: Always available

### Recommended Coordinator Logic

```python
async def _async_update_data(self) -> dict[str, Any]:
    """Fetch data from API."""
    data = {}

    # Always fetch system info and state
    data["system"] = await self.client.get_system_info()
    state = await self.client.get_system_state()
    data["system"]["state"] = state

    # Determine if projector is on
    is_on = state in ("on", "conditioning", "ready")
    data["power"] = {"is_on": is_on}

    # Only fetch these properties when projector is on
    if is_on:
        try:
            data["illumination"] = {
                "laser_power": await self.client.get_laser_power()
            }
        except BarcoPulseCommandError:
            # Property not available even when on
            data["illumination"] = {"laser_power": None}

        try:
            data["source"] = {
                "active": await self.client.get_active_source()
            }
        except BarcoPulseCommandError:
            data["source"] = {"active": None}
    else:
        # Projector is off - these properties are unavailable
        data["illumination"] = {"laser_power": None}
        data["source"] = {"active": None}

    return data
```

### Next Steps

1. ✅ Update coordinator to check power state before querying dependent properties
2. ⏳ Test laser power retrieval with projector powered ON
3. ⏳ Test source properties with projector powered ON
4. ⏳ Update entity availability logic
5. ⏳ Document all state-dependent properties

### Properties to Re-Test When Powered ON

- `illumination.sources.laser.power` - ✅ Confirmed working
- `image.window.main.source` - ⏳ Needs testing
- `image.source.list` - ⏳ Needs testing (may not exist on HDR CS)

### State Transitions to Handle

```
standby → boot → conditioning → on
on → deconditioning → eco → standby
```

Properties availability may vary at each state. Need to test:
- `boot`: Probably unavailable
- `conditioning`: May be available
- `on`: ✅ Confirmed available
- `deconditioning`: May be available
- `eco`: Probably unavailable

---

**Conclusion:** This is expected behavior for laser-based projectors. The laser system is only initialized when the projector is powered on, so laser-related properties are unavailable during standby. The integration must handle this gracefully by checking power state before querying dependent properties.
