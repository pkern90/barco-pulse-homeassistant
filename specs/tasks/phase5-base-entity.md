# Phase 5: Base Entity

## 5.1 Base Entity Class (`custom_components/barco_pulse/entity.py`)

### Imports
- [ ] Import `from __future__ import annotations`
- [ ] Import `CoordinatorEntity` from `homeassistant.helpers.update_coordinator`
- [ ] Import `DeviceInfo` from `homeassistant.helpers.entity`
- [ ] Import constants from `const.py`
- [ ] Import `BarcoDataUpdateCoordinator` from `coordinator.py`
- [ ] Add `TYPE_CHECKING` import for `BarcoDataUpdateCoordinator`

### Base Entity Class
- [ ] Create `BarcoEntity` extending `CoordinatorEntity[BarcoDataUpdateCoordinator]`
- [ ] Set `_attr_has_entity_name = True`

### Initialization
- [ ] Implement `__init__(coordinator)` method
- [ ] Call `super().__init__(coordinator)`
- [ ] Build `_attr_device_info` DeviceInfo dict

### Device Info
- [ ] Set `identifiers` to `{(DOMAIN, coordinator.config_entry.entry_id)}`
- [ ] Set `name` to `coordinator.config_entry.title`
- [ ] Set `manufacturer` to `"Barco"`
- [ ] Set `model` from `coordinator.data.get("system.modelname", "Pulse")`
- [ ] Set `sw_version` from `coordinator.data.get("system.firmwareversion")`

### Availability Property
- [ ] Implement `@property def available()` returning bool
- [ ] Return `self.coordinator.last_update_success`

### Attribution
- [ ] Add `_attr_attribution = ATTRIBUTION` class attribute
