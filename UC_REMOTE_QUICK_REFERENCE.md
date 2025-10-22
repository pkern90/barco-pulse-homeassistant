# Unfolded Circle Remote 3 - Quick Reference

## Entity to Use
`remote.barco_pulse_remote`

## Command Quick Reference

| Action               | Command Format    | Example          |
| -------------------- | ----------------- | ---------------- |
| **Switch Source**    | `source_<name>`   | `source_HDMI 1`  |
| **Activate Preset**  | `preset_<number>` | `preset_5`       |
| **Activate Profile** | `profile_<name>`  | `profile_Cinema` |

## Common Commands

```yaml
# Power On
service: remote.turn_on
target:
  entity_id: remote.barco_pulse_remote

# Power Off
service: remote.turn_off
target:
  entity_id: remote.barco_pulse_remote

# Switch to HDMI 1
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command: source_HDMI 1

# Activate Cinema Preset (slot 1)
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command: preset_1

# Activate Gaming Profile
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command: profile_Gaming

# Command Sequence (multiple commands)
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command:
    - source_HDMI 1
    - preset_1
```

## UC Remote Activity Setup Examples

### Movie Night Activity
1. **Power On**: `remote.barco_pulse_remote`
2. **Send Command**: `preset_1` (Cinema preset)
3. **Send Command**: `source_HDMI 1`

### Gaming Activity
1. **Power On**: `remote.barco_pulse_remote`
2. **Send Command**: `profile_Gaming`
3. **Send Command**: `source_HDMI 2`

### Sports Activity
1. **Power On**: `remote.barco_pulse_remote`
2. **Send Command**: `preset_10` (Sports preset)
3. **Send Command**: `source_HDMI 1`

## Finding Your Profile Names

Check in Home Assistant:
```
Developer Tools → States → select.barco_pulse_profile
```
Look at the `options` attribute for available names.

## Available Preset Numbers
- Range: **0 to 29** (30 total slots)
- Use: `preset_0`, `preset_1`, ..., `preset_29`

## Important Notes

⚠️ **State Requirement**: Presets and profiles only work when projector is **powered on** (`on` or `ready` state)

⚠️ **Case Sensitivity**: Profile names are case-sensitive - `profile_Cinema` ≠ `profile_cinema`

⚠️ **Exact Match**: Profile names must exactly match projector configuration

✅ **Sources Work Anytime**: Source commands work regardless of power state

## Preset vs Profile?

- **Preset** = Numbered slot (0-29) that stores profile + source + lens position
- **Profile** = Named picture setting (Cinema, Gaming, Sports, etc.)

**Use presets** for faster execution and activity-based scenes.
**Use profiles** for direct picture mode changes.

## Troubleshooting

1. **Commands not working?**
   - Check projector is powered on
   - Verify profile name spelling/case
   - Ensure preset number is 0-29

2. **Find profile names:**
   ```yaml
   # In Developer Tools → Template
   {{ state_attr('select.barco_pulse_profile', 'options') }}
   ```

3. **Enable debug logging:**
   ```yaml
   logger:
     logs:
       custom_components.barco_pulse: debug
   ```

## Need More Details?
See: `UNFOLDED_CIRCLE_REMOTE_INTEGRATION.md` for complete documentation.
