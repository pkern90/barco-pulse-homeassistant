# Phase 7: Manifest and Metadata

## 7.1 Manifest (`custom_components/barco_pulse/manifest.json`)

### Required Fields
- [ ] Set `"domain": "barco_pulse"`
- [ ] Set `"name": "Barco Pulse"`
- [ ] Set `"codeowners": ["@pkern90"]`
- [ ] Set `"config_flow": true`
- [ ] Set `"integration_type": "device"`
- [ ] Set `"iot_class": "local_polling"`
- [ ] Set `"version": "1.0.0"`

### Documentation and Support
- [ ] Set `"documentation": "https://github.com/pkern90/barco-pulse-homeassistant"`
- [ ] Set `"issue_tracker": "https://github.com/pkern90/barco-pulse-homeassistant/issues"`

### Dependencies
- [ ] Set `"requirements": []` (no external dependencies)
- [ ] Verify no other dependencies needed

## 7.2 Translations (`custom_components/barco_pulse/translations/en.json`)

### Config Flow Translations
- [ ] Create `config` section
- [ ] Add `step.user.title`: "Connect to Barco Pulse Projector"
- [ ] Add `step.user.description`: Connection instructions
- [ ] Add `step.user.data.host`: "Host (IP address)"
- [ ] Add `step.user.data.port`: "Port"
- [ ] Add `step.user.data.auth_code`: "Authentication Code (optional)"
- [ ] Add `step.reconfigure.title`: "Reconfigure Barco Pulse Projector"
- [ ] Add `step.reconfigure.description`: Update instructions
- [ ] Add reconfigure data fields (same as user)

### Error Messages
- [ ] Add `error.cannot_connect`: "Cannot connect to projector. Check host and port."
- [ ] Add `error.invalid_auth`: "Invalid authentication code."
- [ ] Add `error.unknown`: "Unexpected error occurred."

### Abort Messages
- [ ] Add `abort.already_configured`: "This projector is already configured."
- [ ] Add `abort.reconfigure_successful`: "Configuration updated successfully."

### Binary Sensor Translations
- [ ] Add `entity.binary_sensor.power.name`: "Power"

### Sensor Translations
- [ ] Add `entity.sensor.state.name`: "State"
- [ ] Add `entity.sensor.serial_number.name`: "Serial Number"
- [ ] Add `entity.sensor.model_name.name`: "Model"
- [ ] Add `entity.sensor.firmware_version.name`: "Firmware"
- [ ] Add `entity.sensor.laser_power.name`: "Laser Power"
- [ ] Add `entity.sensor.source.name`: "Current Source"

### Switch Translations
- [ ] Add `entity.switch.power.name`: "Power"

### Select Translations
- [ ] Add `entity.select.source.name`: "Input Source"

### Number Translations
- [ ] Add `entity.number.laser_power.name`: "Laser Power"
- [ ] Add `entity.number.brightness.name`: "Brightness"
- [ ] Add `entity.number.contrast.name`: "Contrast"
- [ ] Add `entity.number.saturation.name`: "Saturation"
- [ ] Add `entity.number.hue.name`: "Hue"

### Remote Translations
- [ ] Add `entity.remote.remote.name`: "Remote Control"

## 7.3 Strings (`custom_components/barco_pulse/strings.json`)

### Copy Translations
- [ ] Copy entire content from `translations/en.json`
- [ ] Ensure exact match for backward compatibility

## 7.4 Services (Optional - `custom_components/barco_pulse/services.yaml`)

### Service Definitions
- [ ] Skip for initial implementation
- [ ] Can add custom services later if needed (e.g., lens memory, test patterns)
