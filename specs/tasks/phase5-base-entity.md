# Phase 5: Base Entity

## 5.1 Base Entity Class (`custom_components/barco_pulse/entity.py`)

### Imports
- [x] Import `from __future__ import annotations`
- [x] Import `CoordinatorEntity` from `homeassistant.helpers.update_coordinator`
- [x] Import `DeviceInfo` from `homeassistant.helpers.entity`
- [x] Import constants from `const.py`
- [x] Import `BarcoDataUpdateCoordinator` from `coordinator.py`
- [x] Add `TYPE_CHECKING` import for `BarcoDataUpdateCoordinator`

### Base Entity Class
- [x] Create `BarcoEntity` extending `CoordinatorEntity[BarcoDataUpdateCoordinator]`
- [x] Set `_attr_has_entity_name = True`

### Initialization
- [x] Implement `__init__(coordinator)` method
- [x] Call `super().__init__(coordinator)`
- [x] Build `_attr_device_info` DeviceInfo dict

### Device Info
- [x] Set `identifiers` to `{(DOMAIN, coordinator.config_entry.entry_id)}`
- [x] Set `name` to `coordinator.config_entry.title`
- [x] Set `manufacturer` to `"Barco"`
- [x] Set `model` from `coordinator.data.get("system.modelname", "Pulse")`
- [x] Set `sw_version` from `coordinator.data.get("system.firmwareversion")`

### Availability Property
- [x] Implement `@property def available()` returning bool
- [x] Return `self.coordinator.last_update_success`

### Attribution
- [x] Add `_attr_attribution = ATTRIBUTION` class attribute
