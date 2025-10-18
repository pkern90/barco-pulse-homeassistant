# Barco Pulse Home Assistant Integration - Implementation Plan

## Project Status

Template-based skeleton with placeholder API. Goal: Transform into functional Barco Pulse projector integration using JSON-RPC 2.0 API over TCP (port 9090).

## Core Objectives

1. Rename all `integration_blueprint` references to `barco_pulse`
2. Implement JSON-RPC 2.0 TCP client in `api.py`
3. Create coordinator data model for projector state
4. Implement entities (sensors, switches, binary sensors)
5. Update config flow for projector setup
6. Handle errors and state management

---

## Phase 1: Foundation & Renaming

### 1.1 Update Constants and Metadata

**Files:** `const.py`, `manifest.json`

**Tasks:**
- [x] `const.py`: Change `DOMAIN` to `"barco_pulse"`, update `ATTRIBUTION`
- [x] `manifest.json`: Update domain, name, iot_class to `"local_polling"`

### 1.2 Rename All Classes

**Files:** `data.py`, `__init__.py`, `coordinator.py`, `entity.py`, all platform files

**Tasks:**
- [x] `IntegrationBlueprintData` → `BarcoPulseData`
- [x] `IntegrationBlueprintConfigEntry` → `BarcoPulseConfigEntry`
- [x] `BlueprintDataUpdateCoordinator` → `BarcoPulseDataUpdateCoordinator`
- [x] `IntegrationBlueprintEntity` → `BarcoPulseEntity`
- [x] Entity classes: `IntegrationBlueprintSensor` → `BarcoPulseSensor`, etc.
- [x] Update all imports and type hints

---

## Phase 2: JSON-RPC 2.0 TCP API Client

**File:** `api.py`

### 2.1 API Client Structure

```python
class BarcoPulseApiClient:
    def __init__(self, host: str, port: int = 9090, auth_code: int | None = None)
    
    # Connection
    async def connect() -> None
    async def disconnect() -> None
    
    # Core JSON-RPC
    async def call_method(method: str, params: dict | None = None) -> Any
    
    # Power control
    async def power_on() -> None
    async def power_off() -> None
    
    # Property access
    async def get_property(property_name: str | list[str]) -> Any
    async def set_property(property_name: str, value: Any) -> None
    
    # State queries
    async def get_system_state() -> str
    async def get_system_info() -> dict
    
    # Source management
    async def list_sources() -> list[str]
    async def get_active_source() -> str
    async def set_active_source(source: str) -> None
    
    # Illumination
    async def get_laser_power() -> float
    async def set_laser_power(power: float) -> None
    
    # Internal
    async def _read_loop() -> None
    async def _send_request(request: dict) -> dict
```

### 2.2 JSON-RPC Protocol

**Request:** `{"jsonrpc":"2.0","method":str,"params":dict,"id":int}`  
**Response:** `{"jsonrpc":"2.0","result":any,"id":int}` or `{"jsonrpc":"2.0","error":{...},"id":int}`  
**Notification:** `{"jsonrpc":"2.0","method":str,"params":dict}` (no id)

### 2.3 Exception Classes

```python
class BarcoPulseApiError(Exception): pass
class BarcoPulseConnectionError(BarcoPulseApiError): pass
class BarcoPulseAuthenticationError(BarcoPulseApiError): pass
class BarcoPulseTimeoutError(BarcoPulseApiError): pass
class BarcoPulseCommandError(BarcoPulseApiError): pass
```

### 2.4 Implementation Tasks

**Core Transport:**
- [x] TCP connection with `asyncio.open_connection()` and timeouts
- [x] Request ID generator (incrementing int)
- [x] JSON-RPC message encode/decode
- [x] Background `_read_loop()` for responses
- [x] Request/response correlation using Future dict
- [x] Disconnect cleanup

**Domain Methods:**
- [x] Authentication (`authenticate` method)
- [x] Power control (`system.poweron`, `system.poweroff`)
- [x] Property get/set (`property.get`, `property.set`)
- [x] Source management (`image.source.list`, get/set active source)
- [x] Illumination control (get/set laser power)
- [x] System info (`get_system_info` for serial, model, firmware)

**Error Handling:**
- [x] Connection errors → `BarcoPulseConnectionError`
- [x] Timeouts → `BarcoPulseTimeoutError`
- [x] Auth failures → `BarcoPulseAuthenticationError`
- [x] JSON-RPC errors → `BarcoPulseCommandError`
- [x] Reconnect logic with exponential backoff (handled via disconnect/connect)

**Logging:**
- [x] Logger: `custom_components.barco_pulse`
- [x] Log state transitions (INFO), requests/responses (DEBUG)
- [x] Redact auth codes in logs

**Integration Updates:**
- [x] Updated `config_flow.py` to use host/port/auth_code configuration
- [x] Updated `__init__.py` to connect client on setup and disconnect on unload
- [x] Updated `coordinator.py` to fetch projector data and build data model
- [x] Updated `const.py` with new configuration constants
- [x] Updated `translations/en.json` for new config fields
- [x] All code passes linting checks

**Status:** ✅ **COMPLETED**

---

## Phase 3: Data Coordinator

**File:** `coordinator.py`

### 3.1 Data Model

```python
{
    "system": {
        "state": str,  # "on", "standby", "ready", "eco", "conditioning", etc.
        "serial_number": str,
        "model_name": str,
        "firmware_version": str,
    },
    "power": {
        "is_on": bool,  # Derived from state
    },
    "source": {
        "active": str,
        "available": list[str],
    },
    "illumination": {
        "laser_power": float,  # Percentage
    },
}
```

### 3.2 Implementation Tasks

- [ ] Update `_async_update_data()` to fetch properties from API client
- [ ] Call `get_system_state()`, `get_system_info()`, `get_active_source()`, `list_sources()`, `get_laser_power()`
- [ ] Build coordinator data dict with fetched values
- [ ] Derive `power.is_on` from `system.state`
- [ ] Map API exceptions to `UpdateFailed` or `ConfigEntryAuthFailed`
- [ ] Set update interval: 30 seconds for MVP (adjust later based on state)

---

## Phase 4: Entity Implementation

### 4.1 Sensors

**File:** `sensor.py`

**Entities:**
- `system_state`: Projector State (current state: on, standby, etc.)
- `laser_power`: Laser Power (%)
- `active_source`: Active Source
- `firmware_version`: Firmware Version

**Tasks:**
- [ ] Define `ENTITY_DESCRIPTIONS` with `SensorEntityDescription`
- [ ] Implement `BarcoPulseSensor` class
- [ ] Map `coordinator.data` to `native_value`
- [ ] Set device class, units, icons

### 4.2 Switches

**File:** `switch.py`

**Entities:**
- `power`: Power switch (turn projector on/off)

**Tasks:**
- [ ] Define `ENTITY_DESCRIPTIONS`
- [ ] Implement `BarcoPulseSwitch` class
- [ ] `is_on` from `coordinator.data["power"]["is_on"]`
- [ ] `async_turn_on()`: call `client.power_on()`, then `coordinator.async_request_refresh()`
- [ ] `async_turn_off()`: call `client.power_off()`, then refresh
- [ ] Handle state validation (don't turn on if already on)

### 4.3 Binary Sensors

**File:** `binary_sensor.py`

**Entities:**
- `power_status`: Is projector powered on (device class: power)

**Tasks:**
- [ ] Define `ENTITY_DESCRIPTIONS`
- [ ] Implement `BarcoPulseBinarySensor`
- [ ] Map `coordinator.data` to `is_on`

---

## Phase 5: Configuration Flow

**File:** `config_flow.py`

### 5.1 Update Config Flow

**New flow fields:**
- Host (IP address or hostname) - required
- Port (default: 9090) - optional
- Authentication code (5-digit integer) - optional
- Projector name (friendly name) - optional

**Tasks:**
- [ ] Update `STEP_USER_DATA_SCHEMA` with new fields (host, port, auth_code, name)
- [ ] Test connection in `async_step_user()`: create API client, call `connect()` and `get_system_info()`
- [ ] If auth code provided, call `authenticate()`
- [ ] Set unique ID to serial number from system info (or hash of host if unavailable)
- [ ] Handle errors: `cannot_connect`, `invalid_auth`, `timeout`
- [ ] Update `translations/en.json` with new field labels and error messages

---

## Phase 6: Testing & Validation

### 6.1 Manual Testing Checklist

**Setup:**
- [ ] Add integration via UI with valid host/port
- [ ] Test with invalid host (should show error)
- [ ] Test with authentication code

**Power Control:**
- [ ] Turn projector on via switch
- [ ] Verify state sensor updates
- [ ] Turn projector off
- [ ] Test turning on when already on

**Source Control:**
- [ ] Change input source (if select entity implemented)
- [ ] Verify active source sensor updates

**Error Handling:**
- [ ] Disconnect network during operation
- [ ] Verify entities become unavailable
- [ ] Reconnect and verify recovery

### 6.2 Code Quality

- [ ] Run `scripts/lint` and fix all issues
- [ ] Add type hints to all functions
- [ ] Add docstrings to public methods
- [ ] Remove template comments and placeholders

---

## Phase 7: Optional Enhancements

### 7.1 Select Entity for Source Selection
- [ ] Create `select.py` with source selector entity
- [ ] Populate options from `coordinator.data["source"]["available"]`
- [ ] Implement `async_select_option()` to call `client.set_active_source()`

### 7.2 Number Entity for Laser Power
- [ ] Create `number.py` with laser power slider
- [ ] Set min/max from projector capabilities
- [ ] Implement `async_set_native_value()` to call `client.set_laser_power()`

### 7.3 Property Subscriptions
- [ ] Use `property.subscribe` for real-time updates
- [ ] Handle `property.changed` notifications in API client
- [ ] Update coordinator data on notification
- [ ] Reduce polling interval

---

## Implementation Priority

### MVP (Required)
**Phases:** 1, 2 (core methods), 3, 4.1-4.3, 5, 6  
**Focus:** Basic power control, state monitoring, config flow  
**Time:** ~25-35 hours

### v1.0 (Enhanced)
**Phases:** Complete all MVP + Phase 7 optional enhancements  
**Focus:** Full feature set with source selection, laser power control  
**Time:** ~40-50 hours

### v1.1+ (Future)
**Focus:** Custom services, discovery, advanced entities  
**Time:** ~15-25 hours

---

## Quick Reference

### Key API Methods for Coordinator
```python
# Required for MVP
client.get_system_state() -> str
client.get_system_info() -> dict  # serial, model, firmware
client.get_active_source() -> str
client.list_sources() -> list[str]
client.get_laser_power() -> float
client.power_on()
client.power_off()
```

### Exception Mapping
- `BarcoPulseConnectionError` → `cannot_connect` in config flow, `UpdateFailed` in coordinator
- `BarcoPulseAuthenticationError` → `invalid_auth` in config flow, `ConfigEntryAuthFailed` in coordinator
- `BarcoPulseTimeoutError` → `timeout` in config flow, `UpdateFailed` in coordinator
- `BarcoPulseCommandError` → `UpdateFailed` in coordinator

### Config Flow Fields
- `host`: str (required)
- `port`: int (default 9090)
- `auth_code`: int (optional, 5 digits)
- `name`: str (optional)

### Property Paths (from pulse-api-docs.md)
```python
"system.state"                    # State: on, standby, ready, eco, etc.
"system.serialnumber"             # Serial number
"system.modelname"                # Model name
"system.firmwareversion"          # Firmware version
"image.window.main.source"        # Active source
"illumination.sources.laser.power" # Laser power (0-100)
```
