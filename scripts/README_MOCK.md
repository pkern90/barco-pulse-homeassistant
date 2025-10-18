# Mock Barco Pulse Projector Server

This script simulates a Barco Pulse projector for testing the Home Assistant integration without requiring actual hardware.

## Usage

### Start the mock server

```bash
# Listen on all interfaces (0.0.0.0) on port 9090 (default)
python3 scripts/mock_projector.py

# Listen on specific host/port
python3 scripts/mock_projector.py 192.168.30.206 9090
```

### Test the mock server

In another terminal:

```bash
# Connect and send a test request
echo '{"jsonrpc":"2.0","method":"property.get","params":{"property":"system.serialnumber"},"id":1}' | nc localhost 9090
```

Expected response:
```json
{"jsonrpc": "2.0", "result": "MOCK123456", "id": 1}
```

## Supported Methods

The mock server implements the following JSON-RPC 2.0 methods:

- `authenticate` - Accepts any 5-digit code (10000-99999)
- `property.get` - Get single or multiple properties
- `property.set` - Set a property value
- `system.poweron` - Power on the projector
- `system.poweroff` - Power off the projector

## Mock Data

Default property values:
- `system.serialnumber`: "MOCK123456"
- `system.modelname`: "Barco Pulse (Mock)"
- `system.firmwareversion`: "1.0.0-mock"
- `system.state`: "on"
- `image.window.main.source`: "DisplayPort 1"

Properties can be modified using `property.set` and the changes persist for the duration of the server session.

## Use with Home Assistant Integration

1. Start the mock server:
   ```bash
   python3 scripts/mock_projector.py 192.168.30.206 9090
   ```

2. In Home Assistant, configure the integration with:
   - Host: 192.168.30.206
   - Port: 9090
   - Auth Code: Any 5-digit number (e.g., 12345)

The integration should successfully connect and retrieve projector information.
