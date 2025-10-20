# Barco Pulse Home Assistant Integration - Architecture

**Version**: 1.1  
**Last Updated**: October 20, 2025  
**Status**: Living Design Document (update as implementation progresses)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Core Components](#core-components)
4. [Feature Categories](#feature-categories)
5. [Entity Platform Mapping](#entity-platform-mapping)
6. [Data Flow](#data-flow)
7. [State Management](#state-management)
8. [Remote Control Emulation](#remote-control-emulation)
9. [Profile/Preset Management](#profilepreset-management)
10. [Error Handling Strategy](#error-handling-strategy)
11. [Concurrency & Async Model](#concurrency--async-model)
12. [Logging & Observability](#logging--observability)
13. [Security & Secrets](#security--secrets)
14. [Testing Strategy](#testing-strategy)
15. [Performance Considerations](#performance-considerations)
16. [Subscription/Event Handling](#subscriptionevent-handling)
17. [Versioning & Deprecation](#versioning--deprecation)
18. [Risk & Mitigations](#risk--mitigations)
19. [Maintainability Guidelines](#maintainability-guidelines)
20. [Future Enhancements](#future-enhancements)

---

## Overview

The Barco Pulse Home Assistant integration provides comprehensive control and monitoring of Barco Pulse projectors through their JSON-RPC 2.0 API over a hybrid HTTP/0.9 protocol. The integration follows Home Assistant best practices and architectural patterns established by the JVC Projector integration.

### Design Goals

1. **Comprehensive Feature Coverage**: Support all major projector capabilities (power, sources, illumination, picture, warping, blending)
2. **Robust Connection Management**: Handle network interruptions, power state transitions, and API limitations gracefully
3. **Efficient Polling**: Minimize API calls through state-aware property fetching and intelligent polling intervals
4. **User-Friendly**: Expose complex projector features through familiar Home Assistant entity types
5. **Maintainable**: Clear separation of concerns, type-safe code, comprehensive documentation

### Key Differentiators from Standard Integrations

- **Hybrid Protocol**: Raw TCP sockets with manual HTTP construction (cannot use standard HTTP libraries)
- **State-Dependent Properties**: Many properties only available when projector is fully powered on
- **Complex Feature Set**: Warping, blending, profiles, remote control emulation beyond typical projector integrations
- **Dynamic Discovery**: Introspection + source listing + runtime capability detection (avoid hardcoding ranges/options)
- **Event-Driven Roadmap**: Transition from polling → mixed polling/subscription → push dominated
- **Professional Calibration Hooks**: Future support for warp grids, blend maps, gamma/LUT management

---

## Architecture Patterns

### Reference Implementation

This integration follows the architectural patterns of the **JVC Projector** custom integration:

- Config flow for setup with validation
- DataUpdateCoordinator for centralized polling
- Base entity class for common device info
- Platform-specific entity implementations (sensor, binary_sensor, select, switch, remote)
- Service calls for advanced operations

### Home Assistant Core Patterns

- **Config Entry**: UI-based configuration via config flow
- **Runtime Data**: Store coordinator and client in `entry.runtime_data` (modern pattern, HA 2024.6+)
- **DataUpdateCoordinator**: Centralized data fetching with automatic retry and error handling
- **Entity Base Class**: Shared device info, unique ID management, coordinator subscription
- **Type Safety**: Comprehensive type hints using modern Python syntax (`list[str]`, `dict | None`)

### Component Structure

```
custom_components/barco_pulse/
├── __init__.py              # Entry point, setup/unload
├── api.py                   # JSON-RPC client (raw TCP)
├── config_flow.py           # UI configuration flow
├── const.py                 # Constants and mappings
├── coordinator.py           # Data update coordinator
├── data.py                  # Runtime data structures
├── entity.py                # Base entity class
├── binary_sensor.py         # Binary sensors (power, signal, etc.)
├── sensor.py                # Sensors (state, hours, temperature)
├── select.py                # Selects (sources, profiles, picture modes)
├── switch.py                # Switches (power, blank, test patterns)
├── remote.py                # Remote control emulation
├── number.py                # Numbers (brightness, contrast, laser power)
├── services.yaml            # Service definitions
├── manifest.json            # Integration metadata
└── translations/
    └── en.json              # UI strings
```

---

## Core Components

### 1. API Client (`api.py`)

**Purpose**: Low-level JSON-RPC 2.0 communication over raw TCP sockets.

**Key Responsibilities**:
- TCP connection management (open, close, reconnect)
- Manual HTTP/1.1 POST request construction
- Raw JSON response parsing (no HTTP headers)
- JSON-RPC request/response handling (with ID tracking)
- Authentication management
- Exception mapping (connection errors → custom exceptions)
- Timeout handling (5-10 seconds per request)

**Critical Implementation Details**:

```python
class BarcoDevice:
    """Barco Pulse projector API client."""
    
    def __init__(self, host: str, port: int = 9090, auth_code: str | None = None):
        self._host = host
        self._port = port
        self._auth_code = auth_code
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._request_id = 0
        self._connected = False
        
    async def connect(self) -> None:
        """Establish TCP connection."""
        
    async def disconnect(self) -> None:
        """Close TCP connection."""
        
    async def authenticate(self) -> None:
        """Authenticate if auth code provided."""
        
    async def send_request(self, method: str, params: dict | list | None = None) -> Any:
        """Send JSON-RPC request and return result."""
        # 1. Increment request ID
        # 2. Build JSON-RPC payload
        # 3. Construct HTTP POST with Content-Length
        # 4. Write to TCP stream
        # 5. Read response (raw JSON)
        # 6. Parse and validate JSON-RPC response
        # 7. Handle errors, return result
        
    async def property_get(self, property: str | list[str]) -> Any:
        """Get one or more property values."""
        
    async def property_set(self, property: str, value: Any) -> bool:
        """Set property value."""
        
    async def method_call(self, method: str, **params) -> Any:
        """Call a method with parameters."""
```

**Error Handling**:

```python
class BarcoError(Exception):
    """Base exception."""

class BarcoConnectionError(BarcoError):
    """Connection failed."""

class BarcoAuthError(BarcoError):
    """Authentication failed."""

class BarcoApiError(BarcoError):
    """JSON-RPC error response."""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
```

**HTTP Wire Format**:

```
POST / HTTP/1.1\r\n
Host: 192.168.1.100\r\n
Content-Type: application/json\r\n
Content-Length: 82\r\n
\r\n
{"jsonrpc":"2.0","method":"property.get","params":{"property":"system.state"},"id":1}
```

**Response** (raw JSON, no HTTP headers):

```json
{"jsonrpc":"2.0","result":"on","id":1}
```

---

### 2. Data Update Coordinator (`coordinator.py`)

**Purpose**: Centralized data fetching, connection lifecycle, polling strategy.

**Key Responsibilities**:
- Manage persistent connection or connection-per-request pattern
- Implement state-dependent property fetching logic
- Dynamic polling interval based on power state
- Rate limiting between operations
- Error recovery and retry logic
- Connection health monitoring

**State-Aware Polling Strategy**:

| Power State | Polling Interval | Properties Fetched |
|-------------|------------------|-------------------|
| `standby`, `eco` | 30-60 seconds | System properties only |
| `boot`, `conditioning`, `deconditioning` | 5-10 seconds | System + attempt state-dependent |
| `ready`, `on` | 10-15 seconds | All properties |
| Connection error | Exponential backoff | None (retry connection) |

**Properties by Availability**:

```python
# Always available (any power state)
ALWAYS_AVAILABLE = [
    "system.state",
    "system.serialnumber",
    "system.modelname",
    "system.firmwareversion",
    "system.macaddress",
]

# Available when ON (state = "ready" or "on")
WHEN_ON = [
    "illumination.sources.laser.power",
    "illumination.sources.laser.maxpower",
    "illumination.sources.laser.minpower",
    "illumination.state",
    "image.window.main.source",
    "image.brightness",
    "image.contrast",
    "image.saturation",
    "image.hue",
    "image.sharpness",
]

# Optional/Advanced (ON state, may require introspection)
ADVANCED = [
    "image.processing.warp.enable",
    "image.processing.blend.enable",
    "ui.layer.blank.enable",
    # ... additional properties discovered via introspection
]
```

**Implementation Pattern**:

```python
class BarcoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Barco Pulse data update coordinator."""
    
    def __init__(self, hass: HomeAssistant, device: BarcoDevice):
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=NAME,
            update_interval=INTERVAL_SLOW,  # Start with slow interval
        )
        self.device = device
        self._connection_lock = asyncio.Lock()
        self._update_lock = asyncio.Lock()
        self._last_state: str | None = None
        
    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from projector."""
        async with self._update_lock:
            try:
                # 1. Ensure connected (with retry)
                await self._ensure_connected()
                
                # 2. Rate limiting (minimum time between requests)
                await self._rate_limit()
                
                # 3. Always fetch system state first
                state = await self.device.property_get("system.state")
                data = {"system.state": state}
                
                # 4. Fetch always-available properties
                data.update(await self._fetch_batch(ALWAYS_AVAILABLE))
                
                # 5. Fetch state-dependent properties if ON
                if state in ["ready", "on"]:
                    data.update(await self._fetch_batch_safe(WHEN_ON))
                    
                # 6. Update polling interval based on state
                self._update_interval_for_state(state)
                
                # 7. Track state transitions
                if state != self._last_state:
                    _LOGGER.info("State changed: %s -> %s", self._last_state, state)
                    self._last_state = state
                    
                return data
                
            except BarcoConnectionError as err:
                raise UpdateFailed(f"Connection failed: {err}")
            except BarcoAuthError as err:
                raise ConfigEntryAuthFailed(f"Authentication failed: {err}")
            except BarcoApiError as err:
                if err.code == -32601:  # Method/property not found
                    # Non-fatal, likely state-dependent property in wrong state
                    _LOGGER.debug("Property not available: %s", err.message)
                    return data
                raise UpdateFailed(f"API error: {err}")
                
    async def _fetch_batch_safe(self, properties: list[str]) -> dict[str, Any]:
        """Fetch properties, handle -32601 errors gracefully."""
        # Can fetch as batch or individual, handle errors per-property
        
    async def _ensure_connected(self) -> None:
        """Ensure connection is established."""
        async with self._connection_lock:
            if not self.device._connected:
                await self.device.connect()
                if self.device._auth_code:
                    await self.device.authenticate()
```

---

### 3. Config Flow (`config_flow.py`)

**Purpose**: UI-based projector setup and validation.

**Flow Steps**:

1. **User Input**: Host, port (default 9090), optional authentication code
2. **Validation**: Test connection, fetch serial number for unique ID
3. **Create Entry**: Store configuration, set unique ID
4. **Error Handling**: Connection errors, authentication failures, duplicate detection

**User Schema**:

```python
STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_PORT, default=9090): int,
    vol.Optional(CONF_CODE): str,  # 5-digit PIN
})
```

**Validation Logic**:

```python
async def async_step_user(self, user_input: dict[str, Any] | None = None):
    """Handle user step."""
    errors = {}
    
    if user_input is not None:
        try:
            # Create device and test connection
            device = BarcoDevice(
                host=user_input[CONF_HOST],
                port=user_input.get(CONF_PORT, 9090),
                auth_code=user_input.get(CONF_CODE),
            )
            
            await device.connect()
            
            # Authenticate if code provided
            if device._auth_code:
                await device.authenticate()
                
            # Fetch serial number for unique ID
            serial = await device.property_get("system.serialnumber")
            model = await device.property_get("system.modelname")
            
            await device.disconnect()
            
            # Check for duplicates
            await self.async_set_unique_id(serial)
            self._abort_if_unique_id_configured()
            
            # Create entry
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
```

**Error Messages** (`translations/en.json`):

```json
{
  "config": {
    "error": {
      "cannot_connect": "Failed to connect to projector",
      "invalid_auth": "Invalid authentication code",
      "unknown": "Unexpected error occurred"
    }
  }
}
```

---

### 4. Base Entity (`entity.py`)

**Purpose**: Common entity base class with device info and coordinator integration.

```python
class BarcoEntity(CoordinatorEntity[BarcoDataUpdateCoordinator]):
    """Base entity for Barco Pulse."""
    
    _attr_has_entity_name = True
    
    def __init__(self, coordinator: BarcoDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.unique_id)},
            name=coordinator.config_entry.title,
            manufacturer="Barco",
            model=coordinator.data.get("system.modelname"),
            sw_version=coordinator.data.get("system.firmwareversion"),
            serial_number=coordinator.unique_id,
        )
```

---

## Feature Categories

### 1. Power Management

**Capabilities**:
- Power on/off
- State monitoring (boot, eco, standby, ready, on, conditioning, deconditioning)
- Automatic state-dependent behavior

**Implementation**:
- **Binary Sensor**: `binary_sensor.power` (ON when state is "on" or "ready")
- **Switch**: `switch.power` (power on/off commands)
- **Sensor**: `sensor.state` (current power state string)

**API Methods**:
- `system.poweron` - Power on
- `system.poweroff` - Power off
- `property.get("system.state")` - Get current state

**State Transitions**:

```
standby → boot → conditioning → on
on → deconditioning → standby
standby ↔ eco (low power mode)
```

---

### 2. Input Source Management

**Capabilities**:
- List available sources (DVI, DisplayPort, HDMI, SDI, HDBaseT, dual-head)
- Select active source for main window
- Monitor current source
- Signal detection status

**Implementation**:
- **Select**: `select.source` (list and select input source)
- **Sensor**: `sensor.current_source` (current active source)
- **Binary Sensor**: `binary_sensor.signal_detected` (if supported by API)

**API Methods**:
- `image.source.list` - Get available sources
- `property.get("image.window.main.source")` - Get current source
- `property.set("image.window.main.source", "DisplayPort 1")` - Set source

**Source Name Translation**:

Source names from `image.source.list` contain spaces and special characters. To access source properties, convert to object name:

```python
def source_to_object_name(source: str) -> str:
    """Convert source name to object name."""
    # Remove non-word characters, lowercase
    return re.sub(r'\W', '', source).lower()
    
# Example: "DisplayPort 1" → "displayport1"
```

**Dynamic Source Discovery**:

Sources vary by model and configuration. Use `image.source.list` at startup and cache results. Refresh when `modelupdated` signal received.

---

### 3. Illumination Control

**Capabilities**:
- Laser power control (percentage)
- Dynamic min/max power limits (depend on lens, calibration)
- Illumination state (On/Off)
- Laser runtime tracking

**Implementation**:
- **Number**: `number.laser_power` (0-100%, constrained by min/max)
- **Sensor**: `sensor.laser_power` (current power percentage)
- **Sensor**: `sensor.laser_runtime` (total laser hours)
- **Binary Sensor**: `binary_sensor.illumination` (on/off state)

**API Properties**:
- `illumination.sources.laser.power` - Current power (R/W, ON state only)
- `illumination.sources.laser.maxpower` - Maximum allowed power (R, ON state)
- `illumination.sources.laser.minpower` - Minimum allowed power (R, ON state)
- `illumination.state` - Illumination on/off (R, ON state)

**Dynamic Constraints**:

Min/max power can change based on:
- Lens configuration
- Calibration state
- Thermal conditions

Always fetch `maxpower` and `minpower` during updates to set number entity constraints dynamically.

```python
@property
def native_min_value(self) -> float:
    """Return minimum laser power."""
    return self.coordinator.data.get("illumination.sources.laser.minpower", 0)
    
@property
def native_max_value(self) -> float:
    """Return maximum laser power."""
    return self.coordinator.data.get("illumination.sources.laser.maxpower", 100)
```

---

### 4. Picture Settings

**Capabilities**:
- Brightness, contrast, saturation, hue, sharpness
- Color temperature
- Picture test patterns
- Gamma settings
- Advanced color management

**Implementation**:
- **Number**: `number.brightness`, `number.contrast`, etc. (normalized -1 to 1 or 0-1)
- **Select**: `select.color_temperature` (presets)
- **Switch**: `switch.test_pattern` (enable/disable test patterns)

**API Properties** (all require ON state):
- `image.brightness` - Brightness offset (-1 to 1, normalized)
- `image.contrast` - Contrast adjustment
- `image.saturation` - Color saturation
- `image.hue` - Color hue
- `image.sharpness` - Image sharpness

**Introspection for Constraints**:

Picture properties have metadata (min, max, step-size, precision). Use introspection to discover:

```json
{
  "name": "brightness",
  "type": {
    "base": "float",
    "min": -1,
    "max": 1,
    "step-size": 1,
    "precision": 0.01
  },
  "access": "READ_WRITE"
}
```

**Effective Step**: `step-size × precision = 1 × 0.01 = 0.01`

Cache introspection results during coordinator setup, refresh on firmware updates.

---

### 5. Warping and Blending

**Capabilities**:
- Enable/disable geometric warping
- Upload/download warp grid files (XML)
- Enable/disable edge blending
- Advanced blending zones
- Four-corner adjustment
- Grid overlay for alignment

**Implementation**:
- **Switch**: `switch.warp_enable`, `switch.blend_enable`
- **Binary Sensor**: `binary_sensor.warp_active`, `binary_sensor.blend_active`
- **Service**: `barco_pulse.upload_warp_grid`, `barco_pulse.download_warp_grid`
- **Switch**: `switch.grid_overlay` (alignment grid)

**API Properties**:
- `image.processing.warp.enable` - Enable warping (R/W)
- `image.processing.blend.enable` - Enable blending (R/W)
- `ui.layer.grid.enable` - Grid overlay (R/W)

**File Endpoints** (HTTP, not JSON-RPC):
- `GET http://<host>/api/image/processing/warp/file/transfer` - Download warp grid
- `POST http://<host>/api/image/processing/warp/file/transfer` - Upload warp grid (multipart/form-data)

**Service Implementation**:

```yaml
# services.yaml
upload_warp_grid:
  name: Upload warp grid
  description: Upload a warp grid XML file
  fields:
    file_path:
      name: File path
      description: Path to warp grid XML file
      required: true
      example: "/config/warp_grid.xml"

download_warp_grid:
  name: Download warp grid
  description: Download current warp grid to file
  fields:
    file_path:
      name: File path
      description: Path to save warp grid XML file
      required: true
      example: "/config/warp_grid.xml"
```

---

### 6. Screen Blanking and Freeze

**Capabilities**:
- Blank/mute screen (black output)
- Custom blank text/icon
- Image freeze
- Shutter control (if hardware supported)

**Implementation**:
- **Switch**: `switch.blank` (blank screen)
- **Switch**: `switch.freeze` (freeze current frame)

**API Properties**:
- `ui.layer.blank.enable` - Enable blank overlay
- `ui.layer.blank.show` - Show blank layer
- `ui.layer.blank.text` - Custom blank text
- `ui.layer.blank.icon` - Blank icon selection

---

## Entity Platform Mapping

### Binary Sensors (`binary_sensor.py`)

| Entity ID | Name | Property/Logic | Device Class |
|-----------|------|----------------|--------------|
| `binary_sensor.power` | Power | `system.state in ["ready", "on"]` | power |
| `binary_sensor.illumination` | Illumination | `illumination.state == "On"` | light |
| `binary_sensor.signal_detected` | Signal Detected | Source signal detection | connectivity |
| `binary_sensor.warp_active` | Warp Active | `image.processing.warp.enable` | None |
| `binary_sensor.blend_active` | Blend Active | `image.processing.blend.enable` | None |

### Sensors (`sensor.py`)

| Entity ID | Name | Property | Unit | Device Class |
|-----------|------|----------|------|--------------|
| `sensor.state` | Power State | `system.state` | - | enum |
| `sensor.current_source` | Current Source | `image.window.main.source` | - | None |
| `sensor.laser_power` | Laser Power | `illumination.sources.laser.power` | % | None |
| `sensor.laser_runtime` | Laser Runtime | `statistics.laser plate 1 bank 1 runtime.value` | hours | duration |
| `sensor.firmware_version` | Firmware Version | `system.firmwareversion` | - | None |
| `sensor.model` | Model | `system.modelname` | - | None |

### Selects (`select.py`)

| Entity ID | Name | Method/Property | Options Source |
|-----------|------|-----------------|----------------|
| `select.source` | Input Source | `image.window.main.source` | `image.source.list` |
| `select.profile` | Profile | Profile management (scheduler) | Profile list |
| `select.color_temperature` | Color Temperature | `image.colortemperature` | Introspection |
| `select.language` | UI Language | `ui.language` | Introspection |

### Numbers (`number.py`)

| Entity ID | Name | Property | Min/Max | Step |
|-----------|------|----------|---------|------|
| `number.laser_power` | Laser Power | `illumination.sources.laser.power` | Dynamic | 1 |
| `number.brightness` | Brightness | `image.brightness` | -1 / 1 | 0.01 |
| `number.contrast` | Contrast | `image.contrast` | -1 / 1 | 0.01 |
| `number.saturation` | Saturation | `image.saturation` | -1 / 1 | 0.01 |
| `number.hue` | Hue | `image.hue` | -1 / 1 | 0.01 |
| `number.sharpness` | Sharpness | `image.sharpness` | -1 / 1 | 0.01 |

### Switches (`switch.py`)

| Entity ID | Name | Property | Device Class |
|-----------|------|----------|--------------|
| `switch.power` | Power | `system.poweron` / `system.poweroff` | switch |
| `switch.blank` | Blank Screen | `ui.layer.blank.enable` | switch |
| `switch.freeze` | Freeze Image | Image freeze property | switch |
| `switch.warp` | Warping | `image.processing.warp.enable` | switch |
| `switch.blend` | Blending | `image.processing.blend.enable` | switch |
| `switch.grid_overlay` | Grid Overlay | `ui.layer.grid.enable` | switch |

### Remote (`remote.py`)

**Purpose**: Emulate physical remote control and keypad.

**Features**:
- Send button press commands
- Menu navigation (up, down, left, right, ok, back)
- Direct access shortcuts (lens menu, pattern menu, input menu)
- Custom command support

---

## Data Flow

### Startup Sequence

```
1. HA loads integration → async_setup_entry()
2. Create BarcoDevice with config entry data (host, port, auth)
3. Create BarcoDataUpdateCoordinator
4. Call coordinator.async_config_entry_first_refresh()
   ├─ coordinator connects device
   ├─ coordinator authenticates (if needed)
   ├─ coordinator fetches initial data
   └─ Raises ConfigEntryNotReady on failure
5. Store coordinator in entry.runtime_data
6. Forward setup to platforms (binary_sensor, sensor, select, etc.)
7. Each platform creates entities with coordinator reference
8. Register services
9. Register shutdown handler
```

### Runtime Data Fetching

```
Coordinator Update Timer Fires
├─ _async_update_data() called
├─ Acquire update lock
├─ Ensure connection (reconnect if needed)
├─ Rate limit (minimum interval between requests)
├─ Fetch system.state (always available)
├─ Fetch always-available properties (batch)
├─ If state = "on" or "ready":
│  └─ Fetch state-dependent properties (batch, handle -32601)
├─ Update polling interval based on state
├─ Return data dict
└─ Coordinator notifies all subscribed entities
   └─ Entities update via @property methods
```

### Entity Command Flow

```
User clicks switch/button in HA UI
├─ Entity's async_turn_on() / async_select_option() / etc.
├─ Call coordinator.device.property_set() or method_call()
├─ API client sends JSON-RPC request
├─ Wait for response
├─ Handle errors (show notification on failure)
├─ Request coordinator refresh:
│  └─ await coordinator.async_request_refresh()
└─ Coordinator updates all entities with new state
```

### Subscription Notifications (Future Enhancement)

```
Coordinator subscribes to properties on connect
├─ Send property.subscribe request
├─ Listen for property.changed notifications (no ID field)
├─ Parse notification params
├─ Update coordinator.data immediately (no wait for polling)
└─ Notify entities of update
```

---

## State Management

### Power State Transitions

**State Diagram**:

```
           ┌─────────────────────────┐
           │       standby           │ ◄───────┐
           └──────────┬──────────────┘         │
                      │ poweron                │
                      ▼                        │
           ┌─────────────────────────┐         │
           │         boot            │         │
           └──────────┬──────────────┘         │
                      │                        │
                      ▼                        │
           ┌─────────────────────────┐         │
           │     conditioning        │         │
           └──────────┬──────────────┘         │
                      │                        │
                      ▼                        │
           ┌─────────────────────────┐         │
           │       ready/on          │ ────────┤ poweroff
           └──────────┬──────────────┘         │
                      │                        │
                      ▼                        │
           ┌─────────────────────────┐         │
           │    deconditioning       │ ────────┘
           └─────────────────────────┘

           standby ↔ eco (low power toggle)
```

**State Descriptions**:

- **standby**: Normal off state, can power on
- **eco**: Low power mode, reduced standby consumption
- **boot**: Initializing hardware, loading firmware
- **conditioning**: Warming up laser/illumination (can take 30-60s)
- **ready**: Fully initialized, illumination ready but not active
- **on**: Normal operation, projecting image
- **deconditioning**: Cooling down before standby (can take 60-120s)

**Coordinator Behavior by State**:

| State | Polling Interval | Properties Attempted | Error Handling |
|-------|------------------|---------------------|----------------|
| standby, eco | 60 seconds | System only | Normal |
| boot | 5 seconds | System only | Normal |
| conditioning | 10 seconds | System + attempt ON properties | Ignore -32601 |
| ready, on | 15 seconds | All properties | Log -32601 as warning |
| deconditioning | 10 seconds | System + attempt ON properties | Ignore -32601 |
| Connection error | Exponential backoff (1s, 2s, 4s, 8s max) | None | Retry connection |

**Entity Availability**:

Most entities should remain **available** even when projector is off (standby). Entities should return `None` or last known value for unavailable properties rather than becoming unavailable.

**Exception**: Binary sensors and switches directly related to ON-state features (illumination, signal detection) may use `available` property:

```python
@property
def available(self) -> bool:
    """Return if entity is available."""
    state = self.coordinator.data.get("system.state")
    return state in ["ready", "on"] and self.coordinator.last_update_success
```

---

## Remote Control Emulation

### Overview

The Barco Pulse API provides remote control emulation through the **key dispatcher** system. Physical remote/keypad buttons trigger `keydispatcher.keyevent` signals that can be monitored or emulated.

### Key Architecture

**Signal-Based System**:
- Remote buttons trigger `keydispatcher.keyevent` signal
- Signal provides: `key` (name), `type` (press/release/repeat/clicked), `source` (remote/keypad)
- Integration can **send** key events to emulate button presses
- Integration can **subscribe** to key events to monitor physical button presses

### Remote Entity Implementation

**Platform**: `remote.py` (Home Assistant remote entity)

**Features**:
- Power on/off via remote
- Send individual button commands
- Send sequences of commands
- Support for repeat/hold

**Remote Commands** (based on JVC pattern):

```python
REMOTE_COMMANDS = {
    # Navigation
    "menu": "menu",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "ok": "ok",
    "enter": "enter",
    "back": "back",
    
    # Function keys
    "input": "input",
    "info": "info",
    "blank": "blank",
    "freeze": "freeze",
    "lens": "lens",
    "pattern": "testpattern",
    
    # Picture modes (if supported via keys)
    "cinema": "cinema",
    "presentation": "presentation",
    "video": "video",
    
    # Numeric keys
    "0": "0",
    "1": "1",
    "2": "2",
    # ... etc
}
```

**Key Event Method**:

The API does not explicitly document a "send key" method, but inspection of `keydispatcher.keyevent` signal suggests it's monitoring physical events. If no send method exists, fallback to:

1. **Direct property/method calls** for common operations (use switch/select entities)
2. **Macro system** (if supported) to record/replay button sequences
3. **Feature request** to Barco for programmatic key injection

**Implementation Pattern**:

```python
class BarcoRemote(BarcoEntity, RemoteEntity):
    """Barco Pulse remote entity."""
    
    _attr_supported_features = RemoteEntityFeature.ACTIVITY
    
    @property
    def is_on(self) -> bool:
        """Return if remote is on (projector is on)."""
        return self.coordinator.data.get("system.state") in ["ready", "on"]
        
    async def async_turn_on(self, **kwargs) -> None:
        """Turn projector on."""
        await self.coordinator.device.method_call("system.poweron")
        await self.coordinator.async_request_refresh()
        
    async def async_turn_off(self, **kwargs) -> None:
        """Turn projector off."""
        await self.coordinator.device.method_call("system.poweroff")
        await self.coordinator.async_request_refresh()
        
    async def async_send_command(self, command: list[str], **kwargs) -> None:
        """Send remote control commands."""
        repeat = kwargs.get("num_repeats", 1)
        delay = kwargs.get("delay_secs", 0.4)
        
        for _ in range(repeat):
            for cmd in command:
                if cmd in REMOTE_COMMANDS:
                    # Send key event or equivalent API call
                    # Implementation depends on available API methods
                    await self._send_button(REMOTE_COMMANDS[cmd])
                    await asyncio.sleep(delay)
```

### Monitoring Physical Remote (Future Enhancement)

Subscribe to `keydispatcher.keyevent` signal to monitor physical button presses and trigger automations:

```python
# Subscribe to key events
await device.send_request("signal.subscribe", {"signal": "keydispatcher.keyevent"})

# Handle notifications
# {"jsonrpc":"2.0","method":"signal.callback","params":{"signal":[{"keydispatcher.keyevent":{"key":"menu","type":"PRESS","source":"remote control"}}]}}

# Fire HA event
hass.bus.async_fire("barco_pulse_button", {
    "device_id": entry.entry_id,
    "key": "menu",
    "type": "PRESS",
    "source": "remote control",
})
```

**Use Cases**:
- Trigger HA automations from physical remote
- Sync remote button to HA scenes
- Custom button mapping

---

## Profile/Preset Management

### Overview

Barco Pulse projectors support **profiles** (also called presets) through the **scheduler** system. Profiles store complete projector configurations including picture settings, warping, blending, and input source.

### Scheduler-Based Profiles

The `scheduler` object manages profiles and scheduled actions.

**Key Properties**:
- `scheduler.transitions` - List of available system transitions
- `scheduler.scheduledactions` - List of all scheduled actions (includes profile data)
- `scheduler.nexttasks` - Next scheduled tasks with profile information

**Profile Data Structure** (from scheduled action):

```json
{
  "Name": "Profile1",
  "Type": "system",
  "Transition": "Fade",
  "Macro": "",
  "Profile": "Cinema_Mode",
  "LaunchTimePoint": "2025-10-20T14:30:00Z"
}
```

### Profile Selection Methods

#### Method 1: Via Scheduler Actions

Create scheduled action for immediate execution:

```python
async def set_profile(self, profile_name: str) -> None:
    """Set active profile via scheduler."""
    # Create action
    action_id = await self.device.method_call(
        "scheduler.create",
        name=f"HA_Profile_{profile_name}"
    )
    
    # Configure action with profile
    await self.device.property_set(
        f"scheduler.actions.{action_id}.profile",
        profile_name
    )
    
    # Execute immediately
    await self.device.property_set(
        f"scheduler.actions.{action_id}.execute",
        True
    )
```

#### Method 2: Via Direct Properties (if available)

Some projectors may expose `system.profile.current` or similar:

```python
async def set_profile(self, profile_name: str) -> None:
    """Set active profile directly."""
    await self.device.property_set("system.profile.current", profile_name)
```

**Discovery**: Use introspection to check for profile properties:

```python
# Introspect system object
result = await device.send_request("introspect", {"object": "system", "recursive": False})

# Check for profile-related properties/methods
```

#### Method 3: Via Macros

Profiles can be stored as **macros** (recorded command sequences):

```python
# List available macros
macros = await device.property_get("macros.list")  # Check via introspection

# Execute macro
await device.method_call("macros.execute", name="Cinema_Profile")
```

### Profile List Discovery

**Scheduler Approach**:

```python
async def get_profiles(self) -> list[str]:
    """Get list of available profiles."""
    # Get all scheduled actions (contains profile data)
    actions_json = await self.device.property_get("scheduler.scheduledactions")
    actions = json.loads(actions_json)
    
    # Extract unique profile names
    profiles = {action.get("Profile") for action in actions if action.get("Profile")}
    return sorted(profiles)
```

**Introspection Approach**:

Check for `profiles.*` object or `system.profiles.*`:

```python
result = await device.send_request("introspect", {"object": "", "recursive": False})
# Look for "profiles" in objects list
```

### Profile Select Entity

```python
@dataclass(frozen=True, kw_only=True)
class BarcoSelectDescription(SelectEntityDescription):
    """Barco select entity description."""
    get_options: Callable[[BarcoDevice], Awaitable[list[str]]]
    set_func: Callable[[BarcoDevice, str], Awaitable[None]]

async def get_profile_options(device: BarcoDevice) -> list[str]:
    """Get available profiles."""
    # Implementation depends on discovery method
    return await device.get_profiles()

async def set_profile(device: BarcoDevice, profile: str) -> None:
    """Set active profile."""
    # Implementation depends on available methods
    await device.set_profile(profile)

SELECTS = [
    BarcoSelectDescription(
        key="profile",
        translation_key="profile",
        icon="mdi:palette",
        get_options=get_profile_options,
        set_func=set_profile,
    ),
]

class BarcoSelectEntity(BarcoEntity, SelectEntity):
    """Barco select entity."""
    
    entity_description: BarcoSelectDescription
    
    async def async_added_to_hass(self) -> None:
        """Entity added to hass."""
        await super().async_added_to_hass()
        # Refresh options on add
        self._attr_options = await self.entity_description.get_options(
            self.coordinator.device
        )
        
    @property
    def current_option(self) -> str | None:
        """Return current option."""
        return self.coordinator.data.get(self.entity_description.key)
        
    async def async_select_option(self, option: str) -> None:
        """Select option."""
        await self.entity_description.set_func(self.coordinator.device, option)
        await self.coordinator.async_request_refresh()
```

### Profile Services

Additional services for profile management:

```yaml
# services.yaml
save_profile:
  name: Save profile
  description: Save current settings as a profile
  fields:
    profile_name:
      name: Profile name
      description: Name for the new profile
      required: true
      example: "Cinema Mode"

delete_profile:
  name: Delete profile
  description: Delete a saved profile
  fields:
    profile_name:
      name: Profile name
      description: Name of profile to delete
      required: true
      example: "Cinema Mode"

load_profile:
  name: Load profile
  description: Load a saved profile
  fields:
    profile_name:
      name: Profile name
      description: Name of profile to load
      required: true
      example: "Cinema Mode"
    transition:
      name: Transition
      description: Transition effect (fade, cut, etc.)
      required: false
      example: "Fade"
```

**Implementation**:

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up from config entry."""
    coordinator = entry.runtime_data
    
    async def save_profile(call: ServiceCall) -> None:
        """Save current settings as profile."""
        profile_name = call.data["profile_name"]
        # Implementation via scheduler.create or profile.save
        
    async def delete_profile(call: ServiceCall) -> None:
        """Delete profile."""
        profile_name = call.data["profile_name"]
        # Implementation via scheduler.delete or profile.delete
        
    async def load_profile(call: ServiceCall) -> None:
        """Load profile."""
        profile_name = call.data["profile_name"]
        transition = call.data.get("transition")
        # Implementation via scheduler action or profile.load
        
    hass.services.async_register(DOMAIN, "save_profile", save_profile)
    hass.services.async_register(DOMAIN, "delete_profile", delete_profile)
    hass.services.async_register(DOMAIN, "load_profile", load_profile)
```

---

## Error Handling Strategy

### Exception Hierarchy

```python
class BarcoError(Exception):
    """Base exception for Barco Pulse."""

class BarcoConnectionError(BarcoError):
    """Connection error (TCP connection failed, timeout)."""

class BarcoAuthError(BarcoError):
    """Authentication error (invalid code)."""

class BarcoApiError(BarcoError):
    """JSON-RPC error response."""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API Error {code}: {message}")
```

### Error Code Handling

| Code | Meaning | Action |
|------|---------|--------|
| -32700 | Parse error | Log error, reconnect, retry |
| -32600 | Invalid request | Fix request format (developer error) |
| -32601 | Method/property not found | Check power state, skip if state-dependent |
| -32602 | Invalid params | Fix parameters (developer error) |
| -32603 | Internal error | Log error, retry with backoff |

### Coordinator Error Handling

```python
async def _async_update_data(self) -> dict[str, Any]:
    """Fetch data."""
    try:
        # ... fetch logic
    except BarcoConnectionError as err:
        # Connection failed - will retry with backoff
        raise UpdateFailed(f"Connection failed: {err}") from err
    except BarcoAuthError as err:
        # Auth failed - need reconfiguration
        raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
    except BarcoApiError as err:
        if err.code == -32601:
            # Property not found - likely state-dependent, non-fatal
            _LOGGER.debug("Property not available (state-dependent): %s", err.message)
            return self.data or {}  # Return last known data
        if err.code in [-32700, -32603]:
            # Parse error or internal error - reconnect and retry
            _LOGGER.warning("API error, reconnecting: %s", err)
            await self.device.disconnect()
            raise UpdateFailed(f"API error: {err}") from err
        # Other API errors
        raise UpdateFailed(f"API error: {err}") from err
```

### Entity Command Error Handling

```python
async def async_turn_on(self, **kwargs) -> None:
    """Turn on."""
    try:
        await self.coordinator.device.method_call("system.poweron")
        await self.coordinator.async_request_refresh()
    except BarcoApiError as err:
        _LOGGER.error("Failed to power on: %s", err)
        # Optionally show persistent notification
        self.hass.components.persistent_notification.async_create(
            f"Failed to power on projector: {err.message}",
            title="Barco Pulse Error",
        )
        raise HomeAssistantError(f"Power on failed: {err.message}") from err
```

### Connection Retry Strategy

**Backoff Pattern**:

```python
class BarcoDevice:
    def __init__(self, ...):
        self._retry_delays = [1, 2, 4, 8, 8]  # Exponential capped at 8s
        self._retry_count = 0
        
    async def _connect_with_retry(self, max_retries: int = 3) -> None:
        """Connect with exponential backoff."""
        for attempt in range(max_retries):
            try:
                await self._connect()
                self._retry_count = 0  # Reset on success
                return
            except OSError as err:
                self._retry_count = min(self._retry_count + 1, len(self._retry_delays) - 1)
                delay = self._retry_delays[self._retry_count]
                _LOGGER.warning(
                    "Connection attempt %d/%d failed: %s. Retrying in %ds",
                    attempt + 1,
                    max_retries,
                    err,
                    delay,
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                else:
                    raise BarcoConnectionError(f"Failed after {max_retries} attempts") from err
```

### Timeout Strategy

**Per-Request Timeouts**:

```python
async def send_request(self, method: str, params: Any = None, timeout: float = 10.0) -> Any:
    """Send request with timeout."""
    try:
        async with asyncio.timeout(timeout):
            # ... send and receive
    except asyncio.TimeoutError:
        raise BarcoConnectionError(f"Request timeout after {timeout}s") from None
```

**Recommended Timeouts**:
- Property get: 5 seconds
- Property set: 10 seconds
- Method call (power on/off): 10 seconds
- Introspection: 15 seconds (large response)
- Connection: 5 seconds

---

## Performance Considerations
## Concurrency & Async Model

The integration is fully async and relies on Home Assistant's event loop. Key concurrency components:

- **Connection Lock**: Ensures only one coroutine establishes/reconnects the TCP stream at a time.
- **Update Lock**: Serializes coordinator refresh cycles avoiding overlapping batch requests.
- **Rate Limiter**: Enforces minimal spacing between JSON-RPC calls when multiple entity service calls occur rapidly.
- **Cancellation**: Use `asyncio.timeout` and allow `CancelledError` to propagate for HA shutdown responsiveness.

Guidelines:
1. Re-fetch `system.state` at start of every cycle to prevent stale state-dependent logic.
2. Entity commands should set/modify then trigger `async_request_refresh()` rather than performing extra direct gets.
3. Future subscription listener runs as a background task reading from the persistent stream; never block writes.

Pitfalls & Mitigations:
- Power transition during batch: keep batches small; on -32601 return partial data rather than failing.
- Connection drop mid-read: detect JSON decode failure and reconnect (retain last successful data snapshot).

## Logging & Observability

Granular logging categories:

| Level | Purpose | Examples |
|-------|---------|----------|
| DEBUG | Protocol details, raw JSON (redacted auth) | Request/response bodies, timing metrics |
| INFO  | Lifecycle & transitions | Connection established, state changed |
| WARNING | Recoverable issues | Reconnect attempts, internal API errors (-32603) |
| ERROR | Irrecoverable or user-facing | Auth failure, persistent parse errors |

Observability roadmap:
- Emit HA events (`barco_pulse_state_changed`, `barco_pulse_button`, `barco_pulse_property_changed`).
- Measure request RTT and refresh duration; log deviations (>2s normal threshold, >5s warning).
- Optional future Prometheus exporter (external add-on).

Redaction: Mask auth code except last character. Avoid logging large warp grid blobs unless debug flag active.

## Security & Secrets

Threats: Unauthorized control via leaked auth code; packet sniffing (no TLS). Mitigations:
1. Store auth only in config entry data; never duplicate.
2. Redact auth in logs (`****5`).
3. Validate host input to prevent header injection (strip whitespace, refuse newline chars).
4. Future: Document TLS proxy (stunnel) option as hardening measure.
5. Restrict warp grid file operations to HA config directory.

Auth editing via options flow (future) should not reveal current value.

## Testing Strategy

Layers:
1. Unit: API client (construction, parsing, error mapping), coordinator interval/state logic, entity property mapping.
2. Integration: Simulated TCP server fixture; scripted sequences (standby → boot → conditioning → on).
3. Property matrix: Ensure ON-only properties skipped gracefully in standby.
4. Regression: Introspection parsing snapshot for constraints (laser min/max).
5. Performance smoke: Batch (10 properties) <250ms local; warn if >500ms.

Tools: `pytest-asyncio`, mocks for `StreamReader/Writer`. Coverage prioritizes error paths first.

## Subscription/Event Handling

Roadmap steps:
1. Subscribe via `signal.subscribe` / `property.subscribe` on connect.
2. Background task to process notifications updating `coordinator.data` immediately.
3. Reduce polling interval (e.g., 15s → 90s) once stable subscriptions confirmed.
4. HA events fired for button and property changes.

Listener sketch:
```python
async def _listen_notifications(self) -> None:
    while self._connected:
        try:
            line = await self._reader.readline()
            if not line:
                raise BarcoConnectionError("Stream closed")
            msg = json.loads(line)
            if msg.get("method") == "signal.callback":
                for item in msg["params"].get("signal", []):
                    self._handle_signal(item)
            elif msg.get("method") == "property.changed":
                changed = msg["params"].get("property", {})
                self._apply_property_changes(changed)
        except json.JSONDecodeError:
            _LOGGER.debug("Skipping malformed notification chunk")
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Notification listener error: %s", err)
            await self._schedule_reconnect()
            break
```

Event schemas:

| Event | Data Keys | Description |
|-------|-----------|-------------|
| `barco_pulse_state_changed` | `old_state`, `new_state`, `serial` | Power transition |
| `barco_pulse_button` | `key`, `type`, `source`, `serial` | Physical remote/keypad input |
| `barco_pulse_property_changed` | `properties`, `serial` | Batch changed properties |

## Versioning & Deprecation

Release strategy: GitHub tags (`v0.1.0` MVP, `v0.2.0` subscriptions). Maintain entity unique IDs; no retroactive renames.

Deprecation steps: Announce → keep functional ≥2 minor versions → log warning when used → remove.

Add `CHANGELOG.md` (future) for tracking.

## Risk & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| Firmware protocol change | Breaks parsing | Medium | Resilient JSON framing, version detection via introspection |
| High latency network | Slow UI updates | Medium | Batch requests, subscriptions, adaptive intervals |
| Missing properties on new model | Partial data | High | Introspection fallback, tolerant -32601 handling |
| Notification task leak | Memory growth | Low | Heartbeat & restart mechanism |
| Auth brute force | Unauthorized access | Low | Limit attempts per setup; no repeated silent retries |
| Large warp grid blocking loop | Starvation | Medium | Chunked streaming, optional executor for file operations |

## Maintainability Guidelines

Coding: `from __future__ import annotations` everywhere; dataclasses for entity descriptions; ruff rules enforced.
Documentation: Update this file with each new platform/service; docstrings include error modes.
Dependencies: Minimize external libs; add only with justification and version pin.
Review Checklist: stable IDs, no sync I/O, correct log levels, updated translations for new strings.

## Performance Considerations

### Batch Property Fetching

**Single Request**:

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {
    "property": ["system.state", "illumination.sources.laser.power", "image.brightness"]
  },
  "id": 1
}
```

**Single Response**:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "system.state": "on",
    "illumination.sources.laser.power": 75,
    "image.brightness": 0
  },
  "id": 1
}
```

**Benefit**: Reduce round-trips, faster updates. Use batch fetching for all coordinator updates.

### Introspection Caching

**Strategy**:
1. Perform full introspection once during setup
2. Cache results in coordinator
3. Refresh on `modelupdated` signal
4. Store in persistent storage (hass.data) for quick restarts

**Implementation**:

```python
class BarcoDataUpdateCoordinator:
    def __init__(self, ...):
        self._introspection_cache: dict[str, Any] = {}
        
    async def async_introspect_cached(self, object: str) -> dict:
        """Get introspection data with caching."""
        if object not in self._introspection_cache:
            result = await self.device.send_request("introspect", {
                "object": object,
                "recursive": False,
            })
            self._introspection_cache[object] = result
        return self._introspection_cache[object]
        
    async def refresh_introspection(self) -> None:
        """Refresh introspection cache."""
        self._introspection_cache.clear()
        # Re-introspect key objects
        await self.async_introspect_cached("")
        await self.async_introspect_cached("image")
        await self.async_introspect_cached("illumination")
```

### Connection Pooling

**Options**:

1. **Persistent Connection (Recommended)**
    - Maintains single stream (needed for subscriptions) & reduces latency.
    - Requires robust reconnect logic.
2. **Per Request (Fallback)**
    - Simpler but higher latency & incompatible with push updates.

Feature flag proposal: `BARCO_PULSE_CONNECTION_MODE=per_request` for diagnostics.

Performance Budgets:

| Metric | Target | Notes |
|--------|--------|-------|
| Connect + auth | <3s | Local LAN |
| Batch (10 props) RTT | <250ms | Normal operation |
| Refresh CPU time | <20ms | Parsing only |
| Data dict size | <10KB | Excluding introspection cache |
| Notification latency | <100ms | After receipt |

Instrumentation (DEBUG): log durations & property counts.

### Rate Limiting

Prevent overwhelming projector with rapid requests:

```python
class BarcoDataUpdateCoordinator:
    def __init__(self, ...):
        self._last_request_time: float = 0
        self._min_request_interval: float = 0.1  # 100ms between requests
        
    async def _rate_limit(self) -> None:
        """Ensure minimum interval between requests."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.monotonic()
```

---

## Future Enhancements

### Phase 2: Advanced Features

1. **Subscription-Based Updates**:
   - Subscribe to property changes via `property.subscribe`
   - Handle `property.changed` notifications asynchronously
   - Reduce polling frequency, rely on push notifications

2. **Event Monitoring**:
   - Subscribe to `keydispatcher.keyevent` for remote button presses
   - Subscribe to `notification.emitted` for system notifications
   - Fire HA events for automations

3. **Advanced Blending**:
   - Multi-projector blending zones
   - Blend image upload
   - Advanced color calibration

4. **Lens Control**:
   - Motorized lens position (zoom, focus, shift)
   - Lens memory presets
   - Auto-calibration triggers

5. **Network Discovery**:
   - Zeroconf/mDNS discovery of Barco projectors on LAN
   - Auto-configure discovered projectors

6. **Diagnostics**:
   - Download and parse notification logs
   - Temperature monitoring
   - Fan speed monitoring
   - Laser health metrics

### Phase 3: Professional Features

1. **Multi-Projector Sync**:
   - Coordinate multiple projectors
   - Synchronized power on/off
   - Synchronized source switching

2. **Calibration Integration**:
   - Integration with external calibration tools
   - LUT upload/download
   - Gamma curve management

3. **Show Control**:
   - Integration with show control systems
   - DMX/ArtNet support (projector supports `dmx.artnet`)
   - Scheduler automation

