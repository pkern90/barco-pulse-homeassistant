# Unfolded Circle Remote 3 Setup - Visual Guide

## Overview Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Unfolded Circle Remote 3                        │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Activity   │  │   Activity   │  │    Button    │  │
│  │ Movie Night  │  │    Gaming    │  │   Cinema     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
│         └──────────────────┴──────────────────┘          │
│                            │                             │
└────────────────────────────┼─────────────────────────────┘
                             │
                             │ Commands via Home Assistant
                             │
┌────────────────────────────▼─────────────────────────────┐
│              Home Assistant                              │
│                                                           │
│    ┌─────────────────────────────────────────┐          │
│    │  remote.barco_pulse_remote              │          │
│    ├─────────────────────────────────────────┤          │
│    │  • Power On/Off                         │          │
│    │  • source_HDMI 1                        │          │
│    │  • preset_0 ... preset_29               │          │
│    │  • profile_Cinema, profile_Gaming, etc. │          │
│    └────────────────┬────────────────────────┘          │
│                     │                                     │
└─────────────────────┼─────────────────────────────────────┘
                      │
                      │ JSON-RPC over TCP
                      │
┌─────────────────────▼─────────────────────────────────┐
│            Barco Pulse Projector                      │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Preset  │  │  Preset  │  │  Preset  │  ...      │
│  │    0     │  │    1     │  │    2     │           │
│  │          │  │          │  │          │           │
│  │ Cinema   │  │  Gaming  │  │  Sports  │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│                                                        │
│  ┌──────────────────────────────────────────┐        │
│  │ Profiles:                                 │        │
│  │  • Cinema                                │        │
│  │  • Gaming                                │        │
│  │  • Sports                                │        │
│  │  • Presentation                          │        │
│  └──────────────────────────────────────────┘        │
└────────────────────────────────────────────────────────┘
```

## Command Flow

### Example: "Movie Night" Activity

```
UC Remote Button Press
         │
         ▼
┌────────────────────────┐
│ Activity: Movie Night  │
│                        │
│ Sequence:              │
│ 1. Turn On             │─────▶  remote.turn_on
│ 2. Send: preset_1      │─────▶  remote.send_command: preset_1
│ 3. Send: source_HDMI 1 │─────▶  remote.send_command: source_HDMI 1
└────────────────────────┘
         │
         ▼
┌────────────────────────┐
│  Home Assistant        │
│  Processes Commands    │
└────────────────────────┘
         │
         ▼
┌────────────────────────┐
│  Barco Projector       │
│  • Powers On           │
│  • Activates Preset 1  │
│    (Cinema mode)       │
│  • Switches to HDMI 1  │
└────────────────────────┘
```

## Setup Steps

### Step 1: Add Entity to UC Remote

```
UC Remote Web Interface
└─ Integrations
   └─ Home Assistant
      └─ Add Entity
         └─ remote.barco_pulse_remote ✓
```

### Step 2: Create Activity

```
UC Remote
└─ Activities
   └─ Create New Activity
      ├─ Name: "Movie Night"
      ├─ Icon: 🎬
      └─ On Sequence:
         ├─ [1] Turn On: remote.barco_pulse_remote
         ├─ [2] Send Command: preset_1
         └─ [3] Send Command: source_HDMI 1
```

### Step 3: Add Custom Buttons (Optional)

```
UC Remote
└─ Remote
   └─ Buttons
      └─ Add Button
         ├─ Label: "Cinema"
         ├─ Icon: 🎭
         └─ Action: Send Command
            └─ Command: preset_1
```

## Command Mapping

### Sources
| Your Device             | Command Format         |
| ----------------------- | ---------------------- |
| Apple TV (HDMI 1)       | `source_HDMI 1`        |
| Gaming Console (HDMI 2) | `source_HDMI 2`        |
| Blu-ray Player (HDMI 3) | `source_HDMI 3`        |
| PC (DisplayPort 1)      | `source_DisplayPort 1` |

### Presets (0-29)
| Preset # | Your Setup      | Command     |
| -------- | --------------- | ----------- |
| 0        | Cinema (Dark)   | `preset_0`  |
| 1        | Cinema (Bright) | `preset_1`  |
| 2        | Gaming          | `preset_2`  |
| 3        | Sports          | `preset_3`  |
| 4        | Presentation    | `preset_4`  |
| ...      |                 |             |
| 29       | Custom          | `preset_29` |

### Profiles (by name)
| Profile Name | Command                |
| ------------ | ---------------------- |
| Cinema       | `profile_Cinema`       |
| Gaming       | `profile_Gaming`       |
| Sports       | `profile_Sports`       |
| Presentation | `profile_Presentation` |

## Complete Activity Examples

### 🎬 Movie Night (Preset-based)
```yaml
Activity: Movie Night
├─ Power: On (remote.barco_pulse_remote)
├─ Command: preset_1
└─ Command: source_HDMI 1
```

### 🎮 Gaming Session (Profile-based)
```yaml
Activity: Gaming
├─ Power: On (remote.barco_pulse_remote)
├─ Command: profile_Gaming
└─ Command: source_HDMI 2
```

### ⚽ Watch Sports (Multi-command)
```yaml
Activity: Sports
├─ Power: On (remote.barco_pulse_remote)
└─ Commands (sequence):
   ├─ source_HDMI 1
   └─ preset_3
```

### 📊 Presentation Mode
```yaml
Activity: Presentation
├─ Power: On (remote.barco_pulse_remote)
├─ Command: profile_Presentation
└─ Command: source_DisplayPort 1
```

## Button Layout Example

```
┌─────────────────────────────────────────┐
│         UC Remote Display               │
├─────────────────────────────────────────┤
│                                          │
│  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │ 🎬   │  │ 🎮   │  │ ⚽   │          │
│  │Movie │  │Gaming│  │Sports│          │
│  └──────┘  └──────┘  └──────┘          │
│                                          │
│  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │HDMI 1│  │HDMI 2│  │HDMI 3│          │
│  └──────┘  └──────┘  └──────┘          │
│                                          │
│  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │Cinema│  │Bright│  │Custom│          │
│  └──────┘  └──────┘  └──────┘          │
│                                          │
└─────────────────────────────────────────┘
```

Each button sends:
- **Movie**: `preset_1`
- **Gaming**: `preset_2`
- **Sports**: `preset_3`
- **HDMI 1**: `source_HDMI 1`
- **HDMI 2**: `source_HDMI 2`
- **Cinema**: `profile_Cinema`
- etc.

## Troubleshooting Flow

```
Command Not Working?
         │
         ▼
    Is projector
    powered on? ──No──▶ Power on first
         │              (presets/profiles need power)
        Yes
         │
         ▼
    Is command
    spelled correctly? ──No──▶ Check profile names
         │                     (case-sensitive!)
        Yes
         │
         ▼
    Check HA logs:
    Settings → System
    → Logs
         │
         ▼
    Look for:
    "barco_pulse"
    errors
```

## Finding Your Profile Names

```
Home Assistant
└─ Developer Tools
   └─ States
      └─ select.barco_pulse_profile
         └─ Attributes
            └─ options: [
                  "Cinema",
                  "Gaming",
                  "Sports",
                  "Presentation"
               ]
```

Or use Template Tool:
```jinja2
{{ state_attr('select.barco_pulse_profile', 'options') }}
```

## Benefits Summary

| Feature                 | Benefit                     |
| ----------------------- | --------------------------- |
| ✅ Native Remote Support | No workarounds needed       |
| ✅ Activity Integration  | Full automation support     |
| ✅ Command Sequences     | Multiple actions per button |
| ✅ Fast Execution        | Direct API calls            |
| ✅ Simple Syntax         | Easy to remember            |
| ✅ Power Control         | Built-in on/off             |

## Next Steps

1. ✅ Add `remote.barco_pulse_remote` to UC Remote
2. ✅ Create your first activity
3. ✅ Test power on/off
4. ✅ Test a preset command
5. ✅ Build your custom button layout
6. ✅ Enjoy seamless control!

---

For detailed command reference, see:
- [`UNFOLDED_CIRCLE_REMOTE_INTEGRATION.md`](UNFOLDED_CIRCLE_REMOTE_INTEGRATION.md) - Complete guide
- [`UC_REMOTE_QUICK_REFERENCE.md`](UC_REMOTE_QUICK_REFERENCE.md) - Quick command reference
