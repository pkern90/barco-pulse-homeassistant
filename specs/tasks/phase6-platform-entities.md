# Phase 6: Platform Entities

## 6.1 Binary Sensors (`custom_components/barco_pulse/binary_sensor.py`)

### Imports and Setup
- [x] Import `from __future__ import annotations`
- [x] Import `dataclass`, `Callable`
- [x] Import `BinarySensorEntity`, `BinarySensorEntityDescription`, `BinarySensorDeviceClass`
- [x] Import `HomeAssistant`, `ConfigEntry`
- [x] Import `AddEntitiesCallback` from `homeassistant.helpers.entity_platform`
- [x] Import constants from `const.py`
- [x] Import `BarcoEntity` from `entity.py`
- [x] Import `BarcoRuntimeData` from `data.py`

### Entity Description
- [x] Create `BarcoBinarySensorEntityDescription` dataclass extending `BinarySensorEntityDescription`
- [x] Add `value_fn: Callable[[dict[str, Any]], bool | None]` field
- [x] Use `@dataclass(frozen=True, kw_only=True)` decorator

### Sensor Definitions
- [x] Define `BINARY_SENSORS` tuple with power binary sensor
- [x] Set `key="power"`, `translation_key="power"`
- [x] Set `device_class=BinarySensorDeviceClass.POWER`
- [x] Set `value_fn=lambda data: data.get("state") in POWER_STATES_ACTIVE`

### Binary Sensor Entity Class
- [x] Create `BarcoBinarySensor` extending `BarcoEntity, BinarySensorEntity`
- [x] Add `entity_description: BarcoBinarySensorEntityDescription` type hint

### Initialization
- [x] Implement `__init__(coordinator, description)` method
- [x] Call `super().__init__(coordinator)`
- [x] Store `entity_description = description`
- [x] Set `_attr_unique_id = f"{coordinator.unique_id}_{description.key}"`

### Value Property
- [x] Implement `@property def is_on()` returning `bool | None`
- [x] Return `self.entity_description.value_fn(self.coordinator.data)`

### Platform Setup
- [x] Implement `async def async_setup_entry(hass, entry, async_add_entities)`
- [x] Get coordinator from `entry.runtime_data.coordinator`
- [x] Create list of `BarcoBinarySensor` instances for each description
- [x] Call `async_add_entities(entities)`

## 6.2 Sensors (`custom_components/barco_pulse/sensor.py`)

### Imports and Setup
- [x] Import required types and base classes
- [x] Import `SensorEntity`, `SensorEntityDescription`
- [x] Import `EntityCategory` from `homeassistant.helpers.entity`
- [x] Import constants and base entity

### Entity Description
- [x] Create `BarcoSensorEntityDescription` dataclass
- [x] Add `value_fn: Callable[[dict[str, Any]], str | int | float | None]` field
- [x] Add `enabled_default: bool = True` field

### Sensor Definitions
- [x] Define state sensor with `key="state"`, `translation_key="state"`, `icon="mdi:power"`
- [x] Define serial number sensor with `entity_category=EntityCategory.DIAGNOSTIC`
- [x] Define model name sensor with `entity_category=EntityCategory.DIAGNOSTIC`
- [x] Define firmware version sensor with `entity_category=EntityCategory.DIAGNOSTIC`
- [x] Define laser power sensor showing percentage
- [x] Define active source sensor showing current input

### Sensor Entity Class
- [x] Create `BarcoSensor` extending `BarcoEntity, SensorEntity`
- [x] Implement `__init__(coordinator, description)`
- [x] Set unique_id and enabled_default from description
- [x] Implement `@property def native_value()` using value_fn

### Platform Setup
- [x] Implement `async_setup_entry` creating all sensor entities
- [x] Add all entities at once

## 6.3 Switches (`custom_components/barco_pulse/switch.py`)

### Imports and Setup
- [x] Import `SwitchEntity`, `SwitchDeviceClass`
- [x] Import required base classes and types
- [x] Import constants

### Switch Entity Class
- [x] Create `BarcoPowerSwitch` extending `BarcoEntity, SwitchEntity`
- [x] Set `_attr_translation_key = "power"`
- [x] Set `_attr_device_class = SwitchDeviceClass.SWITCH`

### Initialization
- [x] Implement `__init__(coordinator)` calling super
- [x] Set `_attr_unique_id = f"{coordinator.unique_id}_power_switch"`

### State Property
- [x] Implement `@property def is_on()` returning bool
- [x] Return `self.coordinator.data.get("state") in POWER_STATES_ACTIVE`

### Turn On Method
- [x] Implement `async def async_turn_on(**kwargs)`
- [x] Call `await self.coordinator.device.power_on()`
- [x] Call `await self.coordinator.async_request_refresh()`

### Turn Off Method
- [x] Implement `async def async_turn_off(**kwargs)`
- [x] Call `await self.coordinator.device.power_off()`
- [x] Call `await self.coordinator.async_request_refresh()`

### Platform Setup
- [x] Implement `async_setup_entry` creating power switch entity
- [x] Add entity using `async_add_entities([switch])`

## 6.4 Select Entities (`custom_components/barco_pulse/select.py`)

### Imports and Setup
- [x] Import `SelectEntity` from `homeassistant.components.select`
- [x] Import required base classes and types

### Select Entity Class
- [x] Create `BarcoSourceSelect` extending `BarcoEntity, SelectEntity`
- [x] Set `_attr_translation_key = "source"`
- [x] Set `_attr_icon = "mdi:video-input-hdmi"`

### Initialization
- [x] Implement `__init__(coordinator)` calling super
- [x] Set `_attr_unique_id = f"{coordinator.unique_id}_source"`

### Current Option Property
- [x] Implement `@property def current_option()` returning `str | None`
- [x] Return `self.coordinator.data.get("source")`

### Options Property
- [x] Implement `@property def options()` returning `list[str]`
- [x] Get sources from `self.coordinator.data.get("available_sources", [])`
- [x] Return sources if not empty, else return `["Unknown"]`

### Select Option Method
- [x] Implement `async def async_select_option(option)`
- [x] Call `await self.coordinator.device.set_source(option)`
- [x] Call `await self.coordinator.async_request_refresh()`

### Platform Setup
- [x] Implement `async_setup_entry` creating source select entity
- [x] Add entity using `async_add_entities([select])`

## 6.5 Number Entities (`custom_components/barco_pulse/number.py`)

### Imports and Setup
- [x] Import `NumberEntity`, `NumberDeviceClass`, `NumberMode`
- [x] Import `PERCENTAGE` from `homeassistant.const`
- [x] Import required base classes and types

### Laser Power Number Entity
- [x] Create `BarcoLaserPowerNumber` extending `BarcoEntity, NumberEntity`
- [x] Set `_attr_translation_key = "laser_power"`
- [x] Set `_attr_native_unit_of_measurement = PERCENTAGE`
- [x] Set `_attr_device_class = NumberDeviceClass.POWER_FACTOR`
- [x] Set `_attr_mode = NumberMode.SLIDER`
- [x] Implement `__init__` setting unique_id
- [x] Implement `@property def native_value()` from coordinator data
- [x] Implement `@property def native_min_value()` from `laser_min`
- [x] Implement `@property def native_max_value()` from `laser_max`
- [x] Implement `async def async_set_native_value(value)` calling `set_laser_power()`

### Brightness Number Entity
- [x] Create `BarcoBrightnessNumber` extending `BarcoEntity, NumberEntity`
- [x] Set `_attr_translation_key = "brightness"`
- [x] Set `_attr_native_min_value = -1.0`
- [x] Set `_attr_native_max_value = 1.0`
- [x] Set `_attr_native_step = 0.01`
- [x] Set `_attr_mode = NumberMode.SLIDER`
- [x] Implement `__init__` setting unique_id
- [x] Implement `@property def native_value()` from coordinator data
- [x] Implement `async def async_set_native_value(value)` calling `set_brightness()`

### Contrast Number Entity
- [x] Create `BarcoContrastNumber` with same pattern as brightness
- [x] Set appropriate translation_key and unique_id
- [x] Implement value property and set method

### Saturation Number Entity
- [x] Create `BarcoSaturationNumber` with same pattern as brightness
- [x] Set appropriate translation_key and unique_id
- [x] Implement value property and set method

### Hue Number Entity
- [x] Create `BarcoHueNumber` with same pattern as brightness
- [x] Set appropriate translation_key and unique_id
- [x] Implement value property and set method

### Platform Setup
- [x] Implement `async_setup_entry` creating all number entities
- [x] Add all entities at once: laser power, brightness, contrast, saturation, hue

## 6.6 Remote Entity (`custom_components/barco_pulse/remote.py`)

### Imports and Setup
- [x] Import `RemoteEntity` from `homeassistant.components.remote`
- [x] Import `Iterable` from `collections.abc`
- [x] Import required base classes and types

### Remote Entity Class
- [x] Create `BarcoRemote` extending `BarcoEntity, RemoteEntity`
- [x] Set `_attr_translation_key = "remote"`

### Initialization
- [x] Implement `__init__(coordinator)` calling super
- [x] Set `_attr_unique_id = f"{coordinator.unique_id}_remote"`

### Is On Property
- [x] Implement `@property def is_on()` returning bool
- [x] Return `self.coordinator.data.get("state") in POWER_STATES_ACTIVE`

### Turn On Method
- [x] Implement `async def async_turn_on(**kwargs)`
- [x] Call `await self.coordinator.device.power_on()`
- [x] Call `await self.coordinator.async_request_refresh()`

### Turn Off Method
- [x] Implement `async def async_turn_off(**kwargs)`
- [x] Call `await self.coordinator.device.power_off()`
- [x] Call `await self.coordinator.async_request_refresh()`

### Send Command Method
- [x] Implement `async def async_send_command(command, **kwargs)`
- [x] Iterate through command iterable
- [x] Handle `source_*` commands by extracting source name and calling `set_source()`
- [x] Call `await self.coordinator.async_request_refresh()` after commands

### Platform Setup
- [x] Implement `async_setup_entry` creating remote entity
- [x] Add entity using `async_add_entities([remote])`
