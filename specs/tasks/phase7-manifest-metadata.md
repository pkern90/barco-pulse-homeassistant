# Phase 7: Manifest and Metadata

## 7.1 Manifest (`custom_components/barco_pulse/manifest.json`)

### Required Fields
- [x] Set `"domain": "barco_pulse"`
- [x] Set `"name": "Barco Pulse"`
- [x] Set `"codeowners": ["@pkern90"]`
- [x] Set `"config_flow": true`
- [x] Set `"integration_type": "device"`
- [x] Set `"iot_class": "local_polling"`
- [x] Set `"version": "1.0.0"`

### Documentation and Support
- [x] Set `"documentation": "https://github.com/pkern90/barco-pulse-homeassistant"`
- [x] Set `"issue_tracker": "https://github.com/pkern90/barco-pulse-homeassistant/issues"`

### Dependencies
- [x] Set `"requirements": []` (no external dependencies)
- [x] Verify no other dependencies needed

## 7.2 Translations (`custom_components/barco_pulse/translations/en.json`)

### Config Flow Translations
- [x] Create `config` section
- [x] Add `step.user.title`: "Connect to Barco Pulse Projector"
- [x] Add `step.user.description`: Connection instructions
- [x] Add `step.user.data.host`: "Host (IP address)"
- [x] Add `step.user.data.port`: "Port"
- [x] Add `step.user.data.auth_code`: "Authentication Code (optional)"
- [x] Add `step.reconfigure.title`: "Reconfigure Barco Pulse Projector"
- [x] Add `step.reconfigure.description`: Update instructions
- [x] Add reconfigure data fields (same as user)

### Error Messages
- [x] Add `error.cannot_connect`: "Cannot connect to projector. Check host and port."
- [x] Add `error.invalid_auth`: "Invalid authentication code."
- [x] Add `error.unknown`: "Unexpected error occurred."

### Abort Messages
- [x] Add `abort.already_configured`: "This projector is already configured."
- [x] Add `abort.reconfigure_successful`: "Configuration updated successfully."

### Binary Sensor Translations
- [x] Add `entity.binary_sensor.power.name`: "Power"

### Sensor Translations
- [x] Add `entity.sensor.state.name`: "State"
- [x] Add `entity.sensor.serial_number.name`: "Serial Number"
- [x] Add `entity.sensor.model_name.name`: "Model"
- [x] Add `entity.sensor.firmware_version.name`: "Firmware"
- [x] Add `entity.sensor.laser_power.name`: "Laser Power"
- [x] Add `entity.sensor.source.name`: "Current Source"

### Switch Translations
- [x] Add `entity.switch.power.name`: "Power"

### Select Translations
- [x] Add `entity.select.source.name`: "Input Source"

### Number Translations
- [x] Add `entity.number.laser_power.name`: "Laser Power"
- [x] Add `entity.number.brightness.name`: "Brightness"
- [x] Add `entity.number.contrast.name`: "Contrast"
- [x] Add `entity.number.saturation.name`: "Saturation"
- [x] Add `entity.number.hue.name`: "Hue"

### Remote Translations
- [x] Add `entity.remote.remote.name`: "Remote Control"

## 7.3 Strings (`custom_components/barco_pulse/strings.json`)

### Copy Translations
- [x] Copy entire content from `translations/en.json`
- [x] Ensure exact match for backward compatibility

## 7.4 Services (Optional - `custom_components/barco_pulse/services.yaml`)

### Service Definitions
- [x] Skip for initial implementation
- [x] Can add custom services later if needed (e.g., lens memory, test patterns)
