# Pulse API: JSON-RPC Reference Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Connecting to Pulse Services](#connecting-to-pulse-services)
3. [Quick Start Guide](#quick-start-guide)
4. [Object and Method Naming](#object-and-method-naming)
5. [Type Support](#type-support)
6. [Parameters](#parameters)
7. [Authentication](#authentication)
8. [Service API](#service-api)
9. [Introspection API](#introspection-api)
10. [File Endpoints](#file-endpoints)
11. [Programmer's Guide](#programmers-guide)
12. [API Reference](#api-reference)

---

## Introduction

This document describes the application programmer's interface to Pulse projectors. The facade API is based on the JSON-RPC 2.0 protocol and provides access to Pulse services to clients. The transport protocol for external clients is TCP/IP.

---

## Connecting to Pulse Services

### Network Connection

If the projector is on a network, TCP/IP can be used to connect to Pulse services.

- **Port Number**: 9090
- **Protocol**: TCP/IP

### Serial Port Connection

A serial cable can be connected to the projector to access Pulse services.

**Connection**: 
- Host: 9-pin female connector
- Projector: 9-pin male connector
- Pin configuration: Pin 2 to Pin 2, Pin 3 to Pin 3, Pin 5 to Pin 5

**RS232 Communication Parameters**:

| Parameter | Value |
|-----------|-------|
| Baud rate | 19200 |
| Parity | None |
| Data bits | 8 |
| Stop bits | 1 |
| Flow control | None |

---

## Quick Start Guide

### Power On Projector

```json
{
  "jsonrpc": "2.0",
  "method": "system.poweron"
}
```

### Power Off Projector

```json
{
  "jsonrpc": "2.0",
  "method": "system.poweroff"
}
```

### Select DisplayPort 1 as Input Source

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "params": {
    "property": "image.window.main.source",
    "value": "DisplayPort 1"
  }
}
```

### Select HDMI as Input Source

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "params": {
    "property": "image.window.main.source",
    "value": "HDMI"
  }
}
```

---

## Object and Method Naming

Objects and members use dot notation in lowercase format (JavaScript-like notation). Members can be a method, property, signal, or object.

**Example method invocation**:
```
"method": "foo.echo"
```

**Hierarchical object notation**:
```
tempctrl.fans
tempctrl.fans.mainfan
tempctrl.fans.lampblower
```

**Accessing a property**:
```
tempctrl.fans.mainfan.rpm
```

---

## Type Support

### Basic Types

- **string**: e.g., `"hello"`
- **integer**: e.g., `114`
- **float**: e.g., `3.141592653589793`
- **boolean**: e.g., `true`

### Container Types

- **array**: e.g., `["hello", "to", "you"]`
- **object**: e.g., `{"name": "Johnny", "age": 30, "children": ["Agnes", "Tim"]}`
- **dictionary**: e.g., `{"Norway": 11, "Germany": 5, "Sweden": 2}`

---

## Parameters

Both "by name" and "by position" parameter passing are supported.

---

## Authentication

A client session must start with an authentication request containing a secret passcode. Authentication is only necessary when a higher level than End User is required.

### Authentication Request

```json
{
  "jsonrpc": "2.0",
  "method": "authenticate",
  "params": {
    "code": 98765
  },
  "id": 1
}
```

### Authentication Response

```json
{
  "jsonrpc": "2.0",
  "result": true,
  "id": 1
}
```

**Parameters**:

| Property | Type | Required | Comments |
|----------|------|----------|----------|
| jsonrpc | string | yes | "2.0" |
| method | string | yes | "authenticate" |
| params | object | yes | `{"code": integer}` - 5 digit authentication code |
| id | integer/string | no | request id |

---

## Service API

### Methods

**Method Invocation Example**:

```json
{
  "jsonrpc": "2.0",
  "method": "ledctrl.blink",
  "params": {
    "led": "systemstatus",
    "color": "red",
    "period": 42
  },
  "id": 3
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "result": 0,
  "id": 3
}
```

### Properties

#### Write One Property

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "params": {
    "property": "objectname.propertyname",
    "value": 100
  },
  "id": 3
}
```

**Best Practice**: Wait for confirmation before setting the same property again to avoid flooding the server.

#### Read One Property

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {
    "property": "objectname.propertyname"
  },
  "id": 4
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "result": 100,
  "id": 4
}
```

#### Read Multiple Properties

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {
    "property": ["objectname.propertyname", "objectname.someproperty"]
  },
  "id": 5
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "object.propertyname": 100,
    "objectname.someproperty": "foo"
  },
  "id": 5
}
```

#### Subscribe to Property Changes

```json
{
  "jsonrpc": "2.0",
  "method": "property.subscribe",
  "params": {
    "property": "objectname.propertyname"
  },
  "id": 3
}
```

#### Subscribe to Multiple Properties

```json
{
  "jsonrpc": "2.0",
  "method": "property.subscribe",
  "params": {
    "property": [
      "objectname.propertyname",
      "objectname.otherproperty"
    ]
  },
  "id": 3
}
```

#### Unsubscribe from Property

```json
{
  "jsonrpc": "2.0",
  "method": "property.unsubscribe",
  "params": {
    "property": "objectname.propertyname"
  },
  "id": 3
}
```

### Signals

#### Subscribe to Signal

```json
{
  "jsonrpc": "2.0",
  "method": "signal.subscribe",
  "params": {
    "signal": "objectname.signalname"
  },
  "id": 3
}
```

#### Subscribe to Multiple Signals

```json
{
  "jsonrpc": "2.0",
  "method": "signal.subscribe",
  "params": {
    "signal": [
      "objectname.signalname",
      "otherobject.othersignal"
    ]
  },
  "id": 4
}
```

#### Unsubscribe from Signal

```json
{
  "jsonrpc": "2.0",
  "method": "signal.unsubscribe",
  "params": {
    "signal": "objectname.signalname"
  },
  "id": 5
}
```

### Notifications

Notification messages do not have an `id` field and require no response.

#### Property Change Notification

```json
{
  "jsonrpc": "2.0",
  "method": "property.changed",
  "params": {
    "property": [
      {"objectname.propertyname": 100},
      {"otherobject.otherproperty": "bar"}
    ]
  }
}
```

#### Signal Callback Notification

```json
{
  "jsonrpc": "2.0",
  "method": "signal.callback",
  "params": {
    "signal": [
      {"objectname.signalname": {"arg1": 100, "arg2": "cat"}},
      {"otherobject.othersignal": {"foo": "bar"}}
    ]
  }
}
```

---

## Introspection API

### Read Metadata

Metadata of available objects (methods, properties, signals) can be retrieved. The data is restricted by the client's authenticated access level.

**Request (recursive=true)**:

```json
{
  "jsonrpc": "2.0",
  "method": "introspect",
  "params": {
    "object": "foo",
    "recursive": true
  },
  "id": 1
}
```

**Request (recursive=false)**:

```json
{
  "jsonrpc": "2.0",
  "method": "introspect",
  "params": {
    "object": "motors",
    "recursive": false
  },
  "id": 2
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "name": "motors",
    "objects": [
      {"name": "motors.motor1"},
      {"name": "motors.motor2"},
      {"name": "motors.motor3"}
    ]
  },
  "id": 2
}
```

**Parameters**:

| Property | Type | Required | Default | Comments |
|----------|------|----------|---------|----------|
| jsonrpc | string | yes | - | "2.0" |
| method | string | yes | - | "introspect" |
| params.object | string | no | "" | Object name to introspect |
| params.recursive | bool | no | true | If false, only object names are listed |
| id | string/number | no | - | request id |

### Object Changed Signal

The introspect API provides a signal "modelupdated" to notify when new objects are added or removed.

**Subscribe**:

```json
{
  "jsonrpc": "2.0",
  "method": "signal.subscribe",
  "params": {
    "signal": "modelupdated"
  },
  "id": 2
}
```

**Callback**:

```json
{
  "jsonrpc": "2.0",
  "method": "signal.callback",
  "params": {
    "signal": [
      {
        "introspect.objectchanged": {
          "object": "motors.motor1",
          "newobject": true
        }
      }
    ]
  }
}
```

---

## File Endpoints

Some objects provide endpoints for uploading or downloading data files (e.g., warp grids, blend masks).

### URL Construction

**Format**: `http://<projector-address>/api<file-endpoint>`

**Example**: `http://192.168.1.100/api/image/processing/warp/file/transfer`

### Downloading Files

**Using Browser**: Enter the URL directly

**Using curl**:
```bash
curl -O -J http://192.168.1.100/api/image/processing/warp/file/transfer
```

### Uploading Files

**Using curl**:
```bash
curl -F file=@warpgrid.xml http://192.168.1.100/api/image/processing/warp/file/transfer
```

### Available File Endpoints

| Endpoint | Upload | Download | Description |
|----------|--------|----------|-------------|
| `/api/bio/logger/transfer` | ❌ | ✅ | Download notification log files |
| `/api/notification/logger/transfer` | ❌ | ✅ | Download notification log files |
| `/api/system/license/file/registration` | ❌ | ✅ | Download registration file |
| `/api/ui/capture/lcd` | ❌ | ✅ | Download screen capture of LCD |
| `/api/ui/capture/osd` | ❌ | ✅ | Download screen capture of OSD |
| `/api/ui/splashscreen/file` | ✅ | ❌ | Upload splash screen (800x480 PNG/JPG) |
| `/api/image/processing/warp/file/transfer` | ✅ | ✅ | Warp grid files |
| `/api/image/processing/blend/file/transfer` | ✅ | ✅ | Blend mask files |
| `/api/image/processing/blacklevel/file/transfer` | ✅ | ✅ | Black level mask files |

---

## Programmer's Guide

### Basic Operation

#### Projector State

**Get Current State**:

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "id": 1,
  "params": {
    "property": "system.state"
  }
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "on"
}
```

**Possible States**:
- `boot` - Projector is booting up
- `eco` - Projector is in ECO/power save mode
- `standby` - Projector is in standby mode
- `ready` - Projector is in ready mode
- `conditioning` - Projector is warming up
- `on` - Projector is on
- `deconditioning` - Projector is cooling down

**Subscribe to State Changes**:

```json
{
  "jsonrpc": "2.0",
  "method": "property.subscribe",
  "id": 2,
  "params": {
    "property": ["system.state"]
  }
}
```

**State Change Notification**:

```json
{
  "jsonrpc": "2.0",
  "method": "property.changed",
  "params": {
    "property": [
      {"system.state": "ready"}
    ]
  }
}
```

#### Power On

```json
{
  "jsonrpc": "2.0",
  "method": "system.poweron",
  "id": 3
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": null
}
```

**Note**: Verify the projector is in `standby` or `ready` state before issuing power on command.

#### Power Off

```json
{
  "jsonrpc": "2.0",
  "method": "system.poweroff",
  "id": 4
}
```

**Note**: Verify the projector is in `on` state before issuing power off command.

### Source Input Management

#### Get Active Source

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {
    "property": "image.window.main.source"
  },
  "id": 0
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "result": "DisplayPort 1",
  "id": 0
}
```

#### List Available Sources

```json
{
  "jsonrpc": "2.0",
  "method": "image.source.list",
  "id": 1
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    "DVI 1",
    "DVI 2",
    "DisplayPort 1",
    "DisplayPort 2",
    "Dual DVI",
    "Dual DisplayPort",
    "Dual Head DVI",
    "Dual Head DisplayPort",
    "HDBaseT",
    "HDMI",
    "SDI"
  ]
}
```

#### Set Active Source

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "id": 2,
  "params": {
    "property": "image.window.main.source",
    "value": "DisplayPort 1"
  }
}
```

#### List Connectors

```json
{
  "jsonrpc": "2.0",
  "method": "image.connector.list",
  "id": 1
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    "DisplayPort 1",
    "DisplayPort 2",
    "DVI 1",
    "DVI 2",
    "HDMI",
    "HDBaseT",
    "SDI"
  ]
}
```

#### Get Connector Signal Information

**Translate connector name** (e.g., "DisplayPort 1" → "displayport1"):
- Remove all non-word characters
- Convert to lowercase

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "id": 3,
  "params": {
    "property": "image.connector.displayport1.detectedsignal"
  }
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "active": true,
    "name": "2560x1600 @ 50.10Hz",
    "vertical_total": 1638,
    "horizontal_total": 2720,
    "vertical_resolution": 1600,
    "horizontal_resolution": 2560,
    "vertical_sync_width": 6,
    "vertical_front_porch": 3,
    "vertical_back_porch": 29,
    "horizontal_sync_width": 32,
    "horizontal_front_porch": 48,
    "horizontal_back_porch": 80,
    "horizontal_frequency": 82068.11653672549,
    "vertical_frequency": 50.102710556641114,
    "pixel_rate": 223222961,
    "scan": "Progressive",
    "bits_per_component": 10,
    "color_space": "RGB",
    "signal_range": "0-255",
    "chroma_sampling": "4:4:4",
    "gamma_type": "POWER"
  }
}
```

### Illumination Control

#### Get Illumination State

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {
    "property": "illumination.state"
  },
  "id": 0
}
```

**Response values**: `"On"` or `"Off"`

#### List Illumination Sources

```json
{
  "jsonrpc": "2.0",
  "method": "introspect",
  "id": 0,
  "params": {
    "object": "illumination.sources",
    "recursive": false
  }
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "name": "illumination.sources",
    "objects": [
      {"name": "illumination.sources.laser"}
    ]
  }
}
```

#### Get/Set Laser Power

**Get Power**:

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "id": 1,
  "params": {
    "property": "illumination.sources.laser.power"
  }
}
```

**Set Power**:

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "id": 3,
  "params": {
    "property": "illumination.sources.laser.power",
    "value": 40
  }
}
```

**Get Min/Max Power**:

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "id": 4,
  "params": {
    "property": "illumination.sources.laser.maxpower"
  }
}
```

### Picture Settings

#### Introspect Image Service

```json
{
  "jsonrpc": "2.0",
  "method": "introspect",
  "params": {
    "object": "image",
    "recursive": false
  },
  "id": 0
}
```

**Response** (excerpt showing brightness property):

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "name": "image",
    "properties": [
      {
        "name": "brightness",
        "type": {
          "base": "float",
          "min": -1,
          "max": 1,
          "step-size": 1,
          "precision": 0.01
        },
        "access": "READ_WRITE",
        "description": "Image brightness/offset. The value is normalized, 0 is default, 1 is 100% offset."
      }
    ]
  }
}
```

#### Get Brightness

```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "id": 2,
  "params": {
    "property": "image.brightness"
  }
}
```

#### Set Brightness

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "params": {
    "property": "image.brightness",
    "value": 0.15
  },
  "id": 4
}
```

### Warping with Grid Files

#### Enable Warp

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "id": 1,
  "params": {
    "property": "image.processing.warp.enable",
    "value": true
  }
}
```

#### Upload Warp File

```bash
curl -F file=@warp.xml http://192.168.1.100/api/image/processing/warp/file/transfer
```

#### Select Warp File

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "id": 2,
  "params": {
    "property": "image.processing.warp.file.selected",
    "value": "warp.xml"
  }
}
```

#### Enable Grid File Warping

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "id": 2,
  "params": {
    "property": "image.processing.warp.file.enable",
    "value": true
  }
}
```

### Blending with Images

#### Upload Blend Mask

```bash
curl -F file=@mask.png http://192.168.1.100/api/image/processing/blend/file/transfer
```

#### Select Blend File

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "id": 1,
  "params": {
    "property": "image.processing.blend.file.selected",
    "value": "mask.png"
  }
}
```

#### Enable Blend Mask

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "id": 2,
  "params": {
    "property": "image.processing.blend.mode",
    "value": "FILE"
  }
}
```

**Supported Image Formats**:
- PNG (up to 16 bit)
- JPEG
- TIFF

**Note**: The interface technically supports grayscale only but will accept color images (uses blue channel only).

### Black Level Adjustment

#### Upload Black Level Mask

```bash
curl -F file=@blacklevel.png http://192.168.1.100/api/image/processing/blacklevel/file/transfer
```

#### Select Black Level File

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "id": 1,
  "params": {
    "property": "image.processing.blacklevel.file.selected",
    "value": "blacklevel.png"
  }
}
```

#### Enable Black Level Mask

```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "id": 2,
  "params": {
    "property": "image.processing.blacklevel.mode",
    "value": "FILE"
  }
}
```

### Environment Information

#### Get Temperature Sensors

```json
{
  "jsonrpc": "2.0",
  "method": "environment.getcontrolblocks",
  "id": 1,
  "params": {
    "type": "Sensor",
    "valuetype": "Temperature"
  }
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "environment.laser.board0.bank0.temperature": 35.3,
    "environment.laser.board0.bank1.temperature": 34.8,
    "environment.temperature.inlet": 25.5,
    "environment.temperature.outlet": 29.4,
    "environment.temperature.mainboard": 40.4
  }
}
```

#### Get Fan Speeds

```json
{
  "jsonrpc": "2.0",
  "method": "environment.getcontrolblocks",
  "id": 2,
  "params": {
    "type": "Sensor",
    "valuetype": "Speed"
  }
}
```

**Response**:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "environment.fan.ar1.tacho": 1800,
    "environment.fan.ar2.tacho": 1850,
    "environment.fan.optics.tacho": 2600,
    "environment.fan.psu.tacho": 1450
  }
}
```

**Available Sensor Types**:
- Sensor
- Filter
- Controller
- Actuator
- Alarm
- GenericBlock

**Available Value Types**:
- Temperature
- Speed
- PWM
- Voltage
- Current
- Power
- Altitude
- Pressure
- Humidity
- And more...

### ECO Mode

To wake up a projector in ECO mode:

1. Send a Wake-on-LAN request with the projector's MAC address
2. Use the power button on the remote control
3. Use the power button on the keypad
4. Send a special command on RS232: `:POWR1\r`

---

## API Reference

### Key Properties

#### System Properties

- `system.state` (enum, read-only): Current projector state
  - Values: `boot`, `eco`, `standby`, `ready`, `conditioning`, `on`, `deconditioning`
  
- `system.targetstate` (enum, read-only): State the unit is transitioning into

- `system.health` (enum, read-only): Global health state
  - Values: `Normal`, `Warning`, `Error`
  
- `system.name` (string): Custom name for the device

- `system.serialnumber` (string, read-only): Serial number

- `system.modelname` (string, read-only): Model name

- `system.firmwareversion` (string, read-only): Firmware version

#### Network Properties

- `network.hostname` (string): Host name

- `network.domain` (string): Domain name

- `network.device.lan.ip4config` (object, read-only): Current IPv4 configuration
  - Fields: `Address`, `Mask`, `Gateway`, `NameServers`

- `network.device.lan.ip4configmanual` (object): Manual IPv4 configuration

- `network.device.lan.carrier` (bool, read-only): Whether device has carrier

- `network.device.lan.state` (enum, read-only): Current device state
  - Values: `CONNECTED`, `DISCONNECTED`, `CONNECTING`, etc.

#### DMX Properties

- `dmx.mode` (string): Current DMX mode

- `dmx.artnet` (bool): ArtNet enabled or not

- `dmx.startchannel` (int): DMX start channel [1-512]

- `dmx.shutdown` (bool): Shutdown enabled

- `dmx.shutdowntimeout` (int): Shutdown timeout in minutes [1-60]

#### User Properties

- `user.authenticationrequired` (bool): Require authentication of all users

- `user.list` (object array, read-only): List of all users

- `user.availablegroups` (string array, read-only): Available user groups

#### UI Properties

- `ui.osd` (bool): Enable/disable on-screen display

- `ui.menu` (bool): Show/hide menu

- `ui.language` (string): User interface language

- `ui.theme` (enum): Theme setting
  - Values: `Light`, `Dark`

- `ui.stealthmode` (enum): Stealth mode setting
  - Values: `Off`, `On`, `OnUntilReboot`

### Key Methods

#### System Methods

- `system.poweron()`: Power on the projector
- `system.poweroff()`: Power off the projector
- `system.gotoready()`: Set device from standby to ready state
- `system.gotoeco()`: Set device to eco state
- `system.activity()`: Signal user activity (resets timeout timers)
- `system.reset(domains)`: Reset selected domains
- `system.resetall()`: Reset all domains
- `system.listresetdomains()`: Returns list of available reset domains

#### Image/Source Methods

- `image.source.list()`: Get list of available sources
- `image.connector.list()`: Get list of available connectors
- `image.source.[name].listconnectors()`: List connectors used by a specific source

#### Environment Methods

- `environment.getcontrolblocks(type, valuetype)`: Get control block values
- `environment.getalarminfo()`: Get alarm information
- `environment.getallcontrolblocks()`: Get all control blocks

#### Notification Methods

- `notification.list()`: List all active notifications
- `notification.dismiss(id, response)`: Dismiss a notification
- `notification.suppress(code)`: Suppress a notification code
- `notification.unsuppress(code)`: Unsuppress a notification code
- `notification.log(minimumseverity, start, count)`: List received notifications

#### User Methods

- `login()`: Authenticate user
- `logout()`: De-authenticate user
- `getchallenge()`: Get challenge for key-based authentication
- `generatenewtoken()`: Request new token for authenticated user

#### Network Methods

- `network.list()`: List of logical device IDs

#### Scheduler Methods

- `scheduler.create(name)`: Create a new scheduled action

### Key Signals

- `modelupdated`: Signals when functionality appears or disappears
  - Params: `object` (string), `newobject` (bool), `reason` (string), `accesslevel` (enum)

- `keydispatcher.keyevent`: Raised when user presses a physical key
  - Params: `key` (string), `type` (enum), `source` (string)

- `notification.emitted`: New notification emitted
  - Params: `notification` (object)

- `notification.dismissed`: Notification dismissed
  - Params: `id` (string), `response` (enum)

- `loggedout`: User logged out
  - Params: `reason` (enum)

- `system.date.systemdatechanged`: Date/time changed

- `system.identificationchanged`: Identification changed
  - Params: `identification` (string)

---

## Notes and Best Practices

### Performance

- Wait for confirmation before setting the same property again
- Avoid flooding the server with unnecessary requests
- Use subscriptions for monitoring changes rather than polling

### Authentication

- End User access does not require authentication
- Use authentication for Power User, Administrator, or Service Partner levels
- 5-digit authentication code required

### Object Naming

- Convert source/connector names to object names by:
  1. Removing all non-word characters
  2. Converting to lowercase
  - Example: "DisplayPort 1" → "displayport1"

### Error Handling

- Check projector state before issuing power commands
- Verify file formats match requirements for upload operations
- Handle notification callbacks appropriately

### File Operations

- Blend mask resolution must match projector's blend layer resolution
- Black level mask resolution must match projector's black level layer resolution
- Supported image formats: PNG (up to 16-bit), JPEG, TIFF
- Warp grid format compatible with MCM500/400