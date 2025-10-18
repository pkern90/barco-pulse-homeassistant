# Test Coverage

This directory contains comprehensive tests for the Barco Pulse Home Assistant integration.

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_api.py` - API client tests (connection, JSON-RPC, error handling)
- `test_config_flow.py` - Configuration flow tests (user setup, validation, errors)
- `test_coordinator.py` - Data coordinator tests (updates, error handling)
- `test_init.py` - Integration initialization tests (setup, unload, reload)
- `test_sensor.py` - Sensor entity tests
- `test_switch.py` - Switch entity tests
- `test_binary_sensor.py` - Binary sensor entity tests

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_api.py
```

### Run specific test:
```bash
pytest tests/test_api.py::TestBarcoPulseApiClient::test_connect_success
```

### Run with coverage:
```bash
pytest --cov=custom_components.barco_pulse --cov-report=html
```

## Test Coverage

The test suite covers:

### API Client (`test_api.py`)
- Connection management (connect, disconnect, timeout, errors)
- Authentication (success, failure)
- JSON-RPC method calls (success, error responses)
- Power control (on, off)
- Property management (get, set, single, multiple)
- System information retrieval
- Source management (list, get active, set active)
- Illumination control (laser power get/set)

### Config Flow (`test_config_flow.py`)
- User flow with valid credentials
- User flow with authentication code
- Connection errors
- Authentication errors
- Unknown errors
- Duplicate detection (already configured)

### Coordinator (`test_coordinator.py`)
- Successful data updates
- Power state detection (on/off)
- Connection error handling
- Authentication error handling
- API error handling

### Integration Init (`test_init.py`)
- Successful entry setup
- Connection failure handling
- Entry unload
- Entry reload

### Entity Platforms
- **Sensors** (`test_sensor.py`)
  - Platform setup
  - System state sensor
  - Laser power sensor
  - Active source sensor
  - Firmware version sensor
  - Unavailable state handling

- **Switches** (`test_switch.py`)
  - Platform setup
  - Power switch (on/off state)
  - Turn on action
  - Turn off action
  - Unavailable state handling

- **Binary Sensors** (`test_binary_sensor.py`)
  - Platform setup
  - Power status (on/off)
  - Unavailable state handling

## Fixtures

Common fixtures defined in `conftest.py`:

- `mock_barco_pulse_api` - Mocked API client with all methods
- `mock_config_entry` - Mocked config entry
- `mock_coordinator` - Mocked data coordinator
- `coordinator_data` - Sample coordinator data
- `auto_enable_custom_integrations` - Enables custom integration loading

## Notes

- Tests use `pytest-homeassistant-custom-component` for HA test utilities
- All async tests are automatically handled by `pytest-asyncio`
- Mocks are used extensively to avoid actual network connections
- Lint errors about `assert` usage in tests are expected and acceptable
