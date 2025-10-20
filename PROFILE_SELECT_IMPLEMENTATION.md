# Profile Select Implementation Summary

## Overview

Added a **Profile Select Entity** that allows users to activate Barco Pulse projector profiles directly by name from Home Assistant.

## What Was Implemented

### New Entity: `BarcoProfileSelect`

**Entity Details:**
- **Entity ID**: `select.barco_pulse_profile`
- **Name**: Profile
- **Icon**: 🏔️ (mdi:image-filter-hdr)
- **Availability**: Only when projector is powered on (`on` or `ready` state)

**Features:**
- Displays all available profiles from the projector
- Direct activation by profile name (uses `profile.activateprofile` API)
- Shows "No profiles configured" when no profiles exist
- Automatically refreshes coordinator after activation

## Implementation Details

### 1. `custom_components/barco_pulse/select.py`

Added `BarcoProfileSelect` class:

```python
class BarcoProfileSelect(BarcoEntity, SelectEntity):
    """Barco Pulse profile select entity."""

    _attr_translation_key = "profile"
    _attr_icon = "mdi:image-filter-hdr"
```

**Key Methods:**
- `options`: Returns list of profile names from `coordinator.data.get("profiles")`
- `async_select_option`: Calls `device.activate_profile(option)` with the profile name
- `available`: Only available when projector state is `on` or `ready`
- `current_option`: Returns `None` (no way to track active profile via API)

### 2. `custom_components/barco_pulse/translations/en.json`

Added translation:
```json
"profile": {
    "name": "Profile"
}
```

### 3. Entity Registration

Updated `async_setup_entry()` to include all three select entities:
- `BarcoSourceSelect` - Input source selection
- `BarcoPresetSelect` - Preset slots (0-29)
- `BarcoProfileSelect` - Profile names (**NEW**)

## Usage Examples

### Via Home Assistant UI

1. Power on the projector
2. Navigate to the Barco Pulse device
3. Find the "Profile" select entity
4. Choose a profile from the dropdown (e.g., "Gaming", "Profile 1")
5. Profile is immediately activated

### Via Automation

```yaml
automation:
  - alias: "Activate Gaming Profile for Movie Night"
    trigger:
      - platform: time
        at: "19:00:00"
    condition:
      - condition: state
        entity_id: switch.barco_pulse_power
        state: "on"
    action:
      - service: select.select_option
        target:
          entity_id: select.barco_pulse_profile
        data:
          option: "Gaming"
```

### Via Service Call

```yaml
service: select.select_option
target:
  entity_id: select.barco_pulse_profile
data:
  option: "Profile 1"
```

### Via Script

```yaml
script:
  movie_mode:
    alias: "Movie Mode"
    sequence:
      - service: switch.turn_on
        target:
          entity_id: switch.barco_pulse_power
      - delay:
          seconds: 30  # Wait for projector to power up
      - service: select.select_option
        target:
          entity_id: select.barco_pulse_profile
        data:
          option: "Cinema"
```

## Comparison: Preset vs Profile

| Feature              | Preset Select               | Profile Select                      |
| -------------------- | --------------------------- | ----------------------------------- |
| **Selection Method** | By number (0-29)            | By name (e.g., "Gaming")            |
| **API Method**       | `profile.activatepreset`    | `profile.activateprofile`           |
| **Parameter Type**   | Integer                     | String                              |
| **Display Format**   | "Preset 0", "Preset 1", ... | "Gaming", "Profile 1", ...          |
| **Total Options**    | Always 30 slots             | Dynamic (based on created profiles) |
| **Use Case**         | Quick numbered access       | User-friendly named access          |

## Technical Notes

### API Integration

The profile select uses:
- **API Method**: `profile.activateprofile`
- **Parameter**: Profile name (string)
- **Example Request**:
  ```json
  {
    "jsonrpc": "2.0",
    "method": "profile.activateprofile",
    "id": 1,
    "params": "Gaming"
  }
  ```

### State Dependencies

- Profile list (`profile.profiles`) is state-dependent
- Only available when `system.state` is `on` or `ready`
- Coordinator gracefully handles `BarcoStateError` when projector is off
- Entity becomes unavailable when projector is not active

### Data Flow

```
User selects profile → Coordinator data provides options → Entity calls API → Profile activated → Coordinator refreshes → UI updates
     "Gaming"       →  ['Gaming', 'Profile 1']  →  activateprofile →    Result    →   Fetch data  →   Available
```

## Testing Checklist

- [x] Entity appears when projector is powered on
- [x] Shows list of available profiles
- [x] Can select and activate each profile
- [x] Entity becomes unavailable when projector is off
- [x] Shows "No profiles configured" when appropriate
- [x] Coordinator refreshes after activation
- [x] Lint checks pass
- [x] Translation works correctly

## Files Modified

1. ✅ `custom_components/barco_pulse/select.py` - Added `BarcoProfileSelect` class
2. ✅ `custom_components/barco_pulse/translations/en.json` - Added profile translation
3. ✅ `.ruff.toml` - Added examples directory exception (for lint)

## Related API Methods (Already Implemented)

From the initial preset implementation:
- `get_profiles()` - Returns list of profile names
- `activate_profile(name)` - Activates profile by name (**used by this entity**)
- `get_preset_assignments()` - Gets preset → profile mappings
- `activate_preset(preset)` - Activates preset by number

## Future Enhancements

Potential improvements:
1. Track active profile (if Barco adds API support)
2. Profile management (create/delete profiles)
3. Show profile details (which domains are stored)
4. Profile export/import
5. Subscribe to `profileactivated` signal for real-time updates

## Summary

The profile select implementation is complete and working! Users now have three select entities:

1. **Input Source** - Choose HDMI/DisplayPort/SDI inputs
2. **Preset** - Quick access to preset slots 0-29
3. **Profile** - User-friendly profile selection by name

All entities follow Home Assistant best practices and pass linting checks. ✅
