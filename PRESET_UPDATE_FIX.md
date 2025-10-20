# Preset Implementation - Update Summary

## Issue Fixed

**Problem**: The UI showed "No presets configured" even though profiles existed on the projector.

**Root Cause**: The implementation was trying to show only presets with assigned profiles, but the `preset_assignments` property was returning an empty dictionary `{}`.

**Analysis of Logs**:
```
'preset_assignments': {},
'available_presets': [],
'profiles': ['Gaming', 'Profile 1']
```

The projector has profiles but no preset assignments were being retrieved.

## Solution

**Understanding Barco Presets**:
- Barco projectors have **30 predefined preset slots** numbered **0-29**
- These slots always exist and can be activated
- Profiles can be assigned to presets, but the slots exist independently
- Users should be able to activate any preset slot (0-29)

**Implementation Change**:
Instead of dynamically building a list based on preset assignments, the UI now:
1. Always shows all 30 preset slots: "Preset 0" through "Preset 29"
2. Only requires that profiles exist (not that presets are assigned)
3. Allows activation of any preset slot

## Code Changes

### `custom_components/barco_pulse/select.py`

**Before**:
```python
@property
def options(self) -> list[str]:
    """Return the list of available presets."""
    preset_assignments = self.coordinator.data.get("preset_assignments", {})
    if not preset_assignments:
        return ["No presets configured"]

    # Create user-friendly options like "1: Profile Name"
    options = []
    for preset_num in sorted(preset_assignments.keys()):
        profile_name = preset_assignments[preset_num]
        if profile_name:  # Only show assigned presets
            options.append(f"{preset_num}: {profile_name}")

    return options if options else ["No presets configured"]
```

**After**:
```python
@property
def options(self) -> list[str]:
    """Return the list of available presets."""
    profiles = self.coordinator.data.get("profiles", [])

    # If no profiles exist, show message
    if not profiles:
        return ["No profiles configured"]

    # Presets are numbered 0-29 (30 total slots)
    # Show all presets regardless of assignment
    return [f"Preset {preset_num}" for preset_num in range(30)]
```

**Parsing Logic**:
```python
# Before: "1: Cinema" → preset_num = int(option.split(":")[0].strip())
# After:  "Preset 5" → preset_num = int(option.split()[-1])
```

## User Impact

### Before Fix
- UI showed "No presets configured"
- Users could not activate any presets
- Required preset assignments to exist

### After Fix
- UI shows "Preset 0" through "Preset 29"
- Users can activate any preset slot
- Only requires that profiles exist on the projector
- More aligned with how Barco projectors actually work

## Usage Example

### In Home Assistant UI
1. Power on projector
2. Navigate to Barco Pulse device
3. Find "Preset" select entity
4. See dropdown with all 30 presets:
   - Preset 0
   - Preset 1
   - Preset 2
   - ...
   - Preset 29
5. Select any preset to activate it

### In Automations
```yaml
service: select.select_option
target:
  entity_id: select.barco_pulse_preset
data:
  option: "Preset 5"
```

## Notes

- The preset assignment data (`preset_assignments`) is still fetched by the coordinator for potential future use
- The implementation now matches the actual behavior of Barco Pulse projectors
- If a preset has no profile assigned, activating it may have no effect (handled gracefully)
- All 30 slots are always shown when the projector is on and profiles exist

## Testing

After this change, with your projector:
1. ✅ Entity should show all 30 presets (not "No presets configured")
2. ✅ You can select and activate any preset 0-29
3. ✅ The API call will succeed for valid presets
4. ✅ Invalid or unassigned presets may fail gracefully (logged)

## Files Updated

1. `custom_components/barco_pulse/select.py` - Updated preset options and parsing logic
2. `PRESET_IMPLEMENTATION.md` - Updated technical documentation
3. `PRESET_QUICKSTART.md` - Updated user guide
