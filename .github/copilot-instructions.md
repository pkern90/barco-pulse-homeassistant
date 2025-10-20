# Copilot Instructions for Barco Pulse Home Assistant Integration

## Project Overview

This is a Home Assistant HACS custom integration for Barco Pulse projectors. The integration communicates with Barco projectors using their JSON-RPC 2.0 API over a hybrid HTTP/0.9 protocol on TCP port 9090 to control power, input sources, illumination, picture settings, and monitor device state.

**Architecture Reference**: See `/specs/ARCHITECTURE.md` for complete architectural design, component patterns, data flow, entity mappings, and implementation details.

**Reference Implementation**: This project follows the same architecture and design patterns as the JVC Projector integration (`~/workspace/jvc_homeassistant`).

**Project Status**: Currently a template-based skeleton. Implementation is in progress to create a production-ready HACS integration.

## Critical Protocol Information

### Barco Pulse Protocol (Hybrid HTTP/0.9)

Barco Pulse projectors use an **unusual hybrid protocol**:

- **Requests**: Standard HTTP/1.1 POST with JSON-RPC 2.0 payload
- **Responses**: Raw JSON **without HTTP headers** (HTTP/0.9-like behavior)

**Critical Constraint**: Standard HTTP libraries (aiohttp, urllib) will fail. Must use **raw TCP sockets** with manual HTTP request construction.

**See**: `/specs/BARCO_HDR_CS_PROTOCOL.md` for complete protocol specification with wire format examples.

### API Specifications

All API documentation is in the `/specs` directory:

- **`ARCHITECTURE.md`**: Complete integration architecture, component design, entity mappings, data flow, and implementation patterns
- **`BARCO_HDR_CS_PROTOCOL.md`**: Protocol specification with wire format examples and connection details
- **`HDR_CS_STATE_DEPENDENT_PROPERTIES.md`**: Power state dependency behavior (critical for coordinator logic)
- **`barco_pulse_api_json_rpc_reference_summary.md`**: Curated subset of API methods (power, state, source, illumination, picture). **Start here** for common features.
- **`barco_pulse_api_json_rpc_reference.md`**: Complete 171-page API reference. Use for advanced features (warp, blend, introspection, subscriptions).
- **`Pulse API_ JSON RPC Reference Documentation.html`**: Original HTML API reference

### Choosing Which Spec to Consult

| Use Case                                                    | Preferred File                                  | Notes                                                                     |
| ----------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------- |
| **Architecture & component design**                         | `ARCHITECTURE.md`                               | Complete design patterns, entity mappings, data flow                      |
| Implement core power & state logic                          | `barco_pulse_api_json_rpc_reference_summary.md` | Faster to scan; includes state list & power methods                       |
| Source selection & listing                                  | Summary first                                   | Falls back to full reference for connector grid position & signal objects |
| Illumination (laser power min/max, dynamic constraints)     | Summary for basic get/set                       | Full reference for edge cases (min/max changes due to lens)               |
| Picture settings (brightness/contrast/etc.)                 | Full reference                                  | Need introspection property metadata (type, min/max, step-size)           |
| Handling notifications (property.changed / signal.callback) | Full reference                                  | Provides full JSON examples & subscription patterns                       |
| Debugging a missing property (-32601)                       | Summary to confirm state dependency             | If still unclear, verify via `introspect` examples in full spec           |
| Adding new advanced entities (warp, blending, gamma)        | Full reference                                  | Contains objects & methods not in summary                                 |

Guidance:

1. **Consult ARCHITECTURE.md first** for component design, entity mappings, and implementation patterns
2. Start with the summary file for any new feature; if you cannot find the property/method or need metadata (constraints/type), jump to the full reference
3. Always cross-check naming: properties use dot notation; when translating displayed source/connector names to object names, remove non-word chars and lowercase (documented in full reference)
4. For dynamic ranges (illumination power, picture floats), prefer using `introspect` (examples in full reference) instead of hardcoding limits
5. Subscription patterns (property.subscribe / signal.subscribe) and notification payload formats live in the full reference—copy those examples when building streaming/async updates later
6. Keep network efficiency: avoid bulk property.get loops if you can subscribe and wait for property.changed notifications (design in future enhancement phase)

## Quick Reference

### Critical API Concepts

See `/specs/ARCHITECTURE.md` for complete details on all components, patterns, and features.

**Power States**: `boot`, `eco`, `standby`, `ready`, `on`, `conditioning`, `deconditioning`

**State-Dependent Properties**: Many properties only available when state = `on` or `ready`. Always check `system.state` first. See `/specs/HDR_CS_STATE_DEPENDENT_PROPERTIES.md`.

**Error Code -32601**: "Property not found" - Usually indicates state dependency, handle gracefully.

### Essential API Methods

- `system.poweron` / `system.poweroff` - Power control
- `property.get` / `property.set` - Property access (supports batch operations)
- `image.source.list` - Get available input sources
- `introspect` - Discover properties and metadata
- `authenticate` - Authenticate with optional 5-digit code

### Component Structure

See `/specs/ARCHITECTURE.md` section "Component Structure" for complete file organization.

Key files:

- `api.py` - Raw TCP JSON-RPC client
- `coordinator.py` - Data update coordinator with state-aware polling
- `config_flow.py` - UI configuration
- `entity.py` - Base entity class
- Platform files: `sensor.py`, `binary_sensor.py`, `switch.py`, `select.py`, `number.py`, `remote.py`

## Development Workflow

### Local Development

```bash
scripts/develop    # Starts Home Assistant with integration loaded
                   # Config stored in ./config/
                   # Uses PYTHONPATH for custom_components access
```

### Linting

```bash
scripts/lint       # Runs ruff format + ruff check --fix
```

**Note**: The integration uses `ruff` (not black/pylint). All code must pass ruff checks.

### Testing

Currently no test suite. Use `scripts/develop` for manual testing with real/simulated projector.

## Code Conventions

### Naming Patterns

- Class names: `Barco<Type>` (e.g., `BarcoSensor`, `BarcoBinarySensor`, `BarcoDataUpdateCoordinator`)
- Constants: UPPER_CASE in `const.py`
- API methods: `async_` prefix for async methods
- Private methods: `_` prefix

### Type Hints

- Use `from __future__ import annotations` at top of every file
- All function parameters and returns must have type hints
- Use `TYPE_CHECKING` for circular import resolution
- Use modern type syntax: `list[str]` not `List[str]`, `dict | None` not `Optional[Dict]`

### Entity Implementation Pattern

```python
@dataclass(frozen=True, kw_only=True)
class BarcoSensorEntityDescription(SensorEntityDescription):
    """Describe Barco sensor entity."""
    enabled_default: bool = True

class BarcoSensor(BarcoEntity, SensorEntity):
    """Barco Pulse sensor entity."""

    entity_description: BarcoSensorEntityDescription

    def __init__(
        self,
        coordinator: BarcoDataUpdateCoordinator,
        description: BarcoSensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"
        self._attr_entity_registry_enabled_default = description.enabled_default

    @property
    def native_value(self) -> str | None:
        """Return the native value."""
        return self.coordinator.data.get(self.entity_description.key)
```

### Coordinator Pattern

```python
class BarcoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Data update coordinator."""

    def __init__(self, hass: HomeAssistant, device: BarcoDevice) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=NAME,
            update_interval=INTERVAL_SLOW,  # Slow when in standby
        )
        self.device = device
        self._connection_lock = asyncio.Lock()
        self._update_lock = asyncio.Lock()
        self._connected = False

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch data from API."""
        async with self._update_lock:
            # 1. Ensure connected
            # 2. Apply rate limiting
            # 3. Get state (always available)
            # 4. Get other properties based on state
            # 5. Update polling interval based on power state
            # 6. Return data dict
```

### Error Handling

- Define custom exceptions inheriting from base API exception
- Coordinator catches API exceptions and converts to `UpdateFailed` or `ConfigEntryAuthFailed`
- Config flow catches API exceptions and maps to user-visible error keys in `translations/en.json`

Example exception hierarchy:

```python
class BarcoError(Exception):
    """Base exception for Barco Pulse."""

class BarcoConnectionError(BarcoError):
    """Connection error."""

class BarcoAuthError(BarcoError):
    """Authentication error."""

class BarcoApiError(BarcoError):
    """API error."""

    def __init__(self, code: int, message: str):
        """Initialize with JSON-RPC error code and message."""
        self.code = code
        self.message = message
        super().__init__(f"API Error {code}: {message}")
```

## Key Files to Update

When implementing Barco Pulse functionality:

1. **`manifest.json`**: Update domain from `integration_blueprint` to `barco_pulse`
2. **`const.py`**: Change `DOMAIN = "barco_pulse"`, update ATTRIBUTION
3. **`api.py`**: Complete rewrite for JSON-RPC over TCP
4. **`coordinator.py`**: Update class names and data structure from coordinator
5. **All platform files**: Rename classes, update entity descriptions, map projector properties to HA entities
6. **`translations/en.json`**: Update config flow strings for Barco Pulse context

## Home Assistant Patterns

### DataUpdateCoordinator

- Centralizes API polling to prevent duplicate requests
- All entities share same coordinator instance
- Call `await coordinator.async_request_refresh()` after entity commands to update state

### ConfigEntry Runtime Data

Modern pattern (HA 2024.6+): Store runtime objects in `entry.runtime_data` as dataclass (see `data.py`).
Access via: `self.coordinator.config_entry.runtime_data.client`

### Device Info

All entities share same device (projector). Device ID uses `(domain, entry_id)` tuple.
Device name from config entry title. Add model/SW version from projector introspection.

## Common Pitfalls

1. **Stale Blueprint Names**: Many references still say `integration_blueprint` - update to `barco_pulse` systematically
2. **Unique IDs**: Must never change once set. Use stable identifier (e.g., projector serial number), not username
3. **Coordinator Timing**: Don't call API directly in entity properties - return cached `coordinator.data`
4. **Async Context**: All I/O must be async. Use `asyncio` streams for TCP socket, not `socket` module
5. **JSON-RPC ID Field**: Requests need `id`, notifications don't. Handle both message types in read loop
6. **State Dependencies**: Always check power state before querying illumination/image properties
7. **HTTP/0.9 Responses**: Use raw TCP sockets; standard HTTP libraries will fail on headerless responses
8. **Connection Cleanup**: Always close connections in finally blocks and register shutdown handlers
