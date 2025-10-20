# Barco Pulse Home Assistant Integration - Implementation Plan

**Version:** 1.0  
**Date:** October 20, 2025  
**Target:** Production-ready HACS custom integration  
**Reference:** JVC Projector integration architecture pattern

---

## Architecture Overview

**Pattern:** Home Assistant DataUpdateCoordinator with platform-based entities  
**Protocol:** JSON-RPC 2.0 over hybrid HTTP/0.9 TCP socket (port 9090)  
**State Management:** State-aware polling with dynamic update intervals  
**Device Model:** Single projector device with multiple platform entities

---

## Critical Protocol Constraints

1. **Transport:** Raw TCP sockets required (no HTTP libraries)
2. **Request:** HTTP/1.1 POST with JSON-RPC 2.0 payload
3. **Response:** Raw JSON without HTTP headers (HTTP/0.9-like)
4. **State Dependency:** Many properties only available in `on`/`ready` states
5. **Error Code -32601:** "Property not found" - handle gracefully for state-dependent properties

---

## Component Implementation Sequence

### Phase 1: Core Infrastructure

#### 1.1 Exception Hierarchy (`exceptions.py`)
```python
class BarcoError(Exception): pass
class BarcoConnectionError(BarcoError): pass
class BarcoAuthError(BarcoError): pass
class BarcoApiError(BarcoError):
    def __init__(self, code: int, message: str)
class BarcoStateError(BarcoError): pass
```

#### 1.2 Constants (`const.py`)
```python
DOMAIN = "barco_pulse"
NAME = "Barco Pulse"
ATTRIBUTION = "Data provided by Barco Pulse projector"

DEFAULT_PORT = 9090
DEFAULT_TIMEOUT = 10
INTERVAL_FAST = 10  # seconds (when on)
INTERVAL_SLOW = 60  # seconds (when standby)

CONF_AUTH_CODE = "auth_code"

POWER_STATES_ACTIVE = ["on", "ready"]
POWER_STATES_TRANSITIONAL = ["conditioning", "deconditioning"]
POWER_STATES_STANDBY = ["standby", "eco", "boot"]

ATTR_LASER_POWER = "laser_power"
ATTR_SOURCE = "source"
# ... entity attribute keys
```

#### 1.3 Data Models (`data.py`)
```python
@dataclass
class BarcoRuntimeData:
    """Runtime data stored in config entry."""
    client: BarcoDevice
    coordinator: BarcoDataUpdateCoordinator
```

#### 1.4 JSON-RPC API Client (`api.py`)

**Core Requirements:**
- Raw TCP socket connection with asyncio streams
- Manual HTTP request construction
- JSON-RPC 2.0 request/response handling
- Graceful parsing of headerless responses
- Connection pooling with lock
- Timeout and retry logic
- Error code mapping to exceptions

**Key Methods:**
```python
class BarcoDevice:
    async def connect() -> None
    async def disconnect() -> None
    async def _send_request(method: str, params: dict | None) -> Any
    async def authenticate(code: int | None) -> bool
    
    # System
    async def get_state() -> str
    async def power_on() -> None
    async def power_off() -> None
    
    # Properties
    async def get_property(property: str) -> Any
    async def get_properties(properties: list[str]) -> dict[str, Any]
    async def set_property(property: str, value: Any) -> bool
    
    # Sources
    async def get_source() -> str | None
    async def get_available_sources() -> list[str]
    async def set_source(source: str) -> bool
    
    # Illumination
    async def get_laser_power() -> int | None
    async def set_laser_power(power: int) -> bool
    async def get_laser_limits() -> tuple[int, int]
    
    # Picture
    async def get_brightness() -> float | None
    async def set_brightness(value: float) -> bool
    # ... contrast, saturation, hue
    
    # Info
    async def get_serial_number() -> str
    async def get_model_name() -> str
    async def get_firmware_version() -> str
```

**Socket Implementation Pattern:**
```python
async def _send_request(self, method: str, params: dict | None = None) -> Any:
    async with self._lock:
        if not self._connected:
            await self.connect()
        
        request_id = self._next_id()
        payload = self._build_jsonrpc_request(method, params, request_id)
        http_request = self._build_http_request(payload)
        
        self._writer.write(http_request.encode("utf-8"))
        await self._writer.drain()
        
        response_json = await self._read_json_response()
        return self._parse_jsonrpc_response(response_json, request_id)

async def _read_json_response(self) -> str:
    """Read raw JSON response (no HTTP headers)."""
    buffer = ""
    while True:
        chunk = await asyncio.wait_for(
            self._reader.read(4096), timeout=self._timeout
        )
        if not chunk:
            raise BarcoConnectionError("Connection closed")
        buffer += chunk.decode("utf-8")
        try:
            json.loads(buffer)  # Test if complete
            return buffer
        except json.JSONDecodeError:
            continue  # Need more data
```

**Error Handling:**
```python
def _parse_jsonrpc_response(self, response: str, expected_id: int) -> Any:
    data = json.loads(response)
    
    if "error" in data:
        code = data["error"]["code"]
        message = data["error"]["message"]
        
        if code == -32601:  # Property not found
            raise BarcoStateError(f"Property unavailable: {message}")
        raise BarcoApiError(code, message)
    
    return data.get("result")
```

### Phase 2: Coordinator

#### 2.1 Data Update Coordinator (`coordinator.py`)

**Core Responsibilities:**
- State-aware property polling
- Dynamic update interval based on power state
- Connection lifecycle management
- Rate limiting
- Error recovery

**Structure:**
```python
class BarcoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, device: BarcoDevice) -> None:
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=NAME,
            update_interval=timedelta(seconds=INTERVAL_SLOW),
        )
        self.device = device
        self._connection_lock = asyncio.Lock()
        self._update_lock = asyncio.Lock()
        self._last_update = 0.0
        
    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from device."""
        async with self._update_lock:
            try:
                # Rate limiting
                await self._enforce_rate_limit()
                
                # Always fetch state
                state = await self.device.get_state()
                data = {"state": state}
                
                # Fetch info properties (always available)
                data.update(await self._get_info_properties())
                
                # State-dependent properties
                if state in POWER_STATES_ACTIVE:
                    data.update(await self._get_active_properties())
                    self.update_interval = timedelta(seconds=INTERVAL_FAST)
                else:
                    self.update_interval = timedelta(seconds=INTERVAL_SLOW)
                
                return data
                
            except BarcoConnectionError as err:
                raise UpdateFailed(f"Connection error: {err}")
            except BarcoAuthError as err:
                raise ConfigEntryAuthFailed(f"Authentication failed: {err}")
            except BarcoStateError:
                # Expected when properties unavailable in current state
                return data
            except Exception as err:
                raise UpdateFailed(f"Unexpected error: {err}")
    
    async def _get_info_properties(self) -> dict[str, Any]:
        """Get always-available info properties."""
        props = ["system.serialnumber", "system.modelname", "system.firmwareversion"]
        return await self.device.get_properties(props)
    
    async def _get_active_properties(self) -> dict[str, Any]:
        """Get properties only available when projector is on."""
        data = {}
        
        try:
            # Illumination
            data["laser_power"] = await self.device.get_laser_power()
            laser_min, laser_max = await self.device.get_laser_limits()
            data["laser_min"] = laser_min
            data["laser_max"] = laser_max
            
            # Source
            data["source"] = await self.device.get_source()
            data["available_sources"] = await self.device.get_available_sources()
            
            # Picture
            data["brightness"] = await self.device.get_brightness()
            data["contrast"] = await self.device.get_contrast()
            data["saturation"] = await self.device.get_saturation()
            data["hue"] = await self.device.get_hue()
            
        except BarcoStateError:
            # Property not available in current state
            pass
        
        return data
    
    async def _enforce_rate_limit(self) -> None:
        """Prevent request flooding."""
        min_interval = 1.0  # seconds
        elapsed = time.time() - self._last_update
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        self._last_update = time.time()
```

### Phase 3: Config Flow

#### 3.1 Configuration Flow (`config_flow.py`)

**Features:**
- Host/port entry
- Optional authentication code
- Connection validation
- Unique ID from serial number
- Reconfiguration support

**Structure:**
```python
class BarcoConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    
    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle user-initiated configuration."""
        errors = {}
        
        if user_input is not None:
            try:
                # Validate connection
                device = BarcoDevice(
                    user_input[CONF_HOST],
                    user_input.get(CONF_PORT, DEFAULT_PORT),
                    user_input.get(CONF_AUTH_CODE),
                )
                
                await device.connect()
                
                # Get unique identifier
                serial = await device.get_serial_number()
                await self.async_set_unique_id(serial)
                self._abort_if_unique_id_configured()
                
                # Get device info for title
                model = await device.get_model_name()
                
                await device.disconnect()
                
                return self.async_create_entry(
                    title=f"{model} ({user_input[CONF_HOST]})",
                    data=user_input,
                )
                
            except BarcoConnectionError:
                errors["base"] = "cannot_connect"
            except BarcoAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_AUTH_CODE): int,
            }),
            errors=errors,
        )
    
    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Handle reconfiguration."""
        # Similar to async_step_user but updates existing entry
```

### Phase 4: Integration Setup

#### 4.1 Integration Init (`__init__.py`)

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Barco Pulse from config entry."""
    
    # Create device client
    device = BarcoDevice(
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
        entry.data.get(CONF_AUTH_CODE),
    )
    
    # Connect and authenticate
    try:
        await device.connect()
    except BarcoConnectionError as err:
        raise ConfigEntryNotReady(f"Cannot connect: {err}")
    
    # Create coordinator
    coordinator = BarcoDataUpdateCoordinator(hass, device)
    
    # Initial data fetch
    await coordinator.async_config_entry_first_refresh()
    
    # Store runtime data
    entry.runtime_data = BarcoRuntimeData(client=device, coordinator=coordinator)
    
    # Register shutdown handler
    async def _async_close_connection(_event: Event) -> None:
        await device.disconnect()
    
    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_close_connection)
    )
    
    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        await entry.runtime_data.client.disconnect()
    
    return unload_ok
```

### Phase 5: Base Entity

#### 5.1 Base Entity Class (`entity.py`)

```python
class BarcoEntity(CoordinatorEntity[BarcoDataUpdateCoordinator]):
    """Base entity for Barco Pulse."""
    
    _attr_has_entity_name = True
    
    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.config_entry.title,
            manufacturer="Barco",
            model=coordinator.data.get("system.modelname", "Pulse"),
            sw_version=coordinator.data.get("system.firmwareversion"),
        )
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
```

### Phase 6: Platform Entities

#### 6.1 Binary Sensors (`binary_sensor.py`)

**Entities:**
- Power State (on/off derived from `system.state`)

```python
@dataclass(frozen=True, kw_only=True)
class BarcoBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Barco binary sensor entity description."""
    value_fn: Callable[[dict[str, Any]], bool | None]

BINARY_SENSORS = [
    BarcoBinarySensorEntityDescription(
        key="power",
        translation_key="power",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: data.get("state") in POWER_STATES_ACTIVE,
    ),
]

class BarcoBinarySensor(BarcoEntity, BinarySensorEntity):
    """Barco binary sensor entity."""
    
    entity_description: BarcoBinarySensorEntityDescription
    
    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data)
```

#### 6.2 Sensors (`sensor.py`)

**Entities:**
- System State (text sensor showing full state)
- Serial Number
- Model Name
- Firmware Version
- Laser Power (percentage)
- Active Source (input name)

```python
@dataclass(frozen=True, kw_only=True)
class BarcoSensorEntityDescription(SensorEntityDescription):
    """Barco sensor entity description."""
    value_fn: Callable[[dict[str, Any]], str | int | None]
    enabled_default: bool = True

SENSORS = [
    BarcoSensorEntityDescription(
        key="state",
        translation_key="state",
        icon="mdi:power",
        value_fn=lambda data: data.get("state"),
    ),
    BarcoSensorEntityDescription(
        key="serial_number",
        translation_key="serial_number",
        icon="mdi:numeric",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("system.serialnumber"),
    ),
    # ... more sensors
]

class BarcoSensor(BarcoEntity, SensorEntity):
    """Barco sensor entity."""
    
    entity_description: BarcoSensorEntityDescription
    
    @property
    def native_value(self) -> str | int | None:
        """Return sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
```

#### 6.3 Switches (`switch.py`)

**Entities:**
- Power Switch (on/off control)

```python
class BarcoPowerSwitch(BarcoEntity, SwitchEntity):
    """Barco power switch entity."""
    
    _attr_translation_key = "power"
    _attr_device_class = SwitchDeviceClass.SWITCH
    
    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.data.get("state") in POWER_STATES_ACTIVE
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        await self.coordinator.device.power_on()
        await self.coordinator.async_request_refresh()
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self.coordinator.device.power_off()
        await self.coordinator.async_request_refresh()
```

#### 6.4 Select Entities (`select.py`)

**Entities:**
- Input Source (dropdown of available sources)

```python
class BarcoSourceSelect(BarcoEntity, SelectEntity):
    """Barco input source select entity."""
    
    _attr_translation_key = "source"
    _attr_icon = "mdi:video-input-hdmi"
    
    @property
    def current_option(self) -> str | None:
        """Return current input source."""
        return self.coordinator.data.get("source")
    
    @property
    def options(self) -> list[str]:
        """Return available input sources."""
        sources = self.coordinator.data.get("available_sources", [])
        return sources if sources else ["Unknown"]
    
    async def async_select_option(self, option: str) -> None:
        """Select input source."""
        await self.coordinator.device.set_source(option)
        await self.coordinator.async_request_refresh()
```

#### 6.5 Number Entities (`number.py`)

**Entities:**
- Laser Power (percentage slider with dynamic min/max)
- Brightness (-1.0 to 1.0)
- Contrast
- Saturation
- Hue

```python
class BarcoLaserPowerNumber(BarcoEntity, NumberEntity):
    """Barco laser power number entity."""
    
    _attr_translation_key = "laser_power"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = NumberDeviceClass.POWER_FACTOR
    _attr_mode = NumberMode.SLIDER
    
    @property
    def native_value(self) -> float | None:
        """Return current laser power."""
        return self.coordinator.data.get("laser_power")
    
    @property
    def native_min_value(self) -> float:
        """Return minimum laser power."""
        return self.coordinator.data.get("laser_min", 0)
    
    @property
    def native_max_value(self) -> float:
        """Return maximum laser power."""
        return self.coordinator.data.get("laser_max", 100)
    
    async def async_set_native_value(self, value: float) -> None:
        """Set laser power."""
        await self.coordinator.device.set_laser_power(int(value))
        await self.coordinator.async_request_refresh()

class BarcoBrightnessNumber(BarcoEntity, NumberEntity):
    """Barco brightness number entity."""
    
    _attr_translation_key = "brightness"
    _attr_native_min_value = -1.0
    _attr_native_max_value = 1.0
    _attr_native_step = 0.01
    _attr_mode = NumberMode.SLIDER
    
    @property
    def native_value(self) -> float | None:
        """Return brightness value."""
        return self.coordinator.data.get("brightness")
    
    async def async_set_native_value(self, value: float) -> None:
        """Set brightness."""
        await self.coordinator.device.set_brightness(value)
        await self.coordinator.async_request_refresh()
```

#### 6.6 Remote Entity (`remote.py`)

**Purpose:** Provide Media Player integration compatibility

```python
class BarcoRemote(BarcoEntity, RemoteEntity):
    """Barco remote entity."""
    
    _attr_translation_key = "remote"
    
    @property
    def is_on(self) -> bool:
        """Return true if projector is on."""
        return self.coordinator.data.get("state") in POWER_STATES_ACTIVE
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on projector."""
        await self.coordinator.device.power_on()
        await self.coordinator.async_request_refresh()
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off projector."""
        await self.coordinator.device.power_off()
        await self.coordinator.async_request_refresh()
    
    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send command to projector."""
        for cmd in command:
            if cmd.startswith("source_"):
                source = cmd.replace("source_", "").replace("_", " ")
                await self.coordinator.device.set_source(source)
```

### Phase 7: Manifest and Metadata

#### 7.1 Manifest (`manifest.json`)

```json
{
  "domain": "barco_pulse",
  "name": "Barco Pulse",
  "codeowners": ["@pkern90"],
  "config_flow": true,
  "documentation": "https://github.com/pkern90/barco-pulse-homeassistant",
  "integration_type": "device",
  "iot_class": "local_polling",
  "issue_tracker": "https://github.com/pkern90/barco-pulse-homeassistant/issues",
  "requirements": [],
  "version": "1.0.0"
}
```

#### 7.2 Translations (`translations/en.json`)

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to Barco Pulse Projector",
        "description": "Enter the connection details for your Barco Pulse projector.",
        "data": {
          "host": "Host (IP address)",
          "port": "Port",
          "auth_code": "Authentication Code (optional)"
        }
      },
      "reconfigure": {
        "title": "Reconfigure Barco Pulse Projector",
        "description": "Update connection details.",
        "data": {
          "host": "Host (IP address)",
          "port": "Port",
          "auth_code": "Authentication Code (optional)"
        }
      }
    },
    "error": {
      "cannot_connect": "Cannot connect to projector. Check host and port.",
      "invalid_auth": "Invalid authentication code.",
      "unknown": "Unexpected error occurred."
    },
    "abort": {
      "already_configured": "This projector is already configured."
    }
  },
  "entity": {
    "binary_sensor": {
      "power": {"name": "Power"}
    },
    "sensor": {
      "state": {"name": "State"},
      "serial_number": {"name": "Serial Number"},
      "model_name": {"name": "Model"},
      "firmware_version": {"name": "Firmware"}
    },
    "switch": {
      "power": {"name": "Power"}
    },
    "select": {
      "source": {"name": "Input Source"}
    },
    "number": {
      "laser_power": {"name": "Laser Power"},
      "brightness": {"name": "Brightness"},
      "contrast": {"name": "Contrast"},
      "saturation": {"name": "Saturation"},
      "hue": {"name": "Hue"}
    },
    "remote": {
      "remote": {"name": "Remote Control"}
    }
  }
}
```

#### 7.3 Strings (`strings.json`)

Copy of `translations/en.json` for backward compatibility.

### Phase 8: Testing and Validation


#### 8.1 Code Quality

**Linting:**
```bash
scripts/lint
```

**Type Checking:**
- All functions have type hints
- Use `from __future__ import annotations`
- Modern type syntax (`dict[str, Any]` not `Dict[str, Any]`)

**Documentation:**
- Docstrings for all public methods
- Inline comments for complex logic
- README with setup instructions

---

## Property Mapping Reference

### System Properties
| API Property | Coordinator Key | Entity |
|--------------|----------------|---------|
| `system.state` | `state` | Binary Sensor (power), Sensor (state) |
| `system.serialnumber` | `system.serialnumber` | Sensor (serial number) |
| `system.modelname` | `system.modelname` | Sensor (model name), Device Info |
| `system.firmwareversion` | `system.firmwareversion` | Sensor (firmware), Device Info |

### Illumination Properties
| API Property | Coordinator Key | Entity |
|--------------|----------------|---------|
| `illumination.sources.laser.power` | `laser_power` | Number (laser power) |
| `illumination.sources.laser.minpower` | `laser_min` | Number (min value) |
| `illumination.sources.laser.maxpower` | `laser_max` | Number (max value) |

### Image Properties
| API Property | Coordinator Key | Entity |
|--------------|----------------|---------|
| `image.window.main.source` | `source` | Select (input source) |
| `image.brightness` | `brightness` | Number (brightness) |
| `image.contrast` | `contrast` | Number (contrast) |
| `image.saturation` | `saturation` | Number (saturation) |
| `image.hue` | `hue` | Number (hue) |

### Source List
| API Method | Coordinator Key | Entity |
|------------|----------------|---------|
| `image.source.list` | `available_sources` | Select (options) |

---

## Implementation Notes

### State-Aware Property Fetching

Always check power state before querying state-dependent properties:

```python
state = await device.get_state()
if state in POWER_STATES_ACTIVE:
    # Safe to query laser power, sources, etc.
    laser_power = await device.get_laser_power()
else:
    # Properties unavailable, skip or return None
    laser_power = None
```

### Error Code Handling

Map JSON-RPC error codes to appropriate exceptions:

```python
ERROR_CODE_MAPPING = {
    -32601: BarcoStateError,  # Property not found (state-dependent)
    -32600: BarcoApiError,    # Invalid request
    -32700: BarcoApiError,    # Parse error
}
```

### Connection Management

- Use single persistent connection with lock
- Reconnect on connection errors
- Close connection on HA shutdown
- Implement timeout for all operations

### Rate Limiting

Enforce minimum 1-second interval between API requests:

```python
async def _enforce_rate_limit(self) -> None:
    elapsed = time.time() - self._last_update
    if elapsed < 1.0:
        await asyncio.sleep(1.0 - elapsed)
    self._last_update = time.time()
```

### Dynamic Polling Intervals

```python
if state in POWER_STATES_ACTIVE:
    self.update_interval = timedelta(seconds=INTERVAL_FAST)  # 10s
else:
    self.update_interval = timedelta(seconds=INTERVAL_SLOW)  # 60s
```

### Source Name Normalization

Convert display names to object names for API methods:

```python
def normalize_source_name(display_name: str) -> str:
    """Convert 'DisplayPort 1' to 'displayport1'."""
    return display_name.replace(" ", "").replace("-", "").lower()
```

---

## File Structure

```
custom_components/barco_pulse/
├── __init__.py              # Integration setup
├── api.py                   # JSON-RPC API client
├── binary_sensor.py         # Binary sensor platform
├── config_flow.py           # Configuration flow
├── const.py                 # Constants
├── coordinator.py           # Data update coordinator
├── data.py                  # Data models
├── entity.py                # Base entity class
├── exceptions.py            # Custom exceptions
├── manifest.json            # Integration manifest
├── number.py                # Number platform
├── remote.py                # Remote platform
├── select.py                # Select platform
├── sensor.py                # Sensor platform
├── strings.json             # UI strings
├── switch.py                # Switch platform
└── translations/
    └── en.json              # English translations
```

---

## References

**Protocol Specification:** `/specs/BARCO_HDR_CS_PROTOCOL.md`  
**API Reference:** `/specs/barco_pulse_api_json_rpc_reference_summary.md`  
**State Dependencies:** `/specs/HDR_CS_STATE_DEPENDENT_PROPERTIES.md`  
**Architecture:** `/specs/ARCHITECTURE.md`  
**Copilot Instructions:** `/.github/copilot-instructions.md`

---

