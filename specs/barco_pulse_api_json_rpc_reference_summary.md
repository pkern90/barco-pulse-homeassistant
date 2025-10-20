# Barco Pulse API: JSON-RPC Reference Summary

**Document Version**: Summary of complete API reference  
**Original Document**: `barco_pulse_api_json_rpc_reference.md` (11,040 lines)  
**Last Updated**: October 20, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Introduction](#introduction)
4. [Authentication](#authentication)
5. [Service API](#service-api)
6. [Introspection API](#introspection-api)
7. [File Endpoints](#file-endpoints)
8. [Programmers Guide](#programmers-guide)
9. [Properties Reference](#properties-reference)
10. [Methods Reference](#methods-reference)
11. [Signals Reference](#signals-reference)

---

## Overview

This document provides a comprehensive summary of the Barco Pulse API JSON-RPC reference documentation. The API provides control and monitoring capabilities for Barco Pulse projectors through a JSON-RPC 2.0 protocol over TCP/IP or serial connection.

**Purpose**: The facade API enables clients to access Pulse projector services for controlling power, input sources, illumination, picture settings, warping, blending, and monitoring device state.

**Protocol**: JSON-RPC 2.0  
**Transport**: TCP/IP (primary) or Serial Port (RS-232)  
**Default Port**: 9090 (TCP/IP)

### Critical Transport Detail (Hybrid HTTP/0.9 Behavior)
Requests must be sent as manual HTTP/1.1 POST frames over a raw TCP socket. Responses are **raw JSON only (no HTTP headers)** – effectively HTTP/0.9 style. Standard HTTP client libraries that expect response headers (e.g. `aiohttp`, `requests`) will fail parsing the response. Implement a custom socket routine that:
1. Opens TCP connection to port 9090
2. Sends properly formed HTTP request with Content-Length
3. Reads until a full JSON object is received (brace balance or length-based)
4. Parses JSON-RPC response / notification

Example low-level request (wire format):
```
POST / HTTP/1.1
Host: <projector-ip>
Content-Type: application/json
Content-Length: <len>\r\n
\n
{"jsonrpc":"2.0","method":"system.state","id":1}
```
Response (no status line or headers):
```
{"jsonrpc":"2.0","result":"on","id":1}
```

### Notifications
JSON-RPC notifications (e.g. `property.changed`, `signal.callback`) have **no `id`** and the client must not reply. They are pushed asynchronously after subscription.

> **Reference**: Original document lines 1-52, 44-58

---

## Quick Reference

### Common Operations

#### Power Control
```json
// Power On
{"jsonrpc": "2.0", "method": "system.poweron"}

// Power Off
{"jsonrpc": "2.0", "method": "system.poweroff"}

// Get Power State
{"jsonrpc": "2.0", "method": "property.get", "params": {"property": "system.state"}, "id": 1}
```

#### Input Source Selection
```json
// List Available Sources
{"jsonrpc": "2.0", "method": "image.source.list", "id": 1}

// Select DisplayPort 1
{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "DisplayPort 1"}, "id": 2}

// Select HDMI
{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "HDMI"}, "id": 3}
```

#### Property Access
```json
// Read Property
{"jsonrpc": "2.0", "method": "property.get", "params": {"property": "property.name"}, "id": 1}

// Write Property
{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "property.name", "value": <value>}, "id": 2}

// Subscribe to Property Changes
{"jsonrpc": "2.0", "method": "property.subscribe", "params": {"property": ["property.name"]}, "id": 3}
```

> **Reference**: Original document lines 84-158

---

## Introduction

### Connecting to Pulse Services

#### Network Connection (TCP/IP)
- **Protocol**: TCP/IP
- **Port**: 9090
- **Connection Type**: Persistent TCP socket
- **Format**: HTTP POST with JSON-RPC 2.0 payload

> **Reference**: Lines 59-66

#### Serial Port Connection (RS-232)
- **Cable**: Standard serial cable (9-pin female to host, 9-pin male to projector)
- **Pin Mapping**: Pin 2↔2, Pin 3↔3, Pin 5↔5

**RS-232 Parameters**:
| Parameter | Value |
|-----------|-------|
| Baud rate | 19200 |
| Parity | None |
| Data bits | 8 |
| Stop bits | 1 |
| Flow control | None |

> **Reference**: Lines 67-82

---

### Object and Method Naming

Objects and members use **dot notation** in lowercase format (JavaScript-like notation).

**Syntax**: `object.subobject.member`

**Examples**:
```
system.poweron              # Method to power on
system.state                # Property for power state
image.window.main.source    # Nested property for active input
tempctrl.fans.mainfan.rpm   # Deep nesting example
```

**Multiple Objects Pattern**:
```
tempctrl.fans
tempctrl.fans.mainfan
tempctrl.fans.lampblower
```

> **Reference**: Lines 110-129

---

### Type Support

#### Basic Types
- **string**: `"hello"`
- **integer**: `114`
- **float**: `3.141592653589793`
- **boolean**: `true` or `false`

#### Container Types
- **array**: `["hello", "to", "you"]`
- **object**: `{"name": "Johnny", "age": 30, "children": ["Agnes", "Tim"]}`
- **dictionary**: `{"Norway": 11, "Germany": 5, "Sweden": 2}`

> **Reference**: Lines 130-144

---

### Parameters

The API supports both parameter passing methods:
- **By name**: `"params": {"property": "system.state"}`
- **By position**: `"params": ["system.state"]`

> **Reference**: Lines 145-148

---

## Authentication

Authentication sets the **user Access Level** and is only necessary when a higher level than "End User" is required. For normal End User access, authentication can be skipped.

### Authentication Request

```json
{
  "jsonrpc": "2.0",
  "method": "authenticate",
  "params": {"code": 98765},
  "id": 1
}
```

### Authentication Response (Success)

```json
{
  "jsonrpc": "2.0",
  "result": true,
  "id": 1
}
```

### Request Parameters

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| jsonrpc | string | yes | Must be "2.0" |
| method | string | yes | Must be "authenticate" |
| params | object | yes | `{"code": integer}` - 5-digit authentication code |
| id | integer/string | no | Request ID for matching response |

### Response

| Property | Type | Description |
|----------|------|-------------|
| result | bool | `true` if authentication successful |
| error | object | Error object if authentication failed (see JSON-RPC 2.0 spec) |

> **Reference**: Lines 160-208

---

## Service API

The Service API provides access to **methods**, **properties**, **signals**, and **notifications**.

### Request Structure

All requests follow JSON-RPC 2.0 format:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| jsonrpc | string | yes | Must be "2.0" |
| method | string | yes | Method name (see below) |
| params | varies | no | Method-specific parameters |
| id | string/number | no | Request ID (omit for notifications) |

### Response Structure

| Property | Type | Description |
|----------|------|-------------|
| jsonrpc | string | Always "2.0" |
| result | varies | Result value (if successful) |
| error | object | Error object (if failed) |
| id | string/number | Matches request ID |

> **Reference**: Lines 209-228

---

### Methods

Methods are invoked using the `method` field in the JSON-RPC request.

**Example - Method Invocation**:
```json
{
  "jsonrpc": "2.0",
  "method": "ledctrl.blink",
  "params": {"led": "systemstatus", "color": "red", "period": 42},
  "id": 3
}
```

> **Reference**: Lines 229-233

---

### Properties

Properties can be read, written, and monitored for changes.

#### Read Single Property (property.get)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "system.state"},
  "id": 1
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": "on",
  "id": 1
}
```

> **Reference**: Lines 234-246

---

#### Write Single Property (property.set)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "params": {"property": "image.brightness", "value": 0.5},
  "id": 2
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": true,
  "id": 2
}
```

> **Reference**: Lines 247-254

---

#### Read Multiple Properties (property.get with array)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {
    "property": ["system.state", "system.modelname", "illumination.sources.laser.power"]
  },
  "id": 3
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "system.state": "on",
    "system.modelname": "Pulse",
    "illumination.sources.laser.power": 75
  },
  "id": 3
}
```

> **Reference**: Lines 255-298

---

#### Write Multiple Properties (property.set with object)
The base documentation excerpt does **not** define a batch form of `property.set` accepting an object map of multiple properties. Each call sets a single property using `{"property": <path>, "value": <value>}`. If multi-write behavior exists, it is outside the shown reference and should be validated via introspection before use. Best practice: issue sequential `property.set` requests and wait for each confirmation to avoid flooding.

> **Reference**: Lines 299-332 (single-property example)

---

#### Subscribe to Property Changes (property.subscribe)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.subscribe",
  "params": {"property": ["system.state", "image.brightness"]},
  "id": 5
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": true,
  "id": 5
}
```

**Notification (when property changes)**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.changed",
  "params": {
    "property": [
      {"system.state": "on"}
    ]
  }
}
```

> **Reference**: Lines 333-391

### Property Change Best Practices
Avoid spamming repeated `property.set` commands for the same property without awaiting the prior confirmation. Flooding can reduce server performance.

---

#### Unsubscribe from Property Changes (property.unsubscribe)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.unsubscribe",
  "params": {"property": ["system.state"]},
  "id": 6
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": true,
  "id": 6
}
```

> **Reference**: Lines 392-425

---

### Signals and Notifications

Signals provide event notifications. Clients subscribe to signals and receive callbacks when events occur.

#### Subscribe to Signal (signal.subscribe)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "signal.subscribe",
  "params": {"signal": "modelupdated"},
  "id": 2
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": true,
  "id": 2
}
```

#### Signal Callback

**Notification**:
```json
{
  "jsonrpc": "2.0",
  "method": "signal.callback",
  "params": {
    "signal": [
      {"introspect.objectchanged": {"object": "motors.motor1", "newobject": true}}
    ]
  }
}
```

> **Reference**: Lines 426-558

---

## Introspection API

The Introspection API enables discovery of available objects, methods, properties, and signals with their metadata.

### Introspect Method

#### Recursive Introspection

**Request** (by name):
```json
{
  "jsonrpc": "2.0",
  "method": "introspect",
  "params": {"object": "foo", "recursive": true},
  "id": 1
}
```

**Request** (by position):
```json
{
  "jsonrpc": "2.0",
  "method": "introspect",
  "params": ["foo", true],
  "id": 1
}
```

**Response** (partial example):
```json
{
  "jsonrpc": "2.0",
  "result": {
    "name": "foo",
    "methods": [
      {"name": "echo", ...}
    ],
    "properties": [...],
    "objects": [...]
  },
  "id": 1
}
```

> **Reference**: Lines 561-595

---

#### Non-Recursive Introspection

Retrieves only immediate child object names (one level deep).

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "introspect",
  "params": {"object": "motors", "recursive": false},
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

> **Reference**: Lines 596-634

---

### Introspection Parameters

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| object | string | no | "" (root) | Object name to introspect (dot notation) |
| recursive | bool | no | true | If false, only lists immediate child object names |

### Introspection Response

The response contains comprehensive metadata including:
- **Methods**: Name, parameters, return type, description
- **Properties**: Name, type, constraints (min/max/step), access level, description
- **Signals**: Name, parameters, description
- **Objects**: Child object names

> **Reference**: Lines 635-730

---

### Object Changed Signal

The `modelupdated` signal notifies when objects are added or removed.

**Subscribe**:
```json
{
  "jsonrpc": "2.0",
  "method": "signal.subscribe",
  "params": {"signal": "modelupdated"},
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
      {"introspect.objectchanged": {"object": "motors.motor1", "newobject": true}}
    ]
  }
}
```

**Callback Arguments**:
| Argument | Type | Description |
|----------|------|-------------|
| object | string | Name of object |
| isnew | bool | `true` if object is new, `false` if object is lost |

> **Reference**: Lines 661-700

---

## File Endpoints

File endpoints provide HTTP-based upload/download for various file types (warp grids, blending images, logs, etc.).

### Download Files

**URL Construction**:
```
http://<projector-ip>/api/<endpoint-path>
```

**Example - Download via Browser**:
```
http://192.168.1.100/api/image/processing/warp/file/transfer
```

**Example - Download via curl**:
```bash
curl -O -J http://192.168.1.100/api/image/processing/warp/file/transfer
```

**Example - Download via PowerShell**:
```powershell
Invoke-WebRequest -Uri http://192.168.1.100/api/image/processing/warp/file/transfer -Method Get -OutFile warpgrid.xml
```

### Upload Files

**Example - Upload via curl**:
```bash
curl -F file=@warpgrid.xml http://192.168.1.100/api/image/processing/warp/file/transfer
```

> **Reference**: Lines 701-730, 2033-2100

---

### Common File Endpoints

| Endpoint | Upload | Download | Description |
|----------|--------|----------|-------------|
| `/api/bio/logger/transfer` | ❌ | ✅ | Download BIO log files |
| `/api/notification/logger/transfer` | ❌ | ✅ | Download notification log files |
| `/api/system/license/file/registration` | ❌ | ✅ | Download registration file |
| `/api/ui/capture/lcd` | ❌ | ✅ | Download LCD screen capture |
| `/api/ui/capture/osd` | ❌ | ✅ | Download OSD screen capture |
| `/api/ui/splashscreen/file` | ✅ | ❌ | Upload splash screen (800x480 PNG/JPG) |

> **Reference**: Lines 2033-2120

---

## Programmers Guide

This section covers common tasks for controlling the projector.

### Basic Operation

#### Projector State

**Get Current State**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "system.state"},
  "id": 1
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": "on",
  "id": 1
}
```

**State Values**:
- `boot` - Projector is booting up
- `eco` - Projector is in ECO/power save mode
- `standby` - Projector is in standby mode
- `ready` - Projector is in ready mode
- `conditioning` - Projector is warming up
- `on` - Projector is on
- `deconditioning` - Projector is cooling down

> **Reference**: Lines 737-760

---

#### Subscribe to State Changes

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.subscribe",
  "params": {"property": ["system.state"]},
  "id": 2
}
```

**Notification (when state changes)**:
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

> **Reference**: Lines 761-800

---

#### Power On

**Request**:
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
  "result": null,
  "id": 3
}
```

**Notes**:
- Result is `null` (not an error - method returns no value)
- If projector is already on or transitioning, command is ignored
- Best practice: Check state is `standby` or `ready` before powering on

> **Reference**: Lines 801-820

---

#### Power Off

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "system.poweroff",
  "id": 4
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": null,
  "id": 4
}
```

**Notes**:
- If projector is already off or transitioning, command is ignored
- Best practice: Check state is `on` before powering off

> **Reference**: Lines 821-840

---

### Source Input

Source input management consists of **windows**, **sources**, and **connectors**.
- Each window has a source attached
- Each source consists of one or more connectors

#### Get Active Source

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "image.window.main.source"},
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

> **Reference**: Lines 841-865

---

#### List Available Sources

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "image.source.list",
  "id": 1
}
```

**Response** (varies by projector model):
```json
{
  "jsonrpc": "2.0",
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
  ],
  "id": 1
}
```

> **Reference**: Lines 866-900

---

#### Set Active Source

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "params": {
    "property": "image.window.main.source",
    "value": "DisplayPort 1"
  },
  "id": 2
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": true,
  "id": 2
}
```

> **Reference**: Lines 901-920

---

#### Working with Connectors

**Translate Source Name to Object Name**:
```javascript
const sourceName = 'DisplayPort 1';
const objectName = sourceName.replace(/\W/g, '').toLowerCase();
// Result: 'displayport1'
```

**List Connectors for Source** (spec example method name):
```json
{
  "jsonrpc": "2.0",
  "method": "image.source.displayport1.listconnectors",
  "id": 3
}
```

**Response** (fields may include `gridposition` with row/column/plane):
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "gridposition": {"row": 0, "column": 0, "plane": 0},
      "name": "DisplayPort 1"
    }
  ],
  "id": 3
}
```

> **Reference**: Lines 921-1000

---

### Illumination Control

#### Get Laser Power

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "illumination.sources.laser.power"},
  "id": 1
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": 75,
  "id": 1
}
```

#### Set Laser Power

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "params": {
    "property": "illumination.sources.laser.power",
    "value": 80
  },
  "id": 2
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": true,
  "id": 2
}
```

#### Get Power Limits

**Get Maximum Power**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "illumination.sources.laser.maxpower"},
  "id": 4
}
```

**Get Minimum Power**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "illumination.sources.laser.minpower"},
  "id": 5
}
```

> **Reference**: Lines 1300-1440

### Illumination State & Subscriptions
You can also query and subscribe to `illumination.state` which returns `On` or `Off`. Subscribe using `property.subscribe` and handle `property.changed` notifications similarly to other properties.

---

### Picture Settings

Picture settings use introspection to discover property metadata (type, constraints, step-size).

#### Introspect Image Properties

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "introspect",
  "params": {"object": "image", "recursive": false},
  "id": 0
}
```

**Response** (partial):
```json
{
  "jsonrpc": "2.0",
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
        "description": "Image brightness/offset. Normalized, 0 is default, 1 is 100% offset."
      }
    ]
  },
  "id": 0
}
```

> **Reference**: Lines 1441-1500

---

#### Get Brightness

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "image.brightness"},
  "id": 2
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": 0,
  "id": 2
}
```

#### Set Brightness

**Request**:
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

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": true,
  "id": 4
}
```

**Notification**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.changed",
  "params": {
    "property": [
      {"image.brightness": 0.15}
    ]
  }
}
```

**Notes**:
- Use `step-size × precision` for increment/decrement operations
- Example: brightness has step-size=1, precision=0.01 → step=0.01
- Same pattern applies to contrast, saturation, hue, and other image properties

> **Reference**: Lines 1501-1600

---

### Warping with Grid Files

#### Enable Warp Globally

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "property.set",
  "params": {
    "property": "image.processing.warp.enable",
    "value": true
  },
  "id": 1
}
```

#### Upload Warp Grid

Use HTTP file upload to the warp file endpoint:

```bash
curl -F file=@warpgrid.xml http://192.168.1.100/api/image/processing/warp/file/transfer
```

#### Download Current Warp Grid

```bash
curl -O -J http://192.168.1.100/api/image/processing/warp/file/transfer
```

> **Reference**: Lines 1600-1700

---

## Properties Reference

Properties are organized hierarchically using dot notation. All properties listed in the full documentation can be read, but not all can be written.

### Property Indicators

- 🔒 **Read-only property** - Cannot be written
- ✏️ **Read-write property** - Can be read and written

### Key Property Categories

#### System Properties
- `system.state` - Current power state (boot/eco/standby/ready/on/conditioning/deconditioning)
- `system.serialnumber` - Projector serial number
- `system.modelname` - Projector model name
- `system.firmwareversion` - Firmware version

#### Image Properties
- `image.brightness` - Image brightness (-1 to 1, normalized)
- `image.contrast` - Image contrast
- `image.saturation` - Color saturation
- `image.hue` - Color hue
- `image.window.main.source` - Active input source

#### Illumination Properties
- `illumination.sources.laser.power` - Laser power percentage
- `illumination.sources.laser.maxpower` - Maximum laser power limit
- `illumination.sources.laser.minpower` - Minimum laser power limit

#### DMX Properties
- `dmx.artnet` - ArtNet enabled/disabled (bool)
- `dmx.artnetnet` - ArtNet network settings

> **Reference**: Lines 2031-11040 (full property listing throughout document)

---

## Methods Reference

### System Methods
- `system.poweron` - Power on the projector
- `system.poweroff` - Power off the projector

### Property Methods
- `property.get` - Read one or more properties
- `property.set` - Write one or more properties
- `property.subscribe` - Subscribe to property change notifications
- `property.unsubscribe` - Unsubscribe from property notifications

### Signal Methods
- `signal.subscribe` - Subscribe to signal notifications
- `signal.unsubscribe` - Unsubscribe from signal notifications

### Image Methods
- `image.source.list` - List all available input sources

### Introspection Methods
- `introspect` - Discover objects, methods, properties, and signals with metadata

### Authentication Methods
- `authenticate` - Authenticate with access code

> **Reference**: Lines 229-558, scattered throughout document

---

## Signals Reference

### Introspection Signals
- `modelupdated` - Notifies when objects are added or removed
  - **Callback**: `introspect.objectchanged`
  - **Arguments**: `object` (string), `newobject` (bool)

### Property Change Notifications
- `property.changed` - Automatic notification when subscribed properties change
  - **Format**: Array of property name/value pairs
  - **Triggered by**: Any `property.set` operation on subscribed properties

> **Reference**: Lines 333-558, 661-730

---

## Implementation Notes for Home Assistant Integration

### Critical Considerations

1. **Connection Protocol**: Use raw TCP sockets on port 9090, not standard HTTP libraries
2. **State Dependency**: Many properties (laser power, input source) only available when projector state is `on` or `ready`
3. **Authentication**: Optional - only required for higher access levels
4. **Polling Strategy**: Use property subscriptions for real-time updates, supplement with periodic polling
5. **Error Handling**: Handle JSON-RPC error codes: `-32601` (method/property not found – often due to power state), `-32600` (invalid request), `-32700` (parse error). Treat `-32601` for state-dependent properties as non-fatal when projector is not fully on.
6. **Property Discovery**: Use introspection to discover available properties and their constraints
7. **Unique ID**: Use `system.serialnumber` for device unique identifier

### State-Dependent Property Strategy
Always fetch `system.state` first. Only attempt ON-state properties when state is in the active range (commonly `ready` or `on`). Gracefully skip or return `None` on `-32601` for properties like `illumination.sources.laser.power` in standby.

#### Ready vs On vs Transitional States
Active property availability typically spans `ready` and `on`. Transitional states `conditioning` and `deconditioning` may intermittently expose values; treat failures in those states as transient, not fatal. Do NOT query image/illumination properties in `standby`, `eco`, or `boot` to avoid unnecessary `-32601` errors.

| State | Safe to Query Illumination | Safe to Query Image Source | Notes |
|-------|----------------------------|----------------------------|-------|
| standby | no | no | Minimal hardware init |
| eco | no | no | Low power mode |
| boot | no | no | Initializing subsystems |
| conditioning | partial (error-tolerant) | partial (error-tolerant) | Warming up laser/image pipeline |
| ready | yes | yes | Fully initialized (pre-user) |
| on | yes | yes | Normal operating state |
| deconditioning | partial (error-tolerant) | partial (error-tolerant) | Cooling down |

Reference: `HDR_CS_STATE_DEPENDENT_PROPERTIES.md`.

### Subscription Lifecycle
1. Subscribe: `property.subscribe` or `signal.subscribe` with list/identifier.
2. Receive asynchronous notifications:
   - Property changes: `property.changed` with array of `{ "path": value }` objects.
   - Signal callbacks: `signal.callback` with array of `{ "signal.name": {<args>} }` objects.
3. Unsubscribe when no longer needed: `property.unsubscribe` / `signal.unsubscribe`.
4. No ACK is sent for notifications; they omit `id`.

Best practices:
* Perform initial `property.get` after subscribing if you need the current value (subscription alone does not push the current value).
* Batch subscription lists to reduce round trips.
* Debounce rapid property.changed events client-side if updating UI frequently.

### Socket Timeout & Retry Strategy
Recommended defaults:
* Connect timeout: 5 s
* Read timeout per request: 5–10 s (laser warm-up may delay some responses)
* Max consecutive retries on connection errors: 3
* Backoff: exponential (e.g., 1s, 2s, 4s) capped at 5s
* Reset backoff after a successful exchange

Pseudo-flow:
```pseudocode
for attempt in 1..MAX_RETRIES:
  try connect(timeout=5s)
  if success: break
  sleep(2^(attempt-1) seconds, max 5)
if not connected: raise BarcoConnectionError

send_request()
wait for JSON response until timeout
if timeout: retry unless non-idempotent or exceeded
```

Handle parse errors (`-32700`) by re-synchronizing the socket (close/reopen). For repeated `-32601` on state-dependent properties, skip further retries until state changes.

### Introspection Performance Impact
`introspect` with `recursive=true` can return large metadata trees (many KB). Use cases:
* One-time cache on startup or after `modelupdated` signal.
* Non-recursive calls (`recursive=false`) to enumerate child object names cheaply, then selectively recurse.

Guidelines:
* Avoid recursive introspection every polling cycle—cache results, refresh on firmware update or `modelupdated`.
* Store constraints (min/max/precision) for UI components to avoid repeated lookups.
* Consider hashing introspection JSON to detect changes.

### Minimal Coordinator Poll Cycle
```pseudocode
state = get(system.state)
if state in ["on", "ready"]:
  fetch(illumination.sources.laser.power, image.window.main.source, image.brightness, image.contrast)
elif state in ["conditioning", "deconditioning"]:
  attempt optional fetches with graceful -32601 handling
else:
  skip dependent properties
```

### Common Error Handling Matrix
| Code | Meaning | Action |
|------|---------|--------|
| -32601 | Not found / unavailable | If state-dependent, treat as None; else log warning |
| -32600 | Invalid request | Check JSON format; developer error |
| -32700 | Parse error | Reset connection; possible truncated response |
| Timeout (client) | No response in window | Retry with backoff; abort after max retries |

### Health & Reconnection
* Track last successful response timestamp; if stale > 2× expected interval, force reconnect.
* On repeated failures, escalate log level and surface HA `UpdateFailed`.

### Telemetry & Debug Recommendations
Log categories:
* Connection lifecycle (open/close/retry)
* Request/response pairs at debug level (omit secrets)
* Error codes mapping
* State transitions

Redact any authentication code in logs.

### Recommended Data Structure

```python
# Coordinator should fetch these properties:
ALWAYS_AVAILABLE = [
    "system.state",
    "system.serialnumber",
    "system.modelname",
    "system.firmwareversion"
]

WHEN_ON = [
    "illumination.sources.laser.power",
    "image.window.main.source",
    "image.brightness",
    "image.contrast"
]

OPTIONAL_WHEN_ON = [
  # Add additional image / illumination properties as discovered via introspection
]

ERROR_CODES = {
  -32601: "Not found (often state-dependent)",
  -32600: "Invalid request format",
  -32700: "Parse error"
}
```

---

## Document References

For detailed information on specific topics, refer to these line ranges in the original document:

| Topic | Line Range |
|-------|------------|
| Introduction & Connection | 1-158 |
| Authentication | 160-208 |
| Service API | 209-558 |
| Introspection API | 559-730 |
| Programmers Guide | 731-2030 |
| File Endpoints List | 2031-2150 |
| Properties Documentation | 2150-11040 |

---

**End of Summary Document**
