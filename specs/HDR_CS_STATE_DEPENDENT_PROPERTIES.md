# Barco Pulse API - State-Dependent Property Behavior

## Overview

Barco Pulse projectors expose different sets of properties depending on their current power state. Many properties are **only available when the projector is powered ON**, returning errors when queried in lower power states like `standby`.

**Tested Models:** Barco HDR CS  
**Last Updated:** October 18, 2025

## Power State Dependency


## Property Availability by Power State

### Always Available (any power state):
- ✅ `system.serialnumber` - Projector serial number
- ✅ `system.modelname` - Projector model name
- ✅ `system.firmwareversion` - Firmware version string
- ✅ `system.state` - Current power state

### Only Available When Powered ON:
- ✅ `illumination.sources.laser.power` - Laser power percentage
- ⚠️ `image.window.main.source` - Active input source (may vary by model)
- ⚠️ `image.source.list` - Available input sources (may not exist on all models)

**Note:** The "powered ON" category includes states: `on`, `conditioning`, and potentially `ready`. States like `standby`, `boot`, `eco`, and `deconditioning` typically do not expose these properties.

## Error Behavior


## Error Behavior

When querying a state-dependent property while the projector is in an inappropriate state (e.g., `standby`), the API returns a JSON-RPC error response:

### Example: Querying Laser Power in STANDBY
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

### Example: Querying Laser Power When POWERED ON

**Request:**
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

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": 75.5,
  "id": 1
}
```

*Note: Actual value varies based on projector settings*

## Power State Transitions

Barco Pulse projectors transition through multiple states during power on/off cycles:

### Power-On Sequence
```
standby → boot → conditioning → on
```

### Power-Off Sequence
```
on → deconditioning → eco → standby
```

### Property Availability During Transitions

| State | System Properties | Laser/Illumination | Source/Input |
|-------|------------------|-------------------|--------------|
| `standby` | ✅ Available | ❌ Not Available | ❌ Not Available |
| `boot` | ✅ Available | ❌ Not Available | ❌ Not Available |
| `conditioning` | ✅ Available | ⚠️ May be available | ⚠️ May be available |
| `on` | ✅ Available | ✅ Available | ✅ Available |
| `ready` | ✅ Available | ✅ Available | ✅ Available |
| `deconditioning` | ✅ Available | ⚠️ May be available | ⚠️ May be available |
| `eco` | ✅ Available | ❌ Not Available | ❌ Not Available |

**Legend:**
- ✅ Confirmed available
- ❌ Confirmed unavailable
- ⚠️ Availability may vary; recommend testing

## Implementation Guidance

### Recommended Approach for Client Applications

1. **Always Query Power State First**
   ```json
   {"jsonrpc":"2.0","method":"property.get","params":{"property":"system.state"},"id":1}
   ```

2. **Check State Before Querying Dependent Properties**
   - Only query `illumination.*` properties when state is `on` or `ready`
   - Only query `image.*` properties when state is `on` or `ready`
   - System properties can be queried in any state

3. **Handle Errors Gracefully**
   - Error code `-32601` ("Property not found") may indicate state dependency
   - Don't retry immediately; wait for state change or power-on completion
   - Treat unavailable properties as null/unknown rather than errors

### Example Decision Logic

```pseudocode
state = get_property("system.state")

if state in ["on", "ready"]:
    // Safe to query all properties
    laser_power = get_property("illumination.sources.laser.power")
    active_source = get_property("image.window.main.source")
else if state in ["conditioning", "deconditioning"]:
    // Transitional states - attempt with error handling
    try:
        laser_power = get_property("illumination.sources.laser.power")
    catch PropertyNotFoundError:
        laser_power = null
else:
    // Standby, boot, eco - skip dependent properties
    laser_power = null
    active_source = null
```

### Availability vs. Error States

When building user interfaces or monitoring systems, distinguish between:

- **Unavailable:** Property cannot be queried due to power state (not an error)
- **Error:** Property should be available but query failed (network issue, authentication, etc.)
- **Unknown:** Property exists but value is null/empty

## Technical Rationale

### Why Are Properties State-Dependent?

**Laser-based projectors** (like Barco Pulse models) have hardware components that are only initialized when the projector is fully powered on:

1. **Laser modules** are powered down in standby for longevity and safety
2. **Image processing hardware** may be in low-power mode during standby
3. **Input detection circuits** may not be active until full power-on

This behavior is **expected and by design**, not a bug or limitation. It reflects the physical state of the projector hardware.

### Performance Considerations

- **Avoid polling unavailable properties** - reduces unnecessary error responses
- **Cache power state** - minimizes redundant queries
- **Batch property queries** when possible (if API supports batch requests)
- **Subscribe to state changes** if API supports property subscriptions

## Testing Checklist

When implementing a Barco Pulse client, test the following scenarios:

- [ ] Query system properties in all power states (should always work)
- [ ] Query laser power in `standby` (should return error -32601)
- [ ] Query laser power in `on` state (should return numeric value)
- [ ] Monitor state transitions during power-on sequence
- [ ] Monitor state transitions during power-off sequence
- [ ] Handle `-32601` errors without crashing or retrying excessively
- [ ] Verify property availability in `conditioning` and `deconditioning` states
- [ ] Test behavior when projector loses power unexpectedly

## Related Documentation

- **Barco Pulse Protocol:** See `BARCO_HDR_CS_PROTOCOL.md` for HTTP/0.9 communication details
- **Barco Pulse API Reference:** See `pulse-api-docs.md` for complete property and method documentation

## Appendix: Known Properties by Category

### System Properties (Always Available)
- `system.serialnumber`
- `system.modelname`
- `system.firmwareversion`
- `system.state`
- `system.uptime` (likely always available)
- `network.*` properties (likely always available)

### Illumination Properties (Power-On Required)
- `illumination.sources.laser.power`
- `illumination.sources.laser.hours` (may be available in standby)
- `illumination.mode` (power-on required)
- `illumination.brightness` (power-on required)

### Image Properties (Power-On Required)
- `image.window.main.source`
- `image.window.main.size`
- `image.window.main.position`
- `image.processing.*` properties
- `image.color.*` properties

### Source Properties (Power-On Required)
- Methods: `image.source.list`
- Source-specific properties and settings

**Note:** This list is based on Barco HDR CS testing. Property availability may vary by projector model and firmware version. Always consult the official Barco API documentation for your specific model.

---

## Summary

**Key Takeaways:**

1. ✅ System properties are always available regardless of power state
2. ❌ Laser/illumination and image properties require projector to be powered on
3. 🔄 State transitions affect property availability dynamically
4. ⚠️ Clients must check `system.state` before querying dependent properties
5. 🎯 Error code `-32601` indicates property unavailable (often due to power state)

This behavior is **normal and expected** for laser projector systems. Proper client implementation must account for state-dependent property availability to provide a robust user experience.
