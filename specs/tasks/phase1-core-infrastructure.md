# Phase 1: Core Infrastructure

## 1.1 Exception Hierarchy (`custom_components/barco_pulse/exceptions.py`)

- [ ] Create base `BarcoError` exception class
- [ ] Create `BarcoConnectionError` for connection failures
- [ ] Create `BarcoAuthError` for authentication failures
- [ ] Create `BarcoApiError` with `code` and `message` attributes
- [ ] Create `BarcoStateError` for state-dependent property errors

## 1.2 Constants (`custom_components/barco_pulse/const.py`)

- [ ] Set `DOMAIN = "barco_pulse"`
- [ ] Set `NAME = "Barco Pulse"`
- [ ] Set `ATTRIBUTION` string
- [ ] Define `DEFAULT_PORT = 9090`
- [ ] Define `DEFAULT_TIMEOUT = 10`
- [ ] Define `INTERVAL_FAST = 10` (seconds)
- [ ] Define `INTERVAL_SLOW = 60` (seconds)
- [ ] Define `CONF_AUTH_CODE = "auth_code"`
- [ ] Define `POWER_STATES_ACTIVE = ["on", "ready"]`
- [ ] Define `POWER_STATES_TRANSITIONAL = ["conditioning", "deconditioning"]`
- [ ] Define `POWER_STATES_STANDBY = ["standby", "eco", "boot"]`
- [ ] Define entity attribute keys (`ATTR_LASER_POWER`, `ATTR_SOURCE`, etc.)

## 1.3 Data Models (`custom_components/barco_pulse/data.py`)

- [ ] Import required types (`dataclass`, `BarcoDevice`, `BarcoDataUpdateCoordinator`)
- [ ] Create `BarcoRuntimeData` dataclass with `client` and `coordinator` fields
- [ ] Use `from __future__ import annotations` for forward references

## 1.4 JSON-RPC API Client (`custom_components/barco_pulse/api.py`)

### Core Structure
- [ ] Create `BarcoDevice` class with `__init__(host, port, auth_code, timeout)`
- [ ] Add `_lock: asyncio.Lock` for connection serialization
- [ ] Add `_reader: asyncio.StreamReader` and `_writer: asyncio.StreamWriter`
- [ ] Add `_connected: bool` flag
- [ ] Add `_request_id: int` counter

### Connection Management
- [ ] Implement `async def connect()` using `asyncio.open_connection()`
- [ ] Implement `async def disconnect()` with writer close and wait_closed
- [ ] Handle connection errors and wrap in `BarcoConnectionError`

### HTTP/JSON-RPC Protocol
- [ ] Implement `_build_jsonrpc_request(method, params, id)` returning dict
- [ ] Implement `_build_http_request(json_payload)` returning HTTP POST string
- [ ] Implement `async def _read_json_response()` reading until valid JSON
- [ ] Implement `_parse_jsonrpc_response(response, expected_id)` with error handling
- [ ] Map error code -32601 to `BarcoStateError`
- [ ] Map other error codes to `BarcoApiError`

### Core Request Method
- [ ] Implement `async def _send_request(method, params)` with lock
- [ ] Auto-connect if not connected
- [ ] Generate request ID
- [ ] Build and send HTTP request
- [ ] Read and parse JSON response
- [ ] Return result or raise exception

### Authentication
- [ ] Implement `async def authenticate(code)` calling `authenticate` method
- [ ] Return bool for success/failure
- [ ] Raise `BarcoAuthError` on authentication failure

### System Methods
- [ ] Implement `async def get_state()` using `property.get` for `system.state`
- [ ] Implement `async def power_on()` using `system.poweron`
- [ ] Implement `async def power_off()` using `system.poweroff`

### Property Methods
- [ ] Implement `async def get_property(property)` using `property.get`
- [ ] Implement `async def get_properties(properties)` using batch `property.get`
- [ ] Implement `async def set_property(property, value)` using `property.set`

### Source Methods
- [ ] Implement `async def get_source()` getting `image.window.main.source`
- [ ] Implement `async def get_available_sources()` using `image.source.list`
- [ ] Implement `async def set_source(source)` setting `image.window.main.source`

### Illumination Methods
- [ ] Implement `async def get_laser_power()` getting `illumination.sources.laser.power`
- [ ] Implement `async def set_laser_power(power)` setting laser power
- [ ] Implement `async def get_laser_limits()` returning tuple of (min, max)

### Picture Methods
- [ ] Implement `async def get_brightness()` getting `image.brightness`
- [ ] Implement `async def set_brightness(value)` setting brightness
- [ ] Implement `async def get_contrast()` getting `image.contrast`
- [ ] Implement `async def set_contrast(value)` setting contrast
- [ ] Implement `async def get_saturation()` getting `image.saturation`
- [ ] Implement `async def set_saturation(value)` setting saturation
- [ ] Implement `async def get_hue()` getting `image.hue`
- [ ] Implement `async def set_hue(value)` setting hue

### Info Methods
- [ ] Implement `async def get_serial_number()` getting `system.serialnumber`
- [ ] Implement `async def get_model_name()` getting `system.modelname`
- [ ] Implement `async def get_firmware_version()` getting `system.firmwareversion`

### Error Handling
- [ ] Handle `asyncio.TimeoutError` and wrap in `BarcoConnectionError`
- [ ] Handle `ConnectionError` and wrap in `BarcoConnectionError`
- [ ] Handle `json.JSONDecodeError` and wrap in `BarcoApiError`
