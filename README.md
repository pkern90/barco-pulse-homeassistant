# Barco Pulse Home Assistant Integration

A custom Home Assistant integration for controlling Barco Pulse projectors.

## Features

- **Power Control**: Turn your projector on/off
- **Input Source Selection**: Switch between HDMI, DisplayPort, and other inputs
- **Illumination Control**: Adjust laser power settings
- **Picture Settings**: Control brightness, contrast, and other picture parameters
- **Status Monitoring**: Monitor projector state, temperature, and runtime hours

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Add this repository as a custom repository
3. Search for "Barco Pulse" and install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/barco_pulse` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Barco Pulse"
4. Enter your projector's IP address
5. (Optional) Enter the authentication code if your projector requires one

## Supported Entities

- **Binary Sensors**: Connection status, signal detection
- **Sensors**: Power state, runtime hours, temperature
- **Switches**: Power control
- **Select**: Input source selection, preset activation, profile activation
- **Number**: Illumination power, picture adjustments
- **Remote**: Send remote control commands (compatible with Unfolded Circle Remote 3)

## Unfolded Circle Remote 3 Support

This integration is fully compatible with the **Unfolded Circle Remote 3**! The `remote.barco_pulse_remote` entity supports:

- Power control (on/off)
- Input source switching (`source_HDMI 1`, etc.)
- Preset activation (`preset_0` through `preset_29`)
- Profile activation (`profile_Cinema`, `profile_Gaming`, etc.)

**Quick Start**:
```yaml
# Activate Cinema preset
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command: preset_1

# Switch to HDMI 1 and activate Gaming profile
service: remote.send_command
target:
  entity_id: remote.barco_pulse_remote
data:
  command:
    - source_HDMI 1
    - profile_Gaming
```

📖 **See**: [`UNFOLDED_CIRCLE_REMOTE_INTEGRATION.md`](UNFOLDED_CIRCLE_REMOTE_INTEGRATION.md) for complete UC Remote setup guide

🚀 **Quick Reference**: [`UC_REMOTE_QUICK_REFERENCE.md`](UC_REMOTE_QUICK_REFERENCE.md) for command examples

## Requirements

- Home Assistant 2024.1.0 or newer
- Barco Pulse projector with network connectivity
- Projector must be accessible on the network. Make sure your firewall allows TCP connections to the corresponding port (default: 9090).

## Compatibility

This integration has only been tested with the Barco Hodr CS projector. It uses the Barco Pulse JSON-RPC API for communication.

## Support

For issues and feature requests, please use the [GitHub issue tracker](../../issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
