# Unfolded Circle Remote 3 Integration Guide

## Overview

The Barco Pulse integration exposes a **Remote entity** that is fully compatible with the Unfolded Circle Remote 3. This allows you to control power, input sources, presets, and profiles directly from your UC Remote.

## Supported Entity

### `remote.barco_pulse_remote`

The remote entity supports the following functionality:

- ✅ **Power Control**: Turn projector on/off
- ✅ **Command Sequences**: Send multiple commands in sequence
- ✅ **Input Source Selection**: Switch HDMI/SDI inputs
- ✅ **Preset Activation**: Activate numbered presets (0-29)
- ✅ **Profile Activation**: Activate profiles by name

## Command Format

The remote entity accepts commands in the following formats:

### 1. Source Selection
**Format**: `source_<name>`

**Examples**:
- `source_HDMI 1`
- `source_HDMI 2`
- `source_SDI 1`
- `source_DisplayPort 1`

### 2. Preset Activation
**Format**: `preset_<number>`

**Examples**:
- `preset_0` - Activate preset 0
- `preset_5` - Activate preset 5
- `preset_15` - Activate preset 15

**Valid Range**: 0-29 (30 total preset slots)

### 3. Profile Activation
**Format**: `profile_<name>`

**Examples**:
- `profile_Cinema`
- `profile_Gaming`
- `profile_Sports`
- `profile_Presentation`

**Note**: Profile names are case-sensitive and must exactly match the name configured in your Barco projector.

## Usage in Home Assistant

### Service Call Examples

#### Switch to HDMI 1
```yaml
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command: source_HDMI 1
```

#### Activate Preset 5
```yaml
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command: preset_5
```

#### Activate Cinema Profile
```yaml
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command: profile_Cinema
```

#### Send Multiple Commands (Sequence)
```yaml
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command:
    - source_HDMI 1
    - preset_5
```

## Configuration in Unfolded Circle Remote 3

### Step 1: Add the Remote Entity

1. Open the **Unfolded Circle Remote 3** web interface or mobile app
2. Navigate to **Integrations** → **Home Assistant**
3. Find and add the entity: `remote.barco_pulse_remote`

### Step 2: Create Activities

You can create activities that combine power control with preset/profile activation:

#### Example Activity: "Movie Night"
1. Create a new activity named "Movie Night"
2. Add the Barco remote entity
3. Configure the power-on sequence:
   - Turn on: `remote.barco_pulse_remote` (powers on projector)
   - Send command: `preset_1` (activates Cinema preset)
   - Send command: `source_HDMI 1` (switches to media player)

#### Example Activity: "Gaming"
1. Create activity "Gaming"
2. Add power-on sequence:
   - Turn on: `remote.barco_pulse_remote`
   - Send command: `profile_Gaming`
   - Send command: `source_HDMI 2`

#### Example Activity: "Sports"
1. Create activity "Sports"
2. Add power-on sequence:
   - Turn on: `remote.barco_pulse_remote`
   - Send command: `preset_10`
   - Send command: `source_HDMI 1`

### Step 3: Create Custom Buttons

You can create custom buttons on your UC Remote for quick preset/profile switching:

1. Go to **Remote** → **Buttons**
2. Add a new button (e.g., "Cinema Mode")
3. Configure the button action:
   - **Type**: Send Command
   - **Entity**: `remote.barco_pulse_remote`
   - **Command**: `preset_1` (or `profile_Cinema`)

Repeat for other presets/profiles you use frequently.

## How to Find Your Profile Names

If you're unsure of your exact profile names, you can check them in Home Assistant:

### Method 1: Using Developer Tools
1. Go to **Developer Tools** → **States**
2. Find entity: `select.barco_pulse_profile`
3. Check the `options` attribute for the list of available profile names

### Method 2: Using the Integration
1. Navigate to your Barco Pulse device in Home Assistant
2. Look for the "Profile" select entity
3. The dropdown shows all available profile names

### Method 3: Check Coordinator Data
Use the Template tool in Developer Tools:
```jinja2
{{ state_attr('select.barco_pulse_profile', 'options') }}
```

## Preset vs Profile: When to Use Which?

### Use **Presets** (`preset_<number>`) when:
- ✅ You have presets pre-configured on the projector
- ✅ You want faster activation (integer-based, more efficient)
- ✅ You prefer numbered references
- ✅ You use the same presets across multiple scenarios

### Use **Profiles** (`profile_<name>`) when:
- ✅ You want human-readable names
- ✅ You're unsure which preset number maps to which setting
- ✅ You frequently add/remove/rename profiles
- ✅ Profile names are more meaningful than numbers

**Pro Tip**: Presets are essentially "bookmarks" to profiles. A preset stores a reference to a profile plus optional source/lens position. If you know your preset assignments, use `preset_X` for faster execution.

## Troubleshooting

### Commands Not Working

**Check Projector State**:
- Presets and profiles can only be activated when the projector is **powered on**
- The projector must be in `on` or `ready` state
- Source commands work regardless of power state

**Verify Command Format**:
- Commands are case-sensitive
- Profile names must exactly match the projector configuration
- Preset numbers must be between 0-29

### Finding Command Issues

Enable debug logging in Home Assistant:

```yaml
logger:
  default: info
  logs:
    custom_components.barco_pulse: debug
```

Then check the logs for command execution details.

## Advanced: Automations with Presets/Profiles

### Time-Based Profile Switching
```yaml
automation:
  - alias: "Daytime Viewing Mode"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: state
        entity_id: remote.barco_pulse_remote
        state: "on"
    action:
      - service: remote.send_command
        target:
          entity_id: remote.barco_pulse_remote
        data:
          command: profile_Daytime

  - alias: "Evening Cinema Mode"
    trigger:
      - platform: time
        at: "19:00:00"
    condition:
      - condition: state
        entity_id: remote.barco_pulse_remote
        state: "on"
    action:
      - service: remote.send_command
        target:
          entity_id: remote.barco_pulse_remote
        data:
          command: preset_1
```

### Ambient Light Sensor Based
```yaml
automation:
  - alias: "Adjust Profile Based on Light"
    trigger:
      - platform: numeric_state
        entity_id: sensor.living_room_illuminance
        below: 50
    condition:
      - condition: state
        entity_id: remote.barco_pulse_remote
        state: "on"
    action:
      - service: remote.send_command
        target:
          entity_id: remote.barco_pulse_remote
        data:
          command: preset_2  # Dark room preset
```

### Media Player Integration
```yaml
automation:
  - alias: "Switch Profile Based on Media Type"
    trigger:
      - platform: state
        entity_id: media_player.plex
        to: "playing"
    condition:
      - condition: state
        entity_id: remote.barco_pulse_remote
        state: "on"
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ 'Movie' in state_attr('media_player.plex', 'media_content_type') }}"
            sequence:
              - service: remote.send_command
                target:
                  entity_id: remote.barco_pulse_remote
                data:
                  command: profile_Cinema
          - conditions:
              - condition: template
                value_template: "{{ 'Sports' in state_attr('media_player.plex', 'media_title') }}"
            sequence:
              - service: remote.send_command
                target:
                  entity_id: remote.barco_pulse_remote
                data:
                  command: preset_10
```

## Benefits of This Approach

✅ **Native UC Remote Support**: Remote entities are fully supported without workarounds

✅ **Simple Command Syntax**: Easy-to-remember command format

✅ **Flexible**: Can send single commands or sequences

✅ **Activity Integration**: Works seamlessly with UC Remote activities

✅ **No Additional Entities**: Uses existing remote entity, no need for extra select entities

✅ **Fast Execution**: Commands execute immediately without UI delays

## Alternative: Using Select Entities (Not Recommended for UC Remote)

While the integration also provides `select.barco_pulse_preset` and `select.barco_pulse_profile` entities, these are **not directly supported** by the Unfolded Circle Remote 3. The remote entity approach is the recommended method.

## Summary

The Barco Pulse integration's remote entity provides full compatibility with the Unfolded Circle Remote 3, allowing you to:

- Control power and basic functions
- Switch input sources
- Activate presets by number (0-29)
- Activate profiles by name

Use the command formats documented above to create activities, buttons, and automations that work seamlessly with your UC Remote 3.
