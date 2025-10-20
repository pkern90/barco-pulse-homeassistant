# Phase 1: Core Infrastructure

## 1.1 Exception Hierarchy (`custom_components/barco_pulse/exceptions.py`)

- [x] Create base `BarcoError` exception class
- [x] Create `BarcoConnectionError` for connection failures
- [x] Create `BarcoAuthError` for authentication failures
- [x] Create `BarcoApiError` with `code` and `message` attributes
- [x] Create `BarcoStateError` for state-dependent property errors

## 1.2 Constants (`custom_components/barco_pulse/const.py`)

- [x] Set `DOMAIN = "barco_pulse"`
- [x] Set `NAME = "Barco Pulse"`
- [x] Set `ATTRIBUTION` string
- [x] Define `DEFAULT_PORT = 9090`
- [x] Define `DEFAULT_TIMEOUT = 10`
- [x] Define `INTERVAL_FAST = 10` (seconds)
- [x] Define `INTERVAL_SLOW = 60` (seconds)
- [x] Define `CONF_AUTH_CODE = "auth_code"`
- [x] Define `POWER_STATES_ACTIVE = ["on", "ready"]`
- [x] Define `POWER_STATES_TRANSITIONAL = ["conditioning", "deconditioning"]`
- [x] Define `POWER_STATES_STANDBY = ["standby", "eco", "boot"]`
- [x] Define entity attribute keys (`ATTR_LASER_POWER`, `ATTR_SOURCE`, etc.)

## 1.3 Data Models (`custom_components/barco_pulse/data.py`)

- [x] Import required types (`dataclass`, `BarcoDevice`, `BarcoDataUpdateCoordinator`)
- [x] Create `BarcoRuntimeData` dataclass with `client` and `coordinator` fields
- [x] Use `from __future__ import annotations` for forward references

## 1.4 JSON-RPC API Client (`custom_components/barco_pulse/api.py`)

### Core Structure
- [x] Create `BarcoDevice` class with `__init__(host, port, auth_code, timeout)`
- [x] Add `_lock: asyncio.Lock` for connection serialization
- [x] Add `_reader: asyncio.StreamReader` and `_writer: asyncio.StreamWriter`
- [x] Add `_connected: bool` flag
- [x] Add `_request_id: int` counter

### Connection Management
- [x] Implement `async def connect()` using `asyncio.open_connection()`
- [x] Implement `async def disconnect()` with writer close and wait_closed
- [x] Handle connection errors and wrap in `BarcoConnectionError`

### HTTP/JSON-RPC Protocol
- [x] Implement `_build_jsonrpc_request(method, params, id)` returning dict
- [x] Implement `_build_http_request(json_payload)` returning HTTP POST string
- [x] Implement `async def _read_json_response()` reading until valid JSON
- [x] Implement `_parse_jsonrpc_response(response, expected_id)` with error handling
- [x] Map error code -32601 to `BarcoStateError`
- [x] Map other error codes to `BarcoApiError`

### Core Request Method
- [x] Implement `async def _send_request(method, params)` with lock
- [x] Auto-connect if not connected
- [x] Generate request ID
- [x] Build and send HTTP request
- [x] Read and parse JSON response
- [x] Return result or raise exception

### Authentication
- [x] Implement `async def authenticate(code)` calling `authenticate` method
- [x] Return bool for success/failure
- [x] Raise `BarcoAuthError` on authentication failure

### System Methods
- [x] Implement `async def get_state()` using `property.get` for `system.state`
- [x] Implement `async def power_on()` using `system.poweron`
- [x] Implement `async def power_off()` using `system.poweroff`

### Property Methods
- [x] Implement `async def get_property(property)` using `property.get`
- [x] Implement `async def get_properties(properties)` using batch `property.get`
- [x] Implement `async def set_property(property, value)` using `property.set`

### Source Methods
- [x] Implement `async def get_source()` getting `image.window.main.source`
- [x] Implement `async def get_available_sources()` using `image.source.list`
- [x] Implement `async def set_source(source)` setting `image.window.main.source`

### Illumination Methods
- [x] Implement `async def get_laser_power()` getting `illumination.sources.laser.power`
- [x] Implement `async def set_laser_power(power)` setting laser power
- [x] Implement `async def get_laser_limits()` returning tuple of (min, max)

### Picture Methods
- [x] Implement `async def get_brightness()` getting `image.brightness`
- [x] Implement `async def set_brightness(value)` setting brightness
- [x] Implement `async def get_contrast()` getting `image.contrast`
- [x] Implement `async def set_contrast(value)` setting contrast
- [x] Implement `async def get_saturation()` getting `image.saturation`
- [x] Implement `async def set_saturation(value)` setting saturation
- [x] Implement `async def get_hue()` getting `image.hue`
- [x] Implement `async def set_hue(value)` setting hue

### Info Methods
- [x] Implement `async def get_serial_number()` getting `system.serialnumber`
- [x] Implement `async def get_model_name()` getting `system.modelname`
- [x] Implement `async def get_firmware_version()` getting `system.firmwareversion`

### Error Handling
- [x] Handle `asyncio.TimeoutError` and wrap in `BarcoConnectionError`
- [x] Handle `ConnectionError` and wrap in `BarcoConnectionError`
- [x] Handle `json.JSONDecodeError` and wrap in `BarcoApiError`
