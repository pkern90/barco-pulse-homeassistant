# Preset Implementation Summary

## Overview

Added support for activating Barco Pulse projector presets through Home Assistant. Presets can only be activated when the projector is powered on (`on` or `ready` state).

## Changes Made

### 1. API Layer (`custom_components/barco_pulse/api.py`)

Added the following methods to the `BarcoDevice` class:

#### `get_preset_assignments() -> dict[int, str]`
- Retrieves all preset assignments from the projector
- Returns a dictionary mapping preset numbers to profile names
- Example: `{1: "Cinema", 2: "Gaming", 3: "Sports"}`
- Raises `BarcoStateError` if projector is not in active state

#### `get_profiles() -> list[str]`
- Gets the list of all available profile names
- Returns a list of profile name strings
- Raises `BarcoStateError` if projector is not in active state

#### `activate_preset(preset: int) -> bool`
- Activates a preset by its number using `profile.activatepreset` JSON-RPC method
- More efficient than `activate_profile` as it uses integers instead of strings
- Returns `True` if activation successful
- Raises `BarcoStateError` if projector is not in active state
- Raises `BarcoApiError` if preset not assigned or invalid

#### `activate_profile(name: str) -> bool`
- Alternative method to activate a profile by name using `profile.activateprofile`
- Returns `True` if activation successful
- Raises `BarcoStateError` if projector is not in active state
- Raises `BarcoApiError` if profile not found

#### `get_profile_for_preset(preset: int) -> str`
- Gets the profile name assigned to a specific preset number
- Returns empty string if unassigned
- Raises `BarcoStateError` if projector is not in active state

**Type Signature Update**: Updated `_send_request` and `_build_jsonrpc_request` parameter types from `dict[str, Any] | list[Any] | None` to `Any` to support single-value params as required by the Barco API.

### 2. Coordinator Layer (`custom_components/barco_pulse/coordinator.py`)

Added preset data fetching to `_get_active_properties()` method:

- Fetches `preset_assignments` (dict mapping preset numbers to profile names)
- Fetches `profiles` (list of available profile names)
- Creates `available_presets` (sorted list of preset numbers with assigned profiles)
- All wrapped in try/except blocks to handle `BarcoStateError` gracefully

### 3. Select Platform (`custom_components/barco_pulse/select.py`)

#### Added `BarcoPresetSelect` Entity

**Key Features:**
- Translation key: `preset`
- Icon: `mdi:palette`
- Unique ID: `{serial_number}_preset`

**Properties:**
- `current_option`: Returns `None` (no way to track "active" preset from API)
- `options`: Returns list of all 30 preset slots: `["Preset 0", "Preset 1", ..., "Preset 29"]`
  - Always shows all 30 predefined preset slots (0-29)
  - Returns `["No profiles configured"]` if no profiles exist on projector
- `available`: Only available when projector is in `on` or `ready` state

**Operation:**
- Parses selected option (e.g., `"Preset 5"`) to extract preset number
- Calls `device.activate_preset(preset_num)`
- Triggers coordinator refresh to update state
- Logs exceptions if parsing fails

#### Updated `async_setup_entry()`
- Now creates both `BarcoSourceSelect` and `BarcoPresetSelect` entities

### 4. Translations (`custom_components/barco_pulse/translations/en.json`)

Added preset entity translation:
```json
"preset": {
    "name": "Preset"
}
```

## Usage in Home Assistant

Once the integration is loaded and the projector is connected:

1. **Entity Name**: `select.barco_pulse_preset` (actual name based on device)
2. **Availability**: Only available when projector is powered on
3. **Options**: Shows all configured presets in format `"1: Profile Name"`
4. **Selection**: Choose a preset from the dropdown to activate it

### Example Automation

```yaml
automation:
  - alias: "Activate Cinema Preset at Night"
    trigger:
      - platform: sun
        event: sunset
    condition:
      - condition: state
        entity_id: switch.barco_pulse_power
        state: "on"
    action:
      - service: select.select_option
        target:
          entity_id: select.barco_pulse_preset
        data:
          option: "1: Cinema"
```

## Technical Notes

### API Protocol
- Uses JSON-RPC 2.0 method: `profile.activatepreset`
- Preset parameter is an integer (more efficient than string-based `profile.activateprofile`)
- Example request:
  ```json
  {
    "jsonrpc": "2.0",
    "method": "profile.activatepreset",
    "id": 386,
    "params": 1
  }
  ```

### State Dependencies
- All preset-related properties (`profile.presetassignments`, `profile.profiles`) are state-dependent
- Only available when `system.state` is `on` or `ready`
- API returns error `-32601` (Property not found) when queried in other states
- Coordinator catches `BarcoStateError` and logs debug message without failing
- **Note**: The preset list (0-29) is hardcoded and always shown when profiles exist, regardless of assignments

### Error Handling
- Gracefully handles missing preset data when projector is off
- Shows "No profiles configured" when no profiles exist on the projector
- Shows all 30 preset slots (0-29) when profiles exist
- Logs exceptions if preset option parsing fails
- Coordinator refresh ensures UI stays updated after preset activation

## Testing Recommendations

1. **Power State Testing**:
   - Verify entity becomes unavailable when projector is off/standby
   - Verify entity becomes available when projector is on/ready

2. **Preset Discovery**:
   - Check that all 30 preset slots (0-29) appear in the dropdown
   - Verify format is correct: "Preset X"
   - Confirm entity shows "No profiles configured" only when no profiles exist

3. **Activation Testing**:
   - Select each preset and verify projector switches profiles
   - Check logs for any parsing errors
   - Verify coordinator refreshes after activation

4. **Edge Cases**:
   - Projector with no profiles configured
   - Activating unassigned preset slots
   - Network interruption during preset activation

## Future Enhancements

Possible improvements for future versions:

1. **Track Active Preset**: If Barco adds API support, show currently active preset
2. **Preset Management**: Add services to create/delete/assign presets
3. **Profile Details**: Show which domains are stored in each profile
4. **Notifications**: Subscribe to `profileactivated` signal for real-time updates
5. **Batch Operations**: Support for multiple preset activations in sequence
