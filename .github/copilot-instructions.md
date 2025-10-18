# Copilot Instructions for Barco Pulse Home Assistant Integration

## Project Overview

This is a Home Assistant custom integration for Barco Pulse projectors. The integration communicates with Barco projectors using their JSON-RPC 2.0 API over TCP (port 9090) to control power, input sources, illumination, picture settings, and monitor device state.

**Project Status**: Currently a template-based skeleton with placeholder API. See `/plan.md` for comprehensive implementation roadmap.

**Critical**: This project is built from the `integration_blueprint` template but many references still use old naming (`integration_blueprint`, `IntegrationBlueprintApiClient`, etc.). When modifying code, update these to `barco_pulse` equivalents.

## Implementation Plan

A detailed implementation plan is available in `/plan.md` covering:

- 9 implementation phases from foundation to release
- Estimated timelines for each component
- Risk assessment and mitigation strategies
- Success criteria for MVP, v1.0, and future releases
- Priority ordering (MVP → Enhanced → Future)

**When working on this project**, always reference `plan.md` to understand the current phase and next steps.

### Current Status

The project is at the beginning of Phase 1 (Foundation & Renaming). Next immediate tasks:

1. Update `const.py` and `manifest.json` with `barco_pulse` naming
2. Rename all classes from `IntegrationBlueprint*` to `BarcoPulse*`
3. Begin implementing JSON-RPC 2.0 TCP API client

## Architecture

### Core Components

- **`api.py`**: API client for JSON-RPC 2.0 communication with projector (currently placeholder using JSONPlaceholder)
- **`coordinator.py`**: DataUpdateCoordinator managing data fetching and entity updates
- **`config_flow.py`**: UI-based configuration flow for adding projectors
- **`entity.py`**: Base entity class with common device info and attribution
- **Platform files** (`sensor.py`, `switch.py`, `binary_sensor.py`): Entity implementations

### Data Flow

1. User configures projector via config flow (host/credentials)
2. `__init__.py` creates API client and coordinator on entry setup
3. Coordinator polls API at defined intervals (default: 1 hour)
4. Entities subscribe to coordinator updates and expose data to Home Assistant
5. Entity commands trigger API calls, then request coordinator refresh

### Entry Point Pattern

```python
async def async_setup_entry(hass, entry):
    # 1. Create coordinator with update interval
    # 2. Store client + coordinator in entry.runtime_data
    # 3. Do initial coordinator refresh
    # 4. Forward setup to platforms
    # 5. Register reload listener
```

## Barco Pulse API Integration

### Key API Concepts (from `pulse-api-docs.md`)

**Connection**: TCP socket to projector IP on port 9090 using JSON-RPC 2.0

**Critical Methods**:

- `system.poweron` / `system.poweroff`: Control projector power
- `property.get` / `property.set`: Read/write properties (e.g., `system.state`, `image.window.main.source`)
- `property.subscribe`: Subscribe to property changes for push notifications
- `introspect`: Discover available objects/properties

**State Values**: `boot`, `eco`, `standby`, `ready`, `conditioning`, `on`, `deconditioning`

**Source Management**:

- Get active: `property.get` on `image.window.main.source`
- List available: `image.source.list` method
- Set active: `property.set` with source name (e.g., "DisplayPort 1")

**Notifications**: Subscribed properties send async notifications without `id` field via `property.changed` method

### Implementation Requirements

The current `api.py` is a placeholder. See **Phase 2** in `/plan.md` for detailed API client architecture.

Key requirements:

1. JSON-RPC 2.0 client over TCP socket (asyncio)
2. Methods for power control, source switching, property get/set
3. Support for authentication (`authenticate` method with 5-digit code)
4. Handle notification callbacks for subscriptions
5. Exception mapping: connection errors, auth errors, API errors
6. Background read loop for responses and notifications
7. Request/response correlation using `id` field

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

- Class names: `Barco<Type>` (e.g., `BarcoSensor`, `BarcoSwitch`)
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
class BarcoPulseSensor(IntegrationBlueprintEntity, SensorEntity):
    def __init__(self, coordinator, entity_description):
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self):
        return self.coordinator.data.get("property_name")
```

Entities pull data from `self.coordinator.data` (set by coordinator's `_async_update_data`).

### Error Handling

- Define custom exceptions inheriting from base API exception
- Coordinator catches API exceptions and converts to `UpdateFailed` or `ConfigEntryAuthFailed`
- Config flow catches API exceptions and maps to user-visible error keys in `translations/en.json`

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
