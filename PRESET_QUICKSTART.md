# Preset Feature - Quick Start Guide

## What Was Implemented

A **Preset Select Entity** that allows users to activate Barco Pulse projector presets directly from Home Assistant.

## How It Works

### 1. Entity Details
- **Entity ID**: `select.barco_pulse_preset`
- **Name**: Preset
- **Icon**: 🎨 (mdi:palette)
- **Availability**: Only when projector is powered on (`on` or `ready` state)

### 2. User Interface

The select dropdown will show all 30 preset slots (numbered 0-29):
```
Preset 0
Preset 1
Preset 2
...
Preset 29
```

**Note**: All 30 preset slots are always shown. The projector has predefined preset slots 0-29, and you can activate any of them. Some may have profiles assigned, others may not.

### 3. Usage Examples

#### Via UI
1. Open Home Assistant
2. Navigate to your Barco Pulse device
3. Find the "Preset" select entity
4. Choose a preset from the dropdown
5. Projector will immediately switch to that preset

#### Via Automation
```yaml
automation:
  - alias: "Movie Mode"
    trigger:
      - platform: state
        entity_id: media_player.living_room_tv
        to: "playing"
    condition:
      - condition: state
        entity_id: switch.barco_pulse_power
        state: "on"
    action:
      - service: select.select_option
        target:
          entity_id: select.barco_pulse_preset
        data:
          option: "Preset 0"
```

#### Via Service Call
```yaml
service: select.select_option
target:
  entity_id: select.barco_pulse_preset
data:
  option: "Preset 5"
```

#### Via Script
```yaml
script:
  activate_cinema_preset:
    alias: "Activate Cinema Preset"
    sequence:
      - service: select.select_option
        target:
          entity_id: select.barco_pulse_preset
        data:
          option: "Preset 0"
```

## Important Notes

### Power State Requirement
- ⚠️ **Preset activation only works when the projector is powered on**
- The entity will show as "unavailable" when the projector is off/standby
- Make sure to power on the projector first before activating presets

### No Active Preset Tracking
- The API does not provide a way to query the "currently active" preset
- The current_option will always show as `None`
- This is a limitation of the Barco Pulse API, not the integration

### Preset Configuration
- Presets 0-29 are predefined slots on the projector
- All 30 presets are always shown in the dropdown
- You can activate any preset, regardless of whether it has a profile assigned
- If a preset has no profile assigned, activating it may have no effect or show an error in the logs

## Technical Implementation

### API Methods Used
- `profile.presetassignments` - Get preset → profile mappings
- `profile.activatepreset` - Activate a preset by number (used)
- `profile.profiles` - Get list of available profiles

### Data Flow
```
User selects preset → Parse option → Call API → Refresh coordinator → Update UI
   "Preset 5"    →   preset=5   → activate →  Get data   →  Show result
```

### Error Handling
- Gracefully handles projector being off (entity unavailable)
- Logs errors if preset format is invalid
- Handles API errors from the projector

## Files Modified

1. **`api.py`** - Added preset-related API methods
2. **`coordinator.py`** - Added preset data fetching
3. **`select.py`** - Added `BarcoPresetSelect` entity
4. **`translations/en.json`** - Added preset translations

## Testing Checklist

- [ ] Power on projector
- [ ] Verify preset entity becomes available
- [ ] Check that presets 0-29 appear in dropdown
- [ ] Select a preset and verify projector responds
- [ ] Power off projector and verify entity becomes unavailable
- [ ] Check logs for any errors

## Common Issues

### Entity Not Showing Up
- Restart Home Assistant after installing the integration
- Check that the projector is connected and powered on
- Verify that presets are configured on the projector

### "No profiles configured" Message
- This appears only if the projector has no profiles at all
- Presets are always available (0-29), but profiles must exist on the projector
- Create profiles on the projector to enable preset functionality

### Preset Activation Fails
- Ensure projector is in `on` or `ready` state
- Check that the preset number exists
- Verify network connection to projector
- Check Home Assistant logs for error messages

## Future Enhancements

Possible future additions:
- Track currently active preset (if API support added)
- Create/modify/delete presets from Home Assistant
- Show profile details and contained domains
- Real-time notifications when presets change
