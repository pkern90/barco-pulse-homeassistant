# Phase 6: Platform Entities

## 6.1 Binary Sensors (`custom_components/barco_pulse/binary_sensor.py`)

### Imports and Setup
- [ ] Import `from __future__ import annotations`
- [ ] Import `dataclass`, `Callable`
- [ ] Import `BinarySensorEntity`, `BinarySensorEntityDescription`, `BinarySensorDeviceClass`
- [ ] Import `HomeAssistant`, `ConfigEntry`
- [ ] Import `AddEntitiesCallback` from `homeassistant.helpers.entity_platform`
- [ ] Import constants from `const.py`
- [ ] Import `BarcoEntity` from `entity.py`
- [ ] Import `BarcoRuntimeData` from `data.py`

### Entity Description
- [ ] Create `BarcoBinarySensorEntityDescription` dataclass extending `BinarySensorEntityDescription`
- [ ] Add `value_fn: Callable[[dict[str, Any]], bool | None]` field
- [ ] Use `@dataclass(frozen=True, kw_only=True)` decorator

### Sensor Definitions
- [ ] Define `BINARY_SENSORS` tuple with power binary sensor
- [ ] Set `key="power"`, `translation_key="power"`
- [ ] Set `device_class=BinarySensorDeviceClass.POWER`
- [ ] Set `value_fn=lambda data: data.get("state") in POWER_STATES_ACTIVE`

### Binary Sensor Entity Class
- [ ] Create `BarcoBinarySensor` extending `BarcoEntity, BinarySensorEntity`
- [ ] Add `entity_description: BarcoBinarySensorEntityDescription` type hint

### Initialization
- [ ] Implement `__init__(coordinator, description)` method
- [ ] Call `super().__init__(coordinator)`
- [ ] Store `entity_description = description`
- [ ] Set `_attr_unique_id = f"{coordinator.unique_id}_{description.key}"`

### Value Property
- [ ] Implement `@property def is_on()` returning `bool | None`
- [ ] Return `self.entity_description.value_fn(self.coordinator.data)`

### Platform Setup
- [ ] Implement `async def async_setup_entry(hass, entry, async_add_entities)`
- [ ] Get coordinator from `entry.runtime_data.coordinator`
- [ ] Create list of `BarcoBinarySensor` instances for each description
- [ ] Call `async_add_entities(entities)`

## 6.2 Sensors (`custom_components/barco_pulse/sensor.py`)

### Imports and Setup
- [ ] Import required types and base classes
- [ ] Import `SensorEntity`, `SensorEntityDescription`
- [ ] Import `EntityCategory` from `homeassistant.helpers.entity`
- [ ] Import constants and base entity

### Entity Description
- [ ] Create `BarcoSensorEntityDescription` dataclass
- [ ] Add `value_fn: Callable[[dict[str, Any]], str | int | float | None]` field
- [ ] Add `enabled_default: bool = True` field

### Sensor Definitions
- [ ] Define state sensor with `key="state"`, `translation_key="state"`, `icon="mdi:power"`
- [ ] Define serial number sensor with `entity_category=EntityCategory.DIAGNOSTIC`
- [ ] Define model name sensor with `entity_category=EntityCategory.DIAGNOSTIC`
- [ ] Define firmware version sensor with `entity_category=EntityCategory.DIAGNOSTIC`
- [ ] Define laser power sensor showing percentage
- [ ] Define active source sensor showing current input

### Sensor Entity Class
- [ ] Create `BarcoSensor` extending `BarcoEntity, SensorEntity`
- [ ] Implement `__init__(coordinator, description)`
- [ ] Set unique_id and enabled_default from description
- [ ] Implement `@property def native_value()` using value_fn

### Platform Setup
- [ ] Implement `async_setup_entry` creating all sensor entities
- [ ] Add all entities at once

## 6.3 Switches (`custom_components/barco_pulse/switch.py`)

### Imports and Setup
- [ ] Import `SwitchEntity`, `SwitchDeviceClass`
- [ ] Import required base classes and types
- [ ] Import constants

### Switch Entity Class
- [ ] Create `BarcoPowerSwitch` extending `BarcoEntity, SwitchEntity`
- [ ] Set `_attr_translation_key = "power"`
- [ ] Set `_attr_device_class = SwitchDeviceClass.SWITCH`

### Initialization
- [ ] Implement `__init__(coordinator)` calling super
- [ ] Set `_attr_unique_id = f"{coordinator.unique_id}_power_switch"`

### State Property
- [ ] Implement `@property def is_on()` returning bool
- [ ] Return `self.coordinator.data.get("state") in POWER_STATES_ACTIVE`

### Turn On Method
- [ ] Implement `async def async_turn_on(**kwargs)`
- [ ] Call `await self.coordinator.device.power_on()`
- [ ] Call `await self.coordinator.async_request_refresh()`

### Turn Off Method
- [ ] Implement `async def async_turn_off(**kwargs)`
- [ ] Call `await self.coordinator.device.power_off()`
- [ ] Call `await self.coordinator.async_request_refresh()`

### Platform Setup
- [ ] Implement `async_setup_entry` creating power switch entity
- [ ] Add entity using `async_add_entities([switch])`

## 6.4 Select Entities (`custom_components/barco_pulse/select.py`)

### Imports and Setup
- [ ] Import `SelectEntity` from `homeassistant.components.select`
- [ ] Import required base classes and types

### Select Entity Class
- [ ] Create `BarcoSourceSelect` extending `BarcoEntity, SelectEntity`
- [ ] Set `_attr_translation_key = "source"`
- [ ] Set `_attr_icon = "mdi:video-input-hdmi"`

### Initialization
- [ ] Implement `__init__(coordinator)` calling super
- [ ] Set `_attr_unique_id = f"{coordinator.unique_id}_source"`

### Current Option Property
- [ ] Implement `@property def current_option()` returning `str | None`
- [ ] Return `self.coordinator.data.get("source")`

### Options Property
- [ ] Implement `@property def options()` returning `list[str]`
- [ ] Get sources from `self.coordinator.data.get("available_sources", [])`
- [ ] Return sources if not empty, else return `["Unknown"]`

### Select Option Method
- [ ] Implement `async def async_select_option(option)`
- [ ] Call `await self.coordinator.device.set_source(option)`
- [ ] Call `await self.coordinator.async_request_refresh()`

### Platform Setup
- [ ] Implement `async_setup_entry` creating source select entity
- [ ] Add entity using `async_add_entities([select])`

## 6.5 Number Entities (`custom_components/barco_pulse/number.py`)

### Imports and Setup
- [ ] Import `NumberEntity`, `NumberDeviceClass`, `NumberMode`
- [ ] Import `PERCENTAGE` from `homeassistant.const`
- [ ] Import required base classes and types

### Laser Power Number Entity
- [ ] Create `BarcoLaserPowerNumber` extending `BarcoEntity, NumberEntity`
- [ ] Set `_attr_translation_key = "laser_power"`
- [ ] Set `_attr_native_unit_of_measurement = PERCENTAGE`
- [ ] Set `_attr_device_class = NumberDeviceClass.POWER_FACTOR`
- [ ] Set `_attr_mode = NumberMode.SLIDER`
- [ ] Implement `__init__` setting unique_id
- [ ] Implement `@property def native_value()` from coordinator data
- [ ] Implement `@property def native_min_value()` from `laser_min`
- [ ] Implement `@property def native_max_value()` from `laser_max`
- [ ] Implement `async def async_set_native_value(value)` calling `set_laser_power()`

### Brightness Number Entity
- [ ] Create `BarcoBrightnessNumber` extending `BarcoEntity, NumberEntity`
- [ ] Set `_attr_translation_key = "brightness"`
- [ ] Set `_attr_native_min_value = -1.0`
- [ ] Set `_attr_native_max_value = 1.0`
- [ ] Set `_attr_native_step = 0.01`
- [ ] Set `_attr_mode = NumberMode.SLIDER`
- [ ] Implement `__init__` setting unique_id
- [ ] Implement `@property def native_value()` from coordinator data
- [ ] Implement `async def async_set_native_value(value)` calling `set_brightness()`

### Contrast Number Entity
- [ ] Create `BarcoContrastNumber` with same pattern as brightness
- [ ] Set appropriate translation_key and unique_id
- [ ] Implement value property and set method

### Saturation Number Entity
- [ ] Create `BarcoSaturationNumber` with same pattern as brightness
- [ ] Set appropriate translation_key and unique_id
- [ ] Implement value property and set method

### Hue Number Entity
- [ ] Create `BarcoHueNumber` with same pattern as brightness
- [ ] Set appropriate translation_key and unique_id
- [ ] Implement value property and set method

### Platform Setup
- [ ] Implement `async_setup_entry` creating all number entities
- [ ] Add all entities at once: laser power, brightness, contrast, saturation, hue

## 6.6 Remote Entity (`custom_components/barco_pulse/remote.py`)

### Imports and Setup
- [ ] Import `RemoteEntity` from `homeassistant.components.remote`
- [ ] Import `Iterable` from `collections.abc`
- [ ] Import required base classes and types

### Remote Entity Class
- [ ] Create `BarcoRemote` extending `BarcoEntity, RemoteEntity`
- [ ] Set `_attr_translation_key = "remote"`

### Initialization
- [ ] Implement `__init__(coordinator)` calling super
- [ ] Set `_attr_unique_id = f"{coordinator.unique_id}_remote"`

### Is On Property
- [ ] Implement `@property def is_on()` returning bool
- [ ] Return `self.coordinator.data.get("state") in POWER_STATES_ACTIVE`

### Turn On Method
- [ ] Implement `async def async_turn_on(**kwargs)`
- [ ] Call `await self.coordinator.device.power_on()`
- [ ] Call `await self.coordinator.async_request_refresh()`

### Turn Off Method
- [ ] Implement `async def async_turn_off(**kwargs)`
- [ ] Call `await self.coordinator.device.power_off()`
- [ ] Call `await self.coordinator.async_request_refresh()`

### Send Command Method
- [ ] Implement `async def async_send_command(command, **kwargs)`
- [ ] Iterate through command iterable
- [ ] Handle `source_*` commands by extracting source name and calling `set_source()`
- [ ] Call `await self.coordinator.async_request_refresh()` after commands

### Platform Setup
- [ ] Implement `async_setup_entry` creating remote entity
- [ ] Add entity using `async_add_entities([remote])`
