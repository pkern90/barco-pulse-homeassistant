Pulse API: JSON RPC Reference

Platinum API JSON RPC Reference Page 3 of 171

Contents

```
Pulse API
Introduction
Connecting to Pulse services
Quick start guide
Object and method naming
Type support
Parameters
Authentication
Service API
Methods
Properties
Signals
Notifications
Introspection API
Read metadata method
Object changed signal
File endpoints
Programmers guide
Basic operation
Source input
Illumination
Picture settings
Warping with grid files
Blending with images
Black level adjustment with images
Environment information
ECO mode
Documentation by introspection
File endpoints
Properties
Methods
Signals
```

Page 4 of 171 JSON RPC Reference Platinum API

# 1 Pulse API

```
This document describes the application programmers interface to Pulse projectors.
How to connect to the projector, the communication protocol and a programmers guide is presented in the following section.
```

Platinum API JSON RPC Reference Page 5 of 171

# 2 Introduction

```
The facade API is based on the JSON-RPC 2.0 protocol and provides access to Pulse services to clients. The transport protocol for
external clients is TCP/IP. HTTP to be added in a future release.
```
## 2. 1 Connecting to Pulse services

2. 1. 1 Network

```
If the projector is on a network, TCP/IP can be used to connect to Pulse services.
The service is available on port number 9090
```
2. 1. 2 Serial port

```
A serial cable can be connected to the projector in order to access the Pulse services.
Connect the projector and host using a standard serial cable with 9-pin female to the host, and 9-pin male to the projector. Pin 2
connects to pin 2, pin 3 connects to pin 3 and pin 5 connects to pin 5.
```
RS232 Communication Parameters

```
Parameter Value
Baud rate 19200
Parity None
Data bits 8
Stop bits 1
Flow controlNone
```
## 2. 2 Quick start guide

```
The following sections are examples of frequently used commands, just to get you started. This assumes that the connection is set
up as described in the previous chapter. The type of connection is not important. The same commands are available for all
connection types.
```
2. 2. 1 Power on projector

2. 2. 2 Power off projector

2. 2. 3 Select DisplayPort 1 as input source

2. 2. 4 Select HDMI as input source

```
{"jsonrpc": "2.0", "method": "system.poweron"}
```
```
{"jsonrpc": "2.0", "method": "system.poweroff"}
```
```
{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "Disp
```
```
{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "HDMI
```

Page 6 of 171 JSON RPC Reference Platinum API

2. 3 Object and method naming

```
Objects and members are named using dot notation in lowercase format (Javascript-like notation). Members are either a method,
property, signal or object.
A typical method part of an invocation will then look like:
```
```
"method": "foo.echo"
```
```
If there are more than one object of a "kind", it may be modeled and notated like:
```
```
tempctrl.fans
tempctrl.fans.mainfan
tempctrl.fans.lampblower
```
```
In the example above it is possible to get all fans by introspect the "object" temptrl.fans
Example: accessing the "rpm" property of the "mainfan":
```
```
tempctrl.fans.mainfan.rpm
```
2. 4 Type support

```
basic types:
string (e.g. "hello"), 
integer (e.g. 114), 
float (e.g. 3.141592653589793)
boolean (e.g. true)
container types:
array (e.g. ["hello", "to","you"] )
object (e.g. {"name": "Johnny", "age": 30, "children": ["Agnes","Tim"] } )
dictionary with string key (e.g. gold medals Falun 2015: {"Norway": 11, "Germany": 5, "Sweden": 2} )
```
2. 5 Parameters

```
Passing parameters "by name" and "by position" are supported
```

Platinum API JSON RPC Reference Page 7 of 171

# 3 Authentication

```
A client session must start with an authentication request containing a secret pass code.
The purpose of the authentication protocol is to set the user Access Level. Authentication is only necessary when a higher level than
End User is required. For normal End User access the authentication can be skipped.
To authenticate with the server use the following request.
```
```
property type required comments
```
```
jsonrpc string yes "2.0"
```
```
method string yes "authenticate"
```
```
params object {"code": integer} yes 5 digits code for authenticating the users access level
```
```
id integer | string no request id
```
```
result bool if success true if result object
```
```
error object if error error object - see  JSON-RPC 2.
```
### {

```
"jsonrpc": "2.0",
"method":"authenticate",
"params": {"code": 98765},
"id": 1
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 1
}
```

Page 8 of 171 JSON RPC Reference Platinum API

# 4 Service API

```
property type required comments
```
```
jsonrpc string yes "2.0"
```
```
method string yes see below
```
```
params see below
```
```
id string |number no request id
```
```
error object if error error object - see  JSON-RPC 2.
```
## 4. 1 Methods

```
Method invocation API
```
## 4. 2 Properties

4. 2. 1 Write one

### {

```
"jsonrpc": "2.0",
"method":"ledctrl.blink",
"params": {"led": "systemstatus", "color": "red", "period": 42},
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"result": 0,
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"method":"property.set",
"params": {"property": "objectname.propertyname", "value": 100},
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 3
}
```

Platinum API JSON RPC Reference Page 9 of 171

```
It is best practice to wait for the confirmation of the property.set before setting the same property again. Continuously setting
the same property without waiting for confirmation may flood the server with unnecessary requests and may lower
performance.
```
4. 2. 2 Read one

4. 2. 3 Read multiple

4. 2. 4 Observe changes on one property

```
For change notifications, see Notifications
```
4. 2. 5 Observe changes on multiple properties

```
For change notifications, see Notifications
```
4. 2. 6 Stop observing one property

```
For change notifications, see Notifications
```
### {

```
"jsonrpc": "2.0",
"method":"property.get",
"params": {"property": "objectname.propertyname"},
"id": 4
}
```
### {

```
"jsonrpc": "2.0",
"result": 100,
"id": 4
}
```
### {

```
"jsonrpc": "2.0",
"method":"property.get",
"params": {"property": ["objectname.propertyname", "objectname.someproperty"]},
"id": 5
}
```
### {

```
"jsonrpc": "2.0",
"result": {"object.propertyname": 100, "objectname.someproperty": "foo"},
"id": 5
}
```
### {

```
"jsonrpc": "2.0",
"method":"property.subscribe",
"params": {"property": "objectname.propertyname"},
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"method":"property.subscribe",
"params": {
"property": [
"objectname.propertyname",
"objectname.otherproperty"
]
},
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 3
}
```

Page 10 of 171 JSON RPC Reference Platinum API

4. 2. 7 Stop observing multiple properties

4. 3 Signals

4. 3. 1 Subscribe to a single signal

```
For change notifications, see Notifications
```
4. 3. 2 Subscribe to multiple signals

```
For change notifications, see Notifications
```
4. 3. 3 Unsubscribe from a single signal

### {

```
"jsonrpc": "2.0",
"method":"property.unsubscribe",
"params": {"property": "objectname.propertyname"},
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"method":"property.unsubscribe",
"params": {
"property": [
"objectname.propertyname",
"objectname.otherproperty"
]
},
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"method":"signal.subscribe",
"params": {"signal": "objectname.signalname"},
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"method":"signal.subscribe",
"params": {
"signal": [
"objectname.signalname",
"otherobject.othersignal"
]
},
"id": 4
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 4
}
```
### {

```
"jsonrpc": "2.0",
"method":"signal.unsubscribe",
"params": {"signal": "objectname.signalname"},
"id": 5
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 5
}
```

Platinum API JSON RPC Reference Page 11 of 171

4. 3. 4 Unsubscribe from multiple signals

4. 4 Notifications

```
The client has to implement notification API to retrieve notifications. Notification messages will not have id and no response
message shall be returned.
```
4. 4. 1 Properties

```
The client must implement a property.changed function which receives an array of property/value pairs:
```
4. 4. 2 Signals

```
If the client subscribes to signals, it must implement the signal.callback function which receives an array of signal/argument-list
pairs:
```
### {

```
"jsonrpc": "2.0",
"method":"signal.unsubscribe",
"params": {
"signal": [
"objectname.signalname",
"otherobject.othersignal"
]
},
"id": 6
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 6
}
```
### {

```
"jsonrpc": "2.0",
"method":"property.changed",
"params": {
"property": [
{"objectname.propertyname": 100},
{"otherobject.otherproperty": "bar"}
]
}
}
```
### {

```
"jsonrpc": "2.0",
"method":"signal.callback",
"params": {
"signal": [
{"objectname.signalname": {"arg1": 100, "arg2": "cat"}},
{"otherobject.othersignal": {"foo": "bar"}}
]
}
}
```

Page 12 of 171 JSON RPC Reference Platinum API

# 5 Introspection API

## 5. 1 Read metadata method

```
Metadata of available objects (methods, properties, signals) can be read out. The data is restricted by the client's authenticated
access level. A typical usage for metadata is to set up OSD menus etc. The format of the metadata is described here: API
introspection data format
Introspection API (recursive=true)
```
```
Introspection API (recursive=false)
```
### {

```
"jsonrpc": "2.0",
"method": "introspect",
"params": {"object": "foo", "recursive": true},
"id": 1
}
```
### {

```
"jsonrpc": "2.0",
"method": "introspect",
"params": ["foo", true]
"id": 1
}
```
### {

```
"jsonrpc": "2.0",
"result": {"object": "foo", "methods": [ { "name": "echo", }, .... see API introspection data
"id": 1
}
```
### {

```
"jsonrpc": "2.0",
"method": "introspect",
"params": {"object": "motors", "recursive": false},
"id": 2
}
```
### {

```
"jsonrpc": "2.0",
"method": "introspect",
"params": ["motors", false]
"id": 2
}
```
### {

```
"jsonrpc": "2.0",
"result": {
"name": "motors",
"objects":[
{ "name": "motors.motor1" },
{"name":"motors.motor2" },
{"name":"motors.motor3"}
]
},
"id": 2
}
```

Platinum API JSON RPC Reference Page 13 of 171

```
property type required comments
```
```
jsonrpc string yes "2.0"
```
```
method string yes "introspect"
```
```
params object {"object":stringno (default="") "object": name of object to introspect (dot notation allowed) , default/empty will introspe
```
```
"recursive": bool} no (default=true)"recursive": if false then only object names are listed (one level). This is convenient if wan
```
```
id string |number no request id
```
```
result object yes The full format of the result is described here: API introspection data format
```
```
error object if error error object - see  JSON-RPC 2.
```
5. 2 Object changed signal

```
The introspect API provides a Signal to notify on new objects or objects lost. The name of the signal is: "modelupdated".  (See
section Signal how to subscribe and unsubscribe to signals.)
Subscribe to a signal
```
```
Callback method at client side:
```
```
argument type description
```
```
object string name of object
isnew bool true: object is new, false: object is lost
```
5. 1 File endpoints

### {

```
"jsonrpc": "2.0",
"method": "signal.subscribe",
"params": {"signal": "modelupdated"},
"id": 2
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 2
}
```
### {

```
"jsonrpc": "2.0",
"method": "signal.callback",
"params": {
"signal": [
{"introspect.objectchanged": {"object": "motors.motor1", "newobject": true }},
]
}
}
```

Page 14 of 171 JSON RPC Reference Platinum API

```
Some objects provide endpoints for uploading or downloading various data types. For example, a warp grid can be uploaded to the
warp engine.
The objects that provide end points are found in the documentation below under the File endpoints headings.
To download a file from the projector, you must enter its URL. The URL is constructed from the following parts:
http://
address of the projector, e.g 192.168.1.
/api
file endpoint, e.g /image/processing/warp/file/transfer
This will give you a URL that looks like this: http://192.168.1.100/api/image/processing/warp/file/transfer
Entering this URL in a browser will trigger a download from the projector and save the current warp grid to your download folder.
You can also use the curl program to do the same. E.g curl -O -J http://api/image/processing/warp/file/transfer
Note that not all endpoints supports downloading the current file. In those cases you need to specify which file to download. E.g
http://192.168.1.100/api/image/processing/warp/file/transfer/warpgrid.xml
To upload a file to the projector, use the curl program, or some other tool that supports HTTP upload.
To upload a warp grid to the projector from your local drive, enter the following command:
curl -F file=@warpgrid.xml http://192.168.1.100/api/image/processing/warp/file/transfer
You can also specify -X POST to the command, but in this case that's implied.
```

Platinum API JSON RPC Reference Page 15 of 171

# 6 Programmers guide

```
This section describes common tasks for controlling the projector. For example, selecting input source and adjusting image
properties.
```
## 6. 1 Basic operation

```
This chapter describes basic operation such as powering on/off the projector
```
6. 1. 1 Projector state

```
To get the current operation state from the projector, use the following command.
```
```
The resulting value will be one the following:
```
```
boot - projector is booting up
eco - projector is in ECO/power save mode
standby - projector is in standby mode
ready - projector is in ready mode
conditioning - projector is warming up
on - projector is on
deconditioning - projector is cooling down
```
```
To be notified when the state changes, a subscription must be requested, as shown in the following example.
```
```
When ever there is a change in the state, the server will notify the client as shown in the next example.
```
### {

```
"jsonrpc": "2.0",
"method": "property.get",
"id": 1,
"params": {
"property": "system.state"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 1,
"result": "on"
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.subscribe",
"id": 2,
"params": {
"property": [
"system.state"
]
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 2,
"result": true
}
```

Page 16 of 171 JSON RPC Reference Platinum API

6. 1. 2 Power on

```
To power on the projector, issue the following request.
```
```
Notice that the result is null. This is not an error, it's just that the method does not return a proper result. If there was an error, the
response would contain an error member that contains information about the error that occurred.
Also notice that this method does not need any arguments, so the params member does not need to be present. Nothing bad
happens if the params member is present. It will just be ignored.
If the projector already is on, or if it's in transition between states, nothing will happen.
Therefore, it's good practice to verify that the projector state is either standby or ready before issuing the power on command.
```
6. 1. 3 Power off

```
To power off the projector, issue the following request.
```
```
If the projector already is off, or if it's in transition between states, nothing will happen.
Therefore, it's good practice to verify that the projector state is on before issuing the power off command.
```
6. 2 Source input

```
The source input management is made up windows, sources and connectors. Each window have a source attached, and each source
is made up of one or more connectors.
```
6. 2. 1 Active source

### {

```
"jsonrpc": "2.0",
"method": "property.changed",
"params": {
"property": [
{ "system.state": "ready" }
]
}
}
```
### {

```
"jsonrpc": "2.0",
"method": "system.poweron",
"id": 3
}
```
### {

```
"jsonrpc": "2.0",
"id": 3,
"result": null
}
```
### {

```
"jsonrpc": "2.0",
"method": "system.poweroff",
"id": 4
}
```
### {

```
"jsonrpc": "2.0",
"id": 4,
"result": null
}
```

Platinum API JSON RPC Reference Page 17 of 171

```
To get the name of the currently active source, use the following request.
```
6. 2. 2 List available sources

```
To get a list of available sources, use the following request.
```
```
The response contains a list of all the available source names. The list contents will vary depending on the projector model.
```
6. 2. 3 Set the active source

```
To set the active source, first get the list of available sources as shown in the previous section. Then use the following request.
```
6. 2. 4 Connectors

```
The connectors are the physical input connectors of the projector. Available connectors depend on the projector model.
To list all the available connectors, use the following request.
```
### {

```
"jsonrpc": "2.0",
"method": "property.get",
"params": {
"property": "image.window.main.source"
},
"id": 0
}
```
### {

```
"jsonrpc": "2.0",
"result": "DisplayPort 1",
"id": 0
}
```
### {

```
"jsonrpc": "2.0",
"method": "image.source.list",
"id": 1
}
```
### {

```
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
### {

```
"jsonrpc": "2.0",
"method": "property.set",
"id": 2,
"params": {
"property": "image.window.main.source",
"value": "DisplayPort 1"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 2,
"result": true
}
```

Page 18 of 171 JSON RPC Reference Platinum API

```
To list the connectors used by a specific source, the source object name must be acquired. This can be done by translating the
source name, or by introspection.
The easiest way is to translate the source name. Given the source name of DisplayPort 1, remove all non word characters and
convert to all lower case characters. This can be done quite easy by using regular expressions. Example in JavaScript shown below.
```
```
const sourceName = 'DisplayPort 1';
const objectName = sourceName.replace(/\W/g, '').toLowerCase();
/* objectName is now 'displayport1' */
```
```
Now that we have the source object name, we can call the method that lists all the connectors used by this source.
```
```
The result of the method is an array of connector information. This information contains the connector name and the grid position of
the connector, which is useful when multiple connectors are used.
```
Source signal

```
To get signal information from an input connector, the input object name must be acquired using the same technique as with source
objects.
Given a connector name of DisplayPort 1, this translates to a connector name of displayport1. We can then get signal
information by using the following request.
```
### {

```
"jsonrpc": "2.0",
"method": "image.connector.list",
"id": 1
}
```
### {

```
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
### {

```
"jsonrpc": "2.0",
"method": "image.source.displayport1.listconnectors",
"id": 2
}
```
### {

```
"jsonrpc": "2.0",
"id": 2,
"result": [
{
"gridposition": {
"row": 0,
"column": 0,
"plane": 0
},
"name": "DisplayPort 1"
}
]
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.get",
"id": 3,
"params": {
"property": "image.connector.displayport1.detectedsignal"
}
}
```

Platinum API JSON RPC Reference Page 19 of 171

6. 2. 5 Source and signal updates

```
To get updates when a new source is selected, or the signal on a connector change, you must listen for changes on a number of
properties.
```
Subscribe to the source property of the window

```
This will generate a property change notification when ever there is a change in the active source. E.g when the user switches from
DisplayPort 1 to DisplayPort 2.
The JSON RPC client must therefore implement the property change listener in order to process the notification.
The JSON RPC server will send notifications as shown below.
```
### {

```
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
### {

```
"jsonrpc": "2.0",
"method": "property.subscribe",
"params": { "property: "image.window.main.source" },
"id": 5
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 5
}
```

Page 20 of 171 JSON RPC Reference Platinum API

```
Note that two notifications are delivered in this case. First, when the previously selected source is deselected. Next, when the new
source is selected.
```
6. 2. 6 Connector signal updates

```
To get updates when there is a change in the signal on sources connectors, each connector of the source must have a listener for the
signal detection property of the connector.
The recommended way to do this is to reflect the source and connector structure of the server in the client application.
That means:
Store all the source names and source object names
Call image.source.list
Translate the source names into source object names as shown in the beginning of the chapter
For each source object
Call image.source.[name].listconnectors
Translate the connector names to connector object names
Maintain a list of connectors per source
For each connector object
Subscribe to image.connector.[name].detectedsignal
When the notifications are received, match up the connector names with the connectors used by the active source and show the new
information to the user.
Keep in mind that notifications are only sent when there is an actual change in a value. Simply subscribing to a property does not get
the current value. To get the current value use the property.get method and specify which property you are interested in.
```
6. 3 Illumination

```
This section describes how to set the lamp/LED/laser power of the projector.
```
6. 3. 1 State

```
To read the state of the illumination use the following commands.
```
### {

```
"jsonrpc": "2.0",
"method": "property.changed",
"params": {
"property": [
{
"image.window.main.source": ""
}
]
}
}
{
"jsonrpc": "2.0",
"method": "property.changed",
"params": {
"property": [
{
"image.window.main.source": "DisplayPort 2"
}
]
}
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.get",
"params": {
"property": "illumination.state"
},
"id": 0
}
```
### {

```
"jsonrpc": "2.0",
"id": 0,
"result": "Off"
}
```

Platinum API JSON RPC Reference Page 21 of 171

```
The result will be either On or Off. To receive notifications when the state changes, you need to subscribe. The following commands
will request change notifications for the illumination state.
```
```
The client needs to implement the property change listener to receive notifications.
When a change happens, the server will send the following notification to the client.
```
6. 3. 2 Sources

```
Different projectors will have different types of illumination sources. Some will have lasers, others will have LEDs, or a combination of
both, and yet others may have xenon or UHP lamps.
To query the available sources, you must do an introspection of the illumination object. The following command shows an
example of that.
```
```
The server will respond with the following result.
```
### {

```
"jsonrpc": "2.0",
"method": "property.subscribe",
"id": 1,
"params": {
"property": [
"illumination.state"
]
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 1,
"result": true
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.changed",
"params": {
"property": [
{
"illumination.state": "On"
}
]
}
}
```
### {

```
"jsonrpc": "2.0",
"method": "introspect",
"id": 0,
"params": {
"object": "illumination.sources",
"recursive": false
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 0,
"result": {
"name": "illumination.sources",
"objects": [
{
"name": "illumination.sources.laser"
}
]
}
}
```

Page 22 of 171 JSON RPC Reference Platinum API

```
From the response, we can see that this projector has a laser illumination source. Each source has properties that give you
information about the minimum, maximum and the current illumination power level.
The current power level can be read or written, the minimum and maxium power level are read only, but they are dynamic values and
may change depending on the setting of the projector. The lens type and lens position may also affect the power levels.
The read the current power level, use the following commands.
```
```
To be notified of changes in the power level, you must subscribe to property changes.
```
```
To set the value of the laser power, use the following command.
```
```
After the confirmation of the value, a change notification is also sent.
```
### {

```
"jsonrpc": "2.0",
"method": "property.get",
"id": 1,
"params": {
"property": "illumination.sources.laser.power"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 1,
"result": 30
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.subscribe",
"id": 2,
"params": {
"property": [
"illumination.sources.laser.power"
]
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 2,
"result": true
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.set",
"id": 3,
"params": {
"property": "illumination.sources.laser.power",
"value": 40
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 3,
"result": true
}
```

Platinum API JSON RPC Reference Page 23 of 171

```
To get the minimum and maximum power levels, use the following commands.
```
6. 4 Picture settings

```
The image service has properties for controlling the image appearance. Like brightness, contrast, saturation and gamma.
This section describes how to set basic picture settings.
```
6. 4. 1 Brightness

```
Before setting any values it is a good idea to get some information about the properties. This is done with introspection.
Individual properties can not be introspected, so we must ask the owner of the property. In this case it is the image service.
To perform introspection of the image service, issue the following request.
```
### {

```
"jsonrpc": "2.0",
"method": "property.changed",
"params": {
"property": [
{
"illumination.sources.laser.power": 40
}
]
}
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.get",
"id": 4,
"params": {
"property": "illumination.sources.laser.maxpower"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 4,
"result": 100
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.get",
"id": 5,
"params": {
"property": "illumination.sources.laser.minpower"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 5,
"result": 0
}
```

Page 24 of 171 JSON RPC Reference Platinum API

```
The server will respond with something similar to this:
```
```
The result contains information about all the properties, objects and signals belonging to the image service.
Here we are only interested in the brightness property, so the rest of the response has been trimmed.
We can see that the brightness property has a type which is float. It also has some constraints that define the minimum and
maxium values for the property. This information can be used to prevent sending out of range values to the server, and also give hints
to the user when e.g using a slider to control the brightness value.
The type also has a step-size. This is a hint that can be used when incrementing or decrementing the value in a GUI application.
The step-size is used as a factor to the precision. E.g for the brightness we have a precision of 0.01 and a step-size of 1. The
means that when ever the user wants to increment the value, we can add (step-size x precision) to the current value.
To get the current brightness value, use the following request.
```
```
To receive notification when the brightness value change, use the following subscription.
```
### {

```
"jsonrpc": "2.0",
"method": "introspect",
"params": {
"object": "image",
"recursive": false
},
"id": 0
}
```
### {

```
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
},
{
....trimmed for brevity
}
],
"objects": [
... trimmed for brevity
]
}
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.get",
"id": 2,
"params": {
"property": "image.brightness"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 2,
"result": 0
}
```

Platinum API JSON RPC Reference Page 25 of 171

```
To set the brightness value, use the following request.
```
```
In addition to the confirmation from the property.set method, a notifaction is also sent.
```
```
The set the other picture settings follow the same procedure as for brightness.
```
6. 5 Warping with grid files

```
To globally enable warp, use the following command.
```
### {

```
"jsonrpc": "2.0",
"method": "property.subscribe",
"id": 3,
"params": {
"property": [
"image.brightness"
]
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 3,
"result": true
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.set",
"params": {
"property": "image.brightness",
"value": 0.15
},
"id": 4
}
```
### {

```
"jsonrpc": "2.0",
"id": 4,
"result": true
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.changed",
"params": {
"property": [
{
"image.brightness": 0.15
}
]
}
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.set",
"id": 1,
"params": {
"property": "image.processing.warp.enable",
"value": true
}
}
```

Page 26 of 171 JSON RPC Reference Platinum API

6. 5. 1 Upload warp file

```
Send the warp grid file through HTTP POST. The following example is using curl to upload a file to the projector at address
192.168.1.100.
```
```
curl -X POST -F file=@warp.xml http://192.168.1.100/api/image/processing/warp/file/transfer
```
```
Note that -X POST can be omitted since this is implied when using -F.
To select/activate the uploaded file, use the following command.
```
```
Finally, the grid file warping must be enabled. To do this, use the following command.
```
6. 5. 2 Warp file format

```
The warp file format is the same as on the MCM500/400.
An example file can be downloaded here.
In the example file, the range attributes have been added by specifying the <X-FlatParameters> and <Y-FlatParameters> tags.
There are 33x33 (=1089) floating point values for each of these two tags, X and Y values respectively. The values themselves are how
much offset each point in the grid will have from its non-warped position, meaning that a file with no warp will contain only zeros. The
value are in book-read order. The range attribute indicates the range or scaling factor of the offset values. For instance, if you set the
X range to 2560, an offset of 2560 will move the grid point all the way from its original position and one full width of the screen to the
right. If you want to use normalized values, set range to 1 and an offset of 1.0 will accomplish the same thing. The other tags in the
file, <TDRmode>, <TDRvalue> and <Sharpness> are not used by Pulse for now. They’re in there for MCM compatibility.
```
6. 6 Blending with images

```
In a multi channel setup, blending is required in order to get a seamless transition between the channels.
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 1
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.set",
"id": 2,
"params": {
"property": "image.processing.warp.file.selected",
"value": "warp.xml"
}
}
```
### {

```
"jsonrpc": "2.0",
"result": true,
"id": 2
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.set",
"id": 2,
"params": {
"property": "image.processing.warp.file.enable",
"value": true
}
}
```

Platinum API JSON RPC Reference Page 27 of 171

```
For this, blend edges can be configured, or one can use pre generated blend masks that are uploaded to the projector.
```
6. 6. 1 Uploading a blend mask

```
Blend masks are grayscale images in either 8 bit or 16 bit pixel resolution. The size of the blend mask must match the resolution of
the blend layer of the projector. For this model, the resolution must be 0 x 0
To upload a blend mask, use the following shell command.
```
```
curl -X POST -F file=@mask.png http://192.168.1.100/api/image/processing/blend/file/transfer
```
```
In the example above we have a blend mask in the PNG format called mask.png and the projector has the IP address of
192.168.1.100.
To select the blend file that was just uploaded, use the following request.
```
```
To enable the blend mask use the following request.
```
6. 6. 2 Supported image formats

```
The supported image formats are:
PNG - up to 16 bit
JPEG
TIFF
The interface only technically supports grayscale, but will accept colour images. It will then only use the blue channel. This is to
support grayscale images saved as RGB images, we don't support using the full colour information.
```
6. 7 Black level adjustment with images

### {

```
"jsonrpc": "2.0",
"method": "property.set",
"id": 1,
"params": {
"property": "image.processing.blend.file.selected",
"value": "mask.png"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 1,
"result": true
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.set",
"id": 2,
"params": {
"property": "image.processing.blend.mode",
"value": "FILE"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 2,
"result": true
}
```

Page 28 of 171 JSON RPC Reference Platinum API

```
In a multi channel setup, blending is required in order to get a seamless transition between the channels. To compensate for the extra
light in the blended regions, the black level can be increased in the non-blended regions to get a uniform black level across all
channels. Black levels can be configured by using the basic controls to specify linear edges, or one can use pre generated images
that are uploaded to the projector.
```
6. 7. 1 Uploading a black level mask

```
Black level masks are grayscale images in either 8 bit or 16 bit pixel resolution. The size of the black level mask must match the
resolution of the black level layer of the projector. For this model, the resolution must be 0 x 0
To upload a black level mask, use the following shell command.
```
```
curl -X POST -F file=@blacklevel.png http://192.168.1.100/api/image/processing/blacklevel/file/transfer
```
```
In the example above we have a black level mask in the PNG format called blacklevel.png and the projector has the IP address of
192.168.1.100.
To select the black level file that was just uploaded, use the following request.
```
```
To enable the black level mask use the following request.
```
6. 7. 2 Supported image formats

```
The supported image formats are:
PNG - up to 16 bit
JPEG
TIFF
The interface only technically supports grayscale, but will accept colour images. It will then only use the blue channel. This is to
support grayscale images saved as RGB images, we don't support using the full colour information.
```
### {

```
"jsonrpc": "2.0",
"method": "property.set",
"id": 1,
"params": {
"property": "image.processing.blacklevel.file.selected",
"value": "blacklevel.png"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 1,
"result": true
}
```
### {

```
"jsonrpc": "2.0",
"method": "property.set",
"id": 2,
"params": {
"property": "image.processing.blacklevel.mode",
"value": "FILE"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 2,
"result": true
}
```

Platinum API JSON RPC Reference Page 29 of 171

6. 8 Environment information

```
The environment service manages a lot of information in order to keep running the projector at the optimal operating conditions.
Among the information available are fan speeds, temperatures and voltages. This section describes an easy method to get
information from the environment service.
```
6. 8. 1 Temperatures

```
To get a snapshot or current reading of all the available temperature sensors, use the following request.
```
```
The result is in the form of a dictionary, where the key is the name of the sensor and the value is the temperature reading.
```
6. 8. 2 Fan speeds

```
To get fan speeds, use the following request.
```
### {

```
"jsonrpc": "2.0",
"method": "environment.getcontrolblocks",
"id": 1,
"params": {
"type": "Sensor",
"valuetype": "Temperature"
}
}
```
### {

```
"jsonrpc": "2.0",
"id": 1,
"result": {
"environment.laser.board0.bank0.temperature": 35.3,
"environment.laser.board0.bank1.temperature": 34.8,
"environment.laser.board0.bank2.temperature": 35.3,
"environment.laser.board0.bank3.temperature": 35.1,
"environment.laser.board0.bank4.temperature": 34.7,
"environment.laser.board0.bank5.temperature": 34.9,
"environment.laser.board0.heatsink0.temperature": 35,
"environment.laser.board0.heatsink1.temperature": 37.6,
"environment.laser.board0.heatsink2.temperature": 40.4,
"environment.laser.board0.heatsink3.temperature": 41.5,
"environment.laser.board0.heatsink4.temperature": 46.4,
"environment.laser.board0.heatsink5.temperature": 41.3,
"environment.laser.board1.bank0.temperature": 36.6,
"environment.laser.board1.bank1.temperature": 36.2,
"environment.laser.board1.bank2.temperature": 36.4,
"environment.laser.board1.bank3.temperature": 36.4,
"environment.laser.board1.bank4.temperature": 36,
"environment.laser.board1.bank5.temperature": 35.9,
"environment.laser.board1.heatsink0.temperature": 34.7,
"environment.laser.board1.heatsink1.temperature": 34.9,
"environment.laser.board1.heatsink2.temperature": 36.5,
"environment.laser.board1.heatsink3.temperature": 36.5,
"environment.laser.board1.heatsink4.temperature": 39.4,
"environment.laser.board1.heatsink5.temperature": 40.3,
"environment.temperature.cyclon5": 47.6,
"environment.temperature.imx6": 40.1,
"environment.temperature.inlet": 25.5,
"environment.temperature.mainboard": 40.4,
"environment.temperature.mainpower": 37.6,
"environment.temperature.outlet": 29.4,
"environment.temperature.scalerfpga": 52.8
}
}
```
### {

```
"jsonrpc": "2.0",
"method": "environment.getcontrolblocks",
"id": 2,
"params": {
"type": "Sensor",
"valuetype": "Speed"
}
}
```

Page 30 of 171 JSON RPC Reference Platinum API

```
The result is in the form of a dictionary, where the key is the name of the sensor, a fan in this case, and the value is the fan speed
reading.
```
6. 8. 3 Other environment info

```
Other environment info is also available and follows the same patterns as for temperatures and fan speeds. Use the
environment.getcontrolblocks method with different sensor types and different sensor value types to get the desired data.
The applicable sensor types are:
Sensor
Filter
Controller
Actuator
Alarm
GenericBlock
The applicable sensor value types are:
```
```
Temperature
Speed
PWM
Voltage
Current
Power
Altitude
Pressure
Humidity
```
### ADC

```
Coordinate
Peltier
Waveform
Average
Delay
Difference
Interpolation
Limit
```
```
Median
Noise
Weighting
Comparison
Threshold
Formula
Driver
PID
Mode
```
```
Simulation
State
Pump
Resistance
Constant
Manual
Range
Any
```
6. 9 ECO mode

```
On projectors that have ECO mode, special handling is required to wake up the projector.
To wake up a projector that is in ECO mode:
```
1. Send a wake on LAN request supplying the projectors HW (MAC) address
2. Use the power button on the remote control
3. Use the power button on the keypad
4. Send a special command on the RS232 serial port
In the last case, waking up using the serial port, send the following ASCII characters:

```
:POWR1\r
```
### {

```
"jsonrpc": "2.0",
"id": 2,
"result": {
"environment.fan.ar1.tacho": 1800,
"environment.fan.ar2.tacho": 1850,
"environment.fan.ar3.tacho": 1750,
"environment.fan.ar4.tacho": 1800,
"environment.fan.ar5.tacho": 1800,
"environment.fan.driver.tacho": 2300,
"environment.fan.optics.tacho": 2600,
"environment.fan.pcb.tacho": 1400,
"environment.fan.phosphorleft.tacho": 3850,
"environment.fan.phosphorright.tacho": 3800,
"environment.fan.psu.tacho": 1450
}
}
```

Platinum API JSON RPC Reference Page 31 of 171


Page 32 of 171 JSON RPC Reference Platinum API

# 7 Documentation by introspection

## 7. 1 File endpoints

```
Alphabetical list of all file endpoints.
A file endpoint is a service that provides upload and/or download of a certain file type.
The upload or download is performed using HTTP.
Legend:
```
```
 File upload is supported
 File download is supported
```
7. 1. 1 bio.logger.transfer 

```
Download notification log files
Example of file download using the curl program on Linux and Mac OS X. Using the -O and -J option makes curl use the
file name suggestion of the server and will overwrite a file if it exists.
```
```
pulse:~$ curl -O -J http://192.168.1.100/api/bio/logger/transfer
```
```
Example of file download using PowerShell on Windows.
```
```
PS C:\Users\pulse> Invoke-WebRequest -Uri http://192.168.1.100/api/bio/logger/transfer -Method Get -OutFil
```
7. 1. 2 notification.logger.transfer 

```
Download notification log files
Example of file download using the curl program on Linux and Mac OS X. Using the -O and -J option makes curl use the
file name suggestion of the server and will overwrite a file if it exists.
```
```
pulse:~$ curl -O -J http://192.168.1.100/api/notification/logger/transfer
```
```
Example of file download using PowerShell on Windows.
```
```
PS C:\Users\pulse> Invoke-WebRequest -Uri http://192.168.1.100/api/notification/logger/transfer -Method Ge
```
7. 1. 3 system.license.file.registration 

```
Download registration file
Example of file download using the curl program on Linux and Mac OS X. Using the -O and -J option makes curl use the
file name suggestion of the server and will overwrite a file if it exists.
```
```
pulse:~$ curl -O -J http://192.168.1.100/api/system/license/file/registration
```
```
Example of file download using PowerShell on Windows.
```
```
PS C:\Users\pulse> Invoke-WebRequest -Uri http://192.168.1.100/api/system/license/file/registration -Metho
```

Platinum API JSON RPC Reference Page 33 of 171

7. 1. 4 ui.capture.lcd 

```
Download screen capture of LCD
Example of file download using the curl program on Linux and Mac OS X. Using the -O and -J option makes curl use the
file name suggestion of the server and will overwrite a file if it exists.
```
```
pulse:~$ curl -O -J http://192.168.1.100/api/ui/capture/lcd
```
```
Example of file download using PowerShell on Windows.
```
```
PS C:\Users\pulse> Invoke-WebRequest -Uri http://192.168.1.100/api/ui/capture/lcd -Method Get -OutFile lcd
```
7. 1. 5 ui.capture.osd 

```
Download screen capture of OSD
Example of file download using the curl program on Linux and Mac OS X. Using the -O and -J option makes curl use the
file name suggestion of the server and will overwrite a file if it exists.
```
```
pulse:~$ curl -O -J http://192.168.1.100/api/ui/capture/osd
```
```
Example of file download using PowerShell on Windows.
```
```
PS C:\Users\pulse> Invoke-WebRequest -Uri http://192.168.1.100/api/ui/capture/osd -Method Get -OutFile osd
```
7. 1. 6 ui.splashscreen.file 

```
Upload splash screen for LCD - 800x480 PNG,JPG
Example of file upload using the curl program.
```
```
pulse:~$ curl -F file=@splashscreen.dat http://192.168.1.100/api/ui/splashscreen/file
```
7. 1 Properties

```
Alphabetical list of all properties.
All properties listed here can be read, but not all properties can be written. A property that is read only, is indicated with this icon: 
```
7. 0. 1 dmx.artnet

```
Artnet enabled or not
Type: bool
```
7. 0. 2 dmx.artnetnet

```
Artnet net selection
Type: int
```
```
Min: 0
```

Page 34 of 171 JSON RPC Reference Platinum API

```
Max: 255
```
```
Precision: 1
```
```
Step size: 1
```
7. 0. 3 dmx.artnetuniverse

```
Artnet universe selection
Type: int
```
```
Min: 0
```
```
Max: 255
```
```
Precision: 1
```
```
Step size: 1
```
7. 0. 4 dmx.mode

```
Current mode
Type: string
```
7. 0. 5 dmx.monitor.channel01.function 

```
Description for the dmx channel
Type: string
```
7. 0. 6 dmx.monitor.channel01.offset 

```
Offset of the channel.
Type: int
```
7. 0. 7 dmx.monitor.channel01.value 

```
Current dmx value for the channel
Type: int
```
7. 0. 8 dmx.monitor.channel02.function 

```
Description for the dmx channel
Type: string
```
7. 0. 9 dmx.monitor.channel02.offset 

```
Offset of the channel.
Type: int
```

Platinum API JSON RPC Reference Page 35 of 171

7. 0. 10 dmx.monitor.channel02.value 

```
Current dmx value for the channel
Type: int
```
7. 0. 11 dmx.monitor.connectionstate.active 

```
true indicates that a dmx (if artnet setting is deactivated) or artnet package (if artnet setting is active) was received in the last
10 seconds.
Type: bool
```
7. 0. 12 dmx.shutdown

```
Shutdown enabled or not
Type: bool
```
7. 0. 13 dmx.shutdowntimeout

```
Time out for shutdown in minutes.
Type: int
```
```
Min: 1
```
```
Max: 60
```
```
Precision: 1
```
```
Step size: 1
```
7. 0. 14 dmx.startchannel

```
The dmx start channel [1..512].
Type: int
```
```
Min: 1
```
```
Max: 512
```
```
Precision: 1
```
```
Step size: 1
```
7. 0. 15 environment.alarmstate 

```
Deprecated, replaced by 'system.health'
Type: enum
```
```
Error
Alert
Warning
Ok
```

Page 36 of 171 JSON RPC Reference Platinum API

7. 0. 16 environment.fanspeed.mainboard.fan1.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 17 environment.fanspeed.mainboard.fan1.threshold.health 

```
The sensor health - indicates if the sensor is operating within normal operating conditions.
Type: enum
```
```
Normal
Warning
Error
```
7. 0. 18 environment.fanspeed.mainboard.fan1.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 19 environment.fanspeed.mainboard.fan1.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 20 environment.fanspeed.mainboard.fan1.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
```

Platinum API JSON RPC Reference Page 37 of 171

```
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 21 environment.image-tilt.pitch.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 22 environment.image-tilt.pitch.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
```

Page 38 of 171 JSON RPC Reference Platinum API

```
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 23 environment.image-tilt.pitch.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 24 environment.image-tilt.pitch.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
```

Platinum API JSON RPC Reference Page 39 of 171

```
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 25 environment.image-tilt.roll.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 26 environment.image-tilt.roll.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 27 environment.image-tilt.roll.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 28 environment.image-tilt.roll.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
```

Page 40 of 171 JSON RPC Reference Platinum API

```
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 29 environment.imageorientation.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 30 environment.imageorientation.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
```

Platinum API JSON RPC Reference Page 41 of 171

```
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 31 environment.imageorientation.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 32 environment.imageorientation.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
```

Page 42 of 171 JSON RPC Reference Platinum API

```
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 33 environment.mainboard.fan1.pid.processvariable.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 34 environment.mainboard.fan1.pid.processvariable.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 35 environment.mainboard.fan1.pid.processvariable.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 36 environment.mainboard.fan1.pid.processvariable.valuetype 

```
value type e.g. Temperature
```

Platinum API JSON RPC Reference Page 43 of 171

```
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 37 environment.mainboard.fan1.setpoint.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 38 environment.mainboard.fan1.setpoint.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```

Page 44 of 171 JSON RPC Reference Platinum API

```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 39 environment.mainboard.fan1.setpoint.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 40 environment.mainboard.fan1.setpoint.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
```

Platinum API JSON RPC Reference Page 45 of 171

```
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 41 environment.mainboard.fan2.pid.processvariable.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 42 environment.mainboard.fan2.pid.processvariable.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 43 environment.mainboard.fan2.pid.processvariable.value 

```
Description is missing!!!
```
```
Type: float
```

Page 46 of 171 JSON RPC Reference Platinum API

7. 0. 44 environment.mainboard.fan2.pid.processvariable.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 45 environment.mainboard.fan2.setpoint.name 

```
user friendly name for this 'block'
Type: string
```

Platinum API JSON RPC Reference Page 47 of 171

7. 0. 46 environment.mainboard.fan2.setpoint.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 47 environment.mainboard.fan2.setpoint.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 48 environment.mainboard.fan2.setpoint.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
```

Page 48 of 171 JSON RPC Reference Platinum API

```
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 49 environment.pwm.mainboard.fan1.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 50 environment.pwm.mainboard.fan1.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 51 environment.pwm.mainboard.fan1.value 


Platinum API JSON RPC Reference Page 49 of 171

```
Description is missing!!!
```
```
Type: float
```
7. 0. 52 environment.pwm.mainboard.fan1.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 53 environment.pwm.mainboard.fan2.name 


Page 50 of 171 JSON RPC Reference Platinum API

```
user friendly name for this 'block'
Type: string
```
7. 0. 54 environment.pwm.mainboard.fan2.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 55 environment.pwm.mainboard.fan2.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 56 environment.pwm.mainboard.fan2.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
```

Platinum API JSON RPC Reference Page 51 of 171

```
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 57 environment.state.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 58 environment.state.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```

Page 52 of 171 JSON RPC Reference Platinum API

7. 0. 59 environment.state.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 60 environment.state.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```

Platinum API JSON RPC Reference Page 53 of 171

7. 0. 61 environment.temperature.mainboard.cpu.health 

```
The sensor health - indicates if the sensor is operating within normal operating conditions.
Type: enum
```
```
Normal
Warning
Error
```
7. 0. 62 environment.temperature.mainboard.cpu.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 63 environment.temperature.mainboard.cpu.threshold.higherror 

```
high threshold value generating an error
Type: float
```
7. 0. 64 environment.temperature.mainboard.cpu.threshold.highwarning 

```
high threshold value generating a warning
Type: float
```
7. 0. 65 environment.temperature.mainboard.cpu.threshold.lowerror 

```
low threshold value generating an error
Type: float
```
7. 0. 66 environment.temperature.mainboard.cpu.threshold.lowwarning 

```
low threshold value generating a warning
Type: float
```
7. 0. 67 environment.temperature.mainboard.cpu.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
```

Page 54 of 171 JSON RPC Reference Platinum API

```
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 68 environment.temperature.mainboard.cpu.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 69 environment.temperature.mainboard.cpu.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
```

Platinum API JSON RPC Reference Page 55 of 171

```
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 70 environment.tilt.pitch.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 71 environment.tilt.pitch.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 72 environment.tilt.pitch.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 73 environment.tilt.pitch.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
```

Page 56 of 171 JSON RPC Reference Platinum API

```
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 74 environment.tilt.roll.name 

```
user friendly name for this 'block'
Type: string
```
7. 0. 75 environment.tilt.roll.unit 

```
unit depends on the value type e.g. temperature will have degC as unit
Type: enum
```
```
NotApplicable
RPM
ampere
milliampere
bar
decibel
```

Platinum API JSON RPC Reference Page 57 of 171

```
degArc
degC
hectopascal
kilogram
lumens
meter
ohm
percentage
seconds
volt
watt
```
7. 0. 76 environment.tilt.roll.value 

```
Description is missing!!!
```
```
Type: float
```
7. 0. 77 environment.tilt.roll.valuetype 

```
value type e.g. Temperature
Type: enum
```
```
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
```

Page 58 of 171 JSON RPC Reference Platinum API

```
Simulation
Speed
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
7. 0. 78 firmware.component.color-sensor-lpc5504jhi48-boot.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 79 firmware.component.color-sensor-lpc5504jhi48-boot.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 80 firmware.component.color-sensor-lpc5504jhi48-boot.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 81 firmware.component.color-sensor-lpc5504jhi48-boot.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 82 firmware.component.color-sensor-lpc5504jhi48-boot.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 83 firmware.component.color-sensor-lpc5504jhi48-boot.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 84 firmware.component.color-sensor-lpc5504jhi48-boot.status 

```
The status of the current firmware upgrade
Type: enum
```

Platinum API JSON RPC Reference Page 59 of 171

```
Inactive
Active
Error
Finished
```
7. 0. 85 firmware.component.color-sensor-lpc5504jhi48-run.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 86 firmware.component.color-sensor-lpc5504jhi48-run.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 87 firmware.component.color-sensor-lpc5504jhi48-run.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 88 firmware.component.color-sensor-lpc5504jhi48-run.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 89 firmware.component.color-sensor-lpc5504jhi48-run.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 90 firmware.component.color-sensor-lpc5504jhi48-run.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 91 firmware.component.color-sensor-lpc5504jhi48-run.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```

Page 60 of 171 JSON RPC Reference Platinum API

7. 0. 92 firmware.component.cornet-fpga.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 93 firmware.component.cornet-fpga.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 94 firmware.component.cornet-fpga.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 95 firmware.component.cornet-fpga.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 96 firmware.component.cornet-fpga.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 97 firmware.component.cornet-fpga.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 98 firmware.component.cornet-fpga.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 99 firmware.component.formatter-blue-wqxga.actualversion 

```
The version of the currently installed firmware.
Type: string
```

Platinum API JSON RPC Reference Page 61 of 171

7. 0. 100 firmware.component.formatter-blue-wqxga.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 101 firmware.component.formatter-blue-wqxga.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 102 firmware.component.formatter-blue-wqxga.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 103 firmware.component.formatter-blue-wqxga.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 104 firmware.component.formatter-blue-wqxga.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 105 firmware.component.formatter-blue-wqxga.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 106 firmware.component.formatter-green-wqxga.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 107 firmware.component.formatter-green-wqxga.displayname 

```
The user-friendly name of the firmware component.
Type: string
```

Page 62 of 171 JSON RPC Reference Platinum API

7. 0. 108 firmware.component.formatter-green-wqxga.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 109 firmware.component.formatter-green-wqxga.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 110 firmware.component.formatter-green-wqxga.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 111 firmware.component.formatter-green-wqxga.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 112 firmware.component.formatter-green-wqxga.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 113 firmware.component.formatter-red-wqxga.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 114 firmware.component.formatter-red-wqxga.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 115 firmware.component.formatter-red-wqxga.error 

```
The error message in case of an upgrade error.
Type: string
```

Platinum API JSON RPC Reference Page 63 of 171

7. 0. 116 firmware.component.formatter-red-wqxga.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 117 firmware.component.formatter-red-wqxga.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 118 firmware.component.formatter-red-wqxga.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 119 firmware.component.formatter-red-wqxga.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 120 firmware.component.intel-i210.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 121 firmware.component.intel-i210.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 122 firmware.component.intel-i210.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 123 firmware.component.intel-i210.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```

Page 64 of 171 JSON RPC Reference Platinum API

7. 0. 124 firmware.component.intel-i210.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 125 firmware.component.intel-i210.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 126 firmware.component.intel-i210.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 127 firmware.component.l1-vh-input-fpga.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 128 firmware.component.l1-vh-input-fpga.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 129 firmware.component.l1-vh-input-fpga.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 130 firmware.component.l1-vh-input-fpga.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 131 firmware.component.l1-vh-input-fpga.progress 

```
The progress of the current firmware upgrade
Type: int
```

Platinum API JSON RPC Reference Page 65 of 171

7. 0. 132 firmware.component.l1-vh-input-fpga.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 133 firmware.component.l1-vh-input-fpga.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 134 firmware.component.l1-vh-input-hd-base-t-a.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 135 firmware.component.l1-vh-input-hd-base-t-a.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 136 firmware.component.l1-vh-input-hd-base-t-a.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 137 firmware.component.l1-vh-input-hd-base-t-a.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 138 firmware.component.l1-vh-input-hd-base-t-a.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 139 firmware.component.l1-vh-input-hd-base-t-a.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```

Page 66 of 171 JSON RPC Reference Platinum API

7. 0. 140 firmware.component.l1-vh-input-hd-base-t-a.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 141 firmware.component.l1-vh-input-hd-base-t-b.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 142 firmware.component.l1-vh-input-hd-base-t-b.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 143 firmware.component.l1-vh-input-hd-base-t-b.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 144 firmware.component.l1-vh-input-hd-base-t-b.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 145 firmware.component.l1-vh-input-hd-base-t-b.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 146 firmware.component.l1-vh-input-hd-base-t-b.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 147 firmware.component.l1-vh-input-hd-base-t-b.status 

```
The status of the current firmware upgrade
Type: enum
```

Platinum API JSON RPC Reference Page 67 of 171

```
Inactive
Active
Error
Finished
```
7. 0. 148 firmware.component.l1-vh-input-power-sequencer.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 149 firmware.component.l1-vh-input-power-sequencer.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 150 firmware.component.l1-vh-input-power-sequencer.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 151 firmware.component.l1-vh-input-power-sequencer.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 152 firmware.component.l1-vh-input-power-sequencer.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 153 firmware.component.l1-vh-input-power-sequencer.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 154 firmware.component.l1-vh-input-power-sequencer.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```

Page 68 of 171 JSON RPC Reference Platinum API

7. 0. 155 firmware.component.laser-control-board-fpga.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 156 firmware.component.laser-control-board-fpga.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 157 firmware.component.laser-control-board-fpga.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 158 firmware.component.laser-control-board-fpga.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 159 firmware.component.laser-control-board-fpga.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 160 firmware.component.laser-control-board-fpga.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 161 firmware.component.laser-control-board-fpga.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 162 firmware.component.laser-control-board-lpc55-boot.actualversion 

```
The version of the currently installed firmware.
Type: string
```

Platinum API JSON RPC Reference Page 69 of 171

7. 0. 163 firmware.component.laser-control-board-lpc55-boot.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 164 firmware.component.laser-control-board-lpc55-boot.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 165 firmware.component.laser-control-board-lpc55-boot.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 166 firmware.component.laser-control-board-lpc55-boot.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 167 firmware.component.laser-control-board-lpc55-boot.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 168 firmware.component.laser-control-board-lpc55-boot.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 169 firmware.component.laser-control-board-lpc55-run.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 170 firmware.component.laser-control-board-lpc55-run.displayname 

```
The user-friendly name of the firmware component.
Type: string
```

Page 70 of 171 JSON RPC Reference Platinum API

7. 0. 171 firmware.component.laser-control-board-lpc55-run.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 172 firmware.component.laser-control-board-lpc55-run.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 173 firmware.component.laser-control-board-lpc55-run.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 174 firmware.component.laser-control-board-lpc55-run.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 175 firmware.component.laser-control-board-lpc55-run.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 176 firmware.component.laser-driver-module-1-hdr.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 177 firmware.component.laser-driver-module-1-hdr.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 178 firmware.component.laser-driver-module-1-hdr.error 

```
The error message in case of an upgrade error.
Type: string
```

Platinum API JSON RPC Reference Page 71 of 171

7. 0. 179 firmware.component.laser-driver-module-1-hdr.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 180 firmware.component.laser-driver-module-1-hdr.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 181 firmware.component.laser-driver-module-1-hdr.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 182 firmware.component.laser-driver-module-1-hdr.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 183 firmware.component.laser-driver-module-1-primary.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 184 firmware.component.laser-driver-module-1-primary.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 185 firmware.component.laser-driver-module-1-primary.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 186 firmware.component.laser-driver-module-1-primary.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```

Page 72 of 171 JSON RPC Reference Platinum API

7. 0. 187 firmware.component.laser-driver-module-1-primary.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 188 firmware.component.laser-driver-module-1-primary.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 189 firmware.component.laser-driver-module-1-primary.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 190 firmware.component.laser-driver-module-1-secondary.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 191 firmware.component.laser-driver-module-1-secondary.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 192 firmware.component.laser-driver-module-1-secondary.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 193 firmware.component.laser-driver-module-1-secondary.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 194 firmware.component.laser-driver-module-1-secondary.progress 

```
The progress of the current firmware upgrade
Type: int
```

Platinum API JSON RPC Reference Page 73 of 171

7. 0. 195 firmware.component.laser-driver-module-1-secondary.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 196 firmware.component.laser-driver-module-1-secondary.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 197 firmware.component.laser-driver-module-1-slot-1.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 198 firmware.component.laser-driver-module-1-slot-1.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 199 firmware.component.laser-driver-module-1-slot-1.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 200 firmware.component.laser-driver-module-1-slot-1.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 201 firmware.component.laser-driver-module-1-slot-1.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 202 firmware.component.laser-driver-module-1-slot-1.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```

Page 74 of 171 JSON RPC Reference Platinum API

7. 0. 203 firmware.component.laser-driver-module-1-slot-1.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 204 firmware.component.laser-driver-module-1-slot-2.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 205 firmware.component.laser-driver-module-1-slot-2.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 206 firmware.component.laser-driver-module-1-slot-2.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 207 firmware.component.laser-driver-module-1-slot-2.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 208 firmware.component.laser-driver-module-1-slot-2.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 209 firmware.component.laser-driver-module-1-slot-2.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 210 firmware.component.laser-driver-module-1-slot-2.status 

```
The status of the current firmware upgrade
Type: enum
```

Platinum API JSON RPC Reference Page 75 of 171

```
Inactive
Active
Error
Finished
```
7. 0. 211 firmware.component.laser-driver-module-1-slot-3.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 212 firmware.component.laser-driver-module-1-slot-3.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 213 firmware.component.laser-driver-module-1-slot-3.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 214 firmware.component.laser-driver-module-1-slot-3.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 215 firmware.component.laser-driver-module-1-slot-3.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 216 firmware.component.laser-driver-module-1-slot-3.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 217 firmware.component.laser-driver-module-1-slot-3.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```

Page 76 of 171 JSON RPC Reference Platinum API

7. 0. 218 firmware.component.laser-driver-module-1-slot-6.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 219 firmware.component.laser-driver-module-1-slot-6.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 220 firmware.component.laser-driver-module-1-slot-6.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 221 firmware.component.laser-driver-module-1-slot-6.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 222 firmware.component.laser-driver-module-1-slot-6.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 223 firmware.component.laser-driver-module-1-slot-6.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 224 firmware.component.laser-driver-module-1-slot-6.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 225 firmware.component.laser-driver-module-1-slot-7.actualversion 

```
The version of the currently installed firmware.
Type: string
```

Platinum API JSON RPC Reference Page 77 of 171

7. 0. 226 firmware.component.laser-driver-module-1-slot-7.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 227 firmware.component.laser-driver-module-1-slot-7.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 228 firmware.component.laser-driver-module-1-slot-7.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 229 firmware.component.laser-driver-module-1-slot-7.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 230 firmware.component.laser-driver-module-1-slot-7.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 231 firmware.component.laser-driver-module-1-slot-7.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 232 firmware.component.laser-power-module-1-slot-8.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 233 firmware.component.laser-power-module-1-slot-8.displayname 

```
The user-friendly name of the firmware component.
Type: string
```

Page 78 of 171 JSON RPC Reference Platinum API

7. 0. 234 firmware.component.laser-power-module-1-slot-8.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 235 firmware.component.laser-power-module-1-slot-8.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 236 firmware.component.laser-power-module-1-slot-8.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 237 firmware.component.laser-power-module-1-slot-8.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 238 firmware.component.laser-power-module-1-slot-8.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 239 firmware.component.mainboard-power-sequencer.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 240 firmware.component.mainboard-power-sequencer.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 241 firmware.component.mainboard-power-sequencer.error 

```
The error message in case of an upgrade error.
Type: string
```

Platinum API JSON RPC Reference Page 79 of 171

7. 0. 242 firmware.component.mainboard-power-sequencer.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 243 firmware.component.mainboard-power-sequencer.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 244 firmware.component.mainboard-power-sequencer.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 245 firmware.component.mainboard-power-sequencer.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 246 firmware.component.peltier-control-board-boot-dn512a.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 247 firmware.component.peltier-control-board-boot-dn512a.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 248 firmware.component.peltier-control-board-boot-dn512a.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 249 firmware.component.peltier-control-board-boot-dn512a.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```

Page 80 of 171 JSON RPC Reference Platinum API

7. 0. 250 firmware.component.peltier-control-board-boot-dn512a.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 251 firmware.component.peltier-control-board-boot-dn512a.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 252 firmware.component.peltier-control-board-boot-dn512a.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 253 firmware.component.peltier-control-board-run-dn512a.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 254 firmware.component.peltier-control-board-run-dn512a.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 255 firmware.component.peltier-control-board-run-dn512a.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 256 firmware.component.peltier-control-board-run-dn512a.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 257 firmware.component.peltier-control-board-run-dn512a.progress 

```
The progress of the current firmware upgrade
Type: int
```

Platinum API JSON RPC Reference Page 81 of 171

7. 0. 258 firmware.component.peltier-control-board-run-dn512a.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 259 firmware.component.peltier-control-board-run-dn512a.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 260 firmware.component.peri-fpga.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 261 firmware.component.peri-fpga.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 262 firmware.component.peri-fpga.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 263 firmware.component.peri-fpga.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 264 firmware.component.peri-fpga.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 265 firmware.component.peri-fpga.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```

Page 82 of 171 JSON RPC Reference Platinum API

7. 0. 266 firmware.component.peri-fpga.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 267 firmware.component.power-distribution-board-fcb-fpga.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 268 firmware.component.power-distribution-board-fcb-fpga.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 269 firmware.component.power-distribution-board-fcb-fpga.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 270 firmware.component.power-distribution-board-fcb-fpga.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 271 firmware.component.power-distribution-board-fcb-fpga.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 272 firmware.component.power-distribution-board-fcb-fpga.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 273 firmware.component.power-distribution-board-fcb-fpga.status 

```
The status of the current firmware upgrade
Type: enum
```

Platinum API JSON RPC Reference Page 83 of 171

```
Inactive
Active
Error
Finished
```
```
7. 0. 274 firmware.component.power-distribution-board-lpc5504jhi48-
boot.actualversion 
```
```
The version of the currently installed firmware.
Type: string
```
```
7. 0. 275 firmware.component.power-distribution-board-lpc5504jhi48-
boot.displayname 
```
```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 276 firmware.component.power-distribution-board-lpc5504jhi48-boot.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 277 firmware.component.power-distribution-board-lpc5504jhi48-boot.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 278 firmware.component.power-distribution-board-lpc5504jhi48-boot.progress 

```
The progress of the current firmware upgrade
Type: int
```
```
7. 0. 279 firmware.component.power-distribution-board-lpc5504jhi48-
boot.requiredversion 
```
```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 280 firmware.component.power-distribution-board-lpc5504jhi48-boot.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
```

Page 84 of 171 JSON RPC Reference Platinum API

```
Finished
```
```
7. 0. 281 firmware.component.power-distribution-board-lpc5504jhi48-
run.actualversion 
```
```
The version of the currently installed firmware.
Type: string
```
```
7. 0. 282 firmware.component.power-distribution-board-lpc5504jhi48-
run.displayname 
```
```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 283 firmware.component.power-distribution-board-lpc5504jhi48-run.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 284 firmware.component.power-distribution-board-lpc5504jhi48-run.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 285 firmware.component.power-distribution-board-lpc5504jhi48-run.progress 

```
The progress of the current firmware upgrade
Type: int
```
```
7. 0. 286 firmware.component.power-distribution-board-lpc5504jhi48-
run.requiredversion 
```
```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 287 firmware.component.power-distribution-board-lpc5504jhi48-run.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```

Platinum API JSON RPC Reference Page 85 of 171

7. 0. 288 firmware.component.power-distribution-board-lsr-fantable-ac.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 289 firmware.component.power-distribution-board-lsr-fantable-ac.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 290 firmware.component.power-distribution-board-lsr-fantable-ac.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 291 firmware.component.power-distribution-board-lsr-fantable-ac.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 292 firmware.component.power-distribution-board-lsr-fantable-ac.progress 

```
The progress of the current firmware upgrade
Type: int
```
```
7. 0. 293 firmware.component.power-distribution-board-lsr-fantable-
ac.requiredversion 
```
```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 294 firmware.component.power-distribution-board-lsr-fantable-ac.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
```
7. 0. 295 firmware.component.power-distribution-board-lsr-fantable-on-
silent.actualversion 
```
```
The version of the currently installed firmware.
```

Page 86 of 171 JSON RPC Reference Platinum API

```
Type: string
```
```
7. 0. 296 firmware.component.power-distribution-board-lsr-fantable-on-
silent.displayname 
```
```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 297 firmware.component.power-distribution-board-lsr-fantable-on-silent.error 

```
The error message in case of an upgrade error.
Type: string
```
```
7. 0. 298 firmware.component.power-distribution-board-lsr-fantable-on-
silent.mismatch 
```
```
Indicate whether there is a version mismatch
Type: bool
```
```
7. 0. 299 firmware.component.power-distribution-board-lsr-fantable-on-
silent.progress 
```
```
The progress of the current firmware upgrade
Type: int
```
```
7. 0. 300 firmware.component.power-distribution-board-lsr-fantable-on-
silent.requiredversion 
```
```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 301 firmware.component.power-distribution-board-lsr-fantable-on-silent.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 302 firmware.component.power-distribution-board-lsr-fantable-on.actualversion 

```
The version of the currently installed firmware.
Type: string
```

Platinum API JSON RPC Reference Page 87 of 171

7. 0. 303 firmware.component.power-distribution-board-lsr-fantable-on.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 304 firmware.component.power-distribution-board-lsr-fantable-on.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 305 firmware.component.power-distribution-board-lsr-fantable-on.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 306 firmware.component.power-distribution-board-lsr-fantable-on.progress 

```
The progress of the current firmware upgrade
Type: int
```
```
7. 0. 307 firmware.component.power-distribution-board-lsr-fantable-
on.requiredversion 
```
```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 308 firmware.component.power-distribution-board-lsr-fantable-on.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 309 firmware.component.power-distribution-board-lsr-fantable-sb.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 310 firmware.component.power-distribution-board-lsr-fantable-sb.displayname 

```
The user-friendly name of the firmware component.
Type: string
```

Page 88 of 171 JSON RPC Reference Platinum API

7. 0. 311 firmware.component.power-distribution-board-lsr-fantable-sb.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 312 firmware.component.power-distribution-board-lsr-fantable-sb.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 313 firmware.component.power-distribution-board-lsr-fantable-sb.progress 

```
The progress of the current firmware upgrade
Type: int
```
```
7. 0. 314 firmware.component.power-distribution-board-lsr-fantable-
sb.requiredversion 
```
```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 315 firmware.component.power-distribution-board-lsr-fantable-sb.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 316 firmware.component.power-distribution-board-lsr-fantable-tc.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 317 firmware.component.power-distribution-board-lsr-fantable-tc.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 318 firmware.component.power-distribution-board-lsr-fantable-tc.error 

```
The error message in case of an upgrade error.
```

Platinum API JSON RPC Reference Page 89 of 171

```
Type: string
```
7. 0. 319 firmware.component.power-distribution-board-lsr-fantable-tc.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 320 firmware.component.power-distribution-board-lsr-fantable-tc.progress 

```
The progress of the current firmware upgrade
Type: int
```
```
7. 0. 321 firmware.component.power-distribution-board-lsr-fantable-
tc.requiredversion 
```
```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 322 firmware.component.power-distribution-board-lsr-fantable-tc.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 323 firmware.component.power-distribution-board-mcb-fpga.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 324 firmware.component.power-distribution-board-mcb-fpga.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 325 firmware.component.power-distribution-board-mcb-fpga.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 326 firmware.component.power-distribution-board-mcb-fpga.mismatch 


Page 90 of 171 JSON RPC Reference Platinum API

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 327 firmware.component.power-distribution-board-mcb-fpga.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 328 firmware.component.power-distribution-board-mcb-fpga.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 329 firmware.component.power-distribution-board-mcb-fpga.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 330 firmware.component.status 

```
The status of the current component firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 331 firmware.component.switch-mode-power-supply.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 332 firmware.component.switch-mode-power-supply.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 333 firmware.component.switch-mode-power-supply.error 

```
The error message in case of an upgrade error.
```

Platinum API JSON RPC Reference Page 91 of 171

```
Type: string
```
7. 0. 334 firmware.component.switch-mode-power-supply.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 335 firmware.component.switch-mode-power-supply.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 336 firmware.component.switch-mode-power-supply.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 337 firmware.component.switch-mode-power-supply.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 338 firmware.component.u-boot-img.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 339 firmware.component.u-boot-img.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 340 firmware.component.u-boot-img.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 341 firmware.component.u-boot-img.mismatch 

```
Indicate whether there is a version mismatch
```

Page 92 of 171 JSON RPC Reference Platinum API

```
Type: bool
```
7. 0. 342 firmware.component.u-boot-img.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 343 firmware.component.u-boot-img.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 344 firmware.component.u-boot-img.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 345 firmware.component.u-boot-spl.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 346 firmware.component.u-boot-spl.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 347 firmware.component.u-boot-spl.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 348 firmware.component.u-boot-spl.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 349 firmware.component.u-boot-spl.progress 

```
The progress of the current firmware upgrade
```

Platinum API JSON RPC Reference Page 93 of 171

```
Type: int
```
7. 0. 350 firmware.component.u-boot-spl.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 351 firmware.component.u-boot-spl.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 352 firmware.component.wobulator-boot.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 353 firmware.component.wobulator-boot.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 354 firmware.component.wobulator-boot.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 355 firmware.component.wobulator-boot.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 356 firmware.component.wobulator-boot.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 357 firmware.component.wobulator-boot.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
```

Page 94 of 171 JSON RPC Reference Platinum API

```
Type: string
```
7. 0. 358 firmware.component.wobulator-boot.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 359 firmware.component.wobulator-run.actualversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 360 firmware.component.wobulator-run.displayname 

```
The user-friendly name of the firmware component.
Type: string
```
7. 0. 361 firmware.component.wobulator-run.error 

```
The error message in case of an upgrade error.
Type: string
```
7. 0. 362 firmware.component.wobulator-run.mismatch 

```
Indicate whether there is a version mismatch
Type: bool
```
7. 0. 363 firmware.component.wobulator-run.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 364 firmware.component.wobulator-run.requiredversion 

```
The firmware version this component is expected to have by the current firmware package.
Type: string
```
7. 0. 365 firmware.component.wobulator-run.status 

```
The status of the current firmware upgrade
```

Platinum API JSON RPC Reference Page 95 of 171

```
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 366 firmware.error 

```
The error of the last firmware upgrade (only set if status is error)
Type: string
```
7. 0. 367 firmware.eula.requiretermagreement 

```
Indiates whether or not the user is required to accept the term agreement.
Type: bool
```
7. 0. 368 firmware.eula.termagreement

```
The user agreement with the firmware EULA.
Type: bool
```
7. 0. 369 firmware.firmwareversion 

```
The version of the currently installed firmware.
Type: string
```
7. 0. 370 firmware.progress 

```
The progress of the current firmware upgrade
Type: int
```
7. 0. 371 firmware.status 

```
The status of the current firmware upgrade
Type: enum
```
```
Inactive
Active
Error
Finished
```
7. 0. 372 iot.certificate.applicable 

```
True if the certificate applies to this projector
Type: bool
```

Page 96 of 171 JSON RPC Reference Platinum API

7. 0. 373 iot.certificate.available 

```
True if a certificate was found
Type: bool
```
7. 0. 374 iot.certificate.valid 

```
Result of the validity check of the certificate
Type: bool
```
7. 0. 375 iot.cloudservices.connectionstate 

```
The current state of the connection.
Type: enum
```
```
CONNECTED
DISCONNECTED
CONNECTING
DISCONNECTING
FAILED
```
7. 0. 376 iot.cloudservices.enable

```
True if IOT cloud connection is enabled, false otherwise
Type: bool
```
7. 0. 377 iot.proxy.address

```
This is the address (hostname/ip) of the proxy.
Type: string
```
7. 0. 378 iot.proxy.enabled

```
When enabled, iot connection will go over proxy specified in othe proxy parameters
Type: bool
```
7. 0. 379 iot.proxy.password

```
Password used to log in to proxy.
Type: string
```
7. 0. 380 iot.proxy.port

```
The port to use for the proxy conenction.
Type: int
```

Platinum API JSON RPC Reference Page 97 of 171

7. 0. 381 iot.proxy.username

```
Username used to log in to proxy.
Type: string
```
7. 0. 382 iot.requiretermagreement 

```
Indiates whether or not the user is required to accept the term agreement.
Type: bool
```
7. 0. 383 iot.termagreement

```
Represents the users acknowledge of the IOT terms of agreement.
Type: bool
```
7. 0. 384 keydispatcher.repeatdelay 

```
Initial key repeat delay in milliseconds
Type: int
```
7. 0. 385 keydispatcher.repeatinterval 

```
Key repeat interval in milliseconds
Type: int
```
7. 0. 386 network.device.lan.carrier 

```
Whether the device has carrier or not
Type: bool
```
7. 0. 387 network.device.lan.configuration

```
The configuration method of the device: auto or manual
Type: enum
```
```
AUTO
MANUAL
```
7. 0. 388 network.device.lan.devicetype 

```
The general type of the network device
Type: enum
```
```
WIRED
WIRELESS
```

Page 98 of 171 JSON RPC Reference Platinum API

### MOBILE

7. 0. 389 network.device.lan.hwaddress 

```
The active hardware (MAC) address
Type: string
```
7. 0. 390 network.device.lan.ip4config 

```
The current configuration for IP version 4
Type: object
```
```
Address : string
Mask : string
Gateway : string
NameServers : string
```
7. 0. 391 network.device.lan.ip4configmanual

```
Get/set the manual configuration for IP version 4
Type: object
```
```
Address : string
Mask : string
Gateway : string
NameServers : string
```
7. 0. 392 network.device.lan.ip6config 

```
The current configuration for IP version 6
Type: object
```
```
Address : string
Prefix : string
Gateway : string
NameServers : string
```
7. 0. 393 network.device.lan.ip6configmanual

```
Get/set the manual configuration for IP version 4
Type: object
```
```
Address : string
Prefix : string
Gateway : string
NameServers : string
```
7. 0. 394 network.device.lan.speed 


Platinum API JSON RPC Reference Page 99 of 171

```
The speed of the device in Mbit/s
Type: int
```
7. 0. 395 network.device.lan.state 

```
The current state of the device
Type: enum
```
```
CONNECTED
DISCONNECTED
CONNECTING
NEEDAUTH
IPCONFIG
IPCHECK
DISCONNECTING
FAILED
```
7. 0. 396 network.device.lan.stateinfo 

```
Additional information about the device state. Can be empty
Type: string
```
7. 0. 397 network.domain

```
The domain name
Type: string
```
7. 0. 398 network.hostname

```
The host name
Type: string
```
7. 0. 399 network.linkedservices.availablepeers 

```
These peers are available on the network.
Type: object[ ]
```
```
Address : string
Hostname : string
Port : string
Serial : string
Name : string
Product : string
```
7. 0. 400 network.linkedservices.grouplist 

```
Available groups this device is master of.
```

Page 100 of 171 JSON RPC Reference Platinum API

```
Type: string[ ]
```
7. 0. 401 network.linkedservices.membershiplist 

```
Available Groups this device is part of as a slave.
Type: string[ ]
```
7. 0. 402 network.version 

```
The Networking Service version
Type: string
```
7. 0. 403 notification.count 

```
The number of notifications received and dismissed
Type: int
```
7. 0. 404 protocols.pjlink.authenticationrequired 

```
Enable/disable PJLink authentication procedure
Type: bool
```
7. 0. 405 protocols.pjlink.enable 

```
Enable/disable PJLink
Type: bool
```
7. 0. 406 remotecontrol.address

```
The address of the remote control that the projector will respond to
Type: int
```
```
Min: 1
```
```
Max: 31
```
```
Precision: 1
```
```
Step size: 1
```
7. 0. 407 remotecontrol.broadcastaddress

```
The broadcast address
Type: int
```
```
Min: 0
```
```
Max: 1
```

Platinum API JSON RPC Reference Page 101 of 171

```
Precision: 1
```
```
Step size: 1
```
7. 0. 408 remotecontrol.sensors.front.enable

```
Enable or disable the IR sensor
Type: bool
```
7. 0. 409 remotecontrol.sensors.front.name 

```
The display name of the IR sensor
Type: string
```
7. 0. 410 remotecontrol.sensors.rear.enable

```
Enable or disable the IR sensor
Type: bool
```
7. 0. 411 remotecontrol.sensors.rear.name 

```
The display name of the IR sensor
Type: string
```
7. 0. 412 remotecontrol.sensors.side.enable

```
Enable or disable the IR sensor
Type: bool
```
7. 0. 413 remotecontrol.sensors.side.name 

```
The display name of the IR sensor
Type: string
```
7. 0. 414 scheduler.actions 

```
List of all scheduled actions' name.
Type: string[ ]
```
7. 0. 415 scheduler.actiontypes 

```
List of all available action types.
Type: string[ ]
```

Page 102 of 171 JSON RPC Reference Platinum API

7. 0. 416 scheduler.nextscheduledaction 

```
The next task(s) that will be executed. (Can be more than one task if multiple tasks have the exact same execution time.)
Type: object[ ]
```
```
Name : string
Type : string
Transition : string
Macro : string
Profile : string
LaunchTimePoint : string
```
7. 0. 417 scheduler.pause

```
Return True if action is paused, otherwise return False.
Type: bool
```
7. 0. 418 scheduler.scheduledactions

```
List of all scheduled actions data.
Type: string
```
7. 0. 419 scheduler.transitions 

```
List of all available transitions for system action.
Type: string[ ]
```
7. 0. 420 statistics.laser plate 1 bank 1 runtime.value 

```
Counter value
Type: int
```
7. 0. 421 statistics.laser plate 1 bank 2 runtime.value 

```
Counter value
Type: int
```
7. 0. 422 statistics.laser plate 1 bank 3 runtime.value 

```
Counter value
Type: int
```
7. 0. 423 statistics.laser plate 2 bank 1 runtime.value 

```
Counter value
```

Platinum API JSON RPC Reference Page 103 of 171

```
Type: int
```
7. 0. 424 statistics.laser plate 2 bank 2 runtime.value 

```
Counter value
Type: int
```
7. 0. 425 statistics.laser plate 2 bank 3 runtime.value 

```
Counter value
Type: int
```
7. 0. 426 statistics.laser plate 3 bank 1 runtime.value 

```
Counter value
Type: int
```
7. 0. 427 statistics.laser plate 3 bank 2 runtime.value 

```
Counter value
Type: int
```
7. 0. 428 statistics.laser plate 3 bank 3 runtime.value 

```
Counter value
Type: int
```
7. 0. 429 statistics.laser plate 4 bank 1 runtime.value 

```
Counter value
Type: int
```
7. 0. 430 statistics.laser plate 4 bank 2 runtime.value 

```
Counter value
Type: int
```
7. 0. 431 statistics.laser plate 4 bank 3 runtime.value 

```
Counter value
Type: int
```
7. 0. 432 statistics.laser plate 5 bank 1 runtime.value 


Page 104 of 171 JSON RPC Reference Platinum API

```
Counter value
Type: int
```
7. 0. 433 statistics.laser plate 5 bank 2 runtime.value 

```
Counter value
Type: int
```
7. 0. 434 statistics.laser plate 5 bank 3 runtime.value 

```
Counter value
Type: int
```
7. 0. 435 statistics.laserruntime.value 

```
Counter value
Type: int
```
7. 0. 436 statistics.projectorruntime.value 

```
Counter value
Type: int
```
7. 0. 437 statistics.systemtime.value 

```
Counter value
Type: int
```
7. 0. 438 statistics.uptime.value 

```
Counter value
Type: int
```
7. 0. 439 system.articlenumber 

```
Article number.
Type: string
```
7. 0. 440 system.colorwheel 

```
Article number of installed color wheel
Type: string
```

Platinum API JSON RPC Reference Page 105 of 171

7. 0. 441 system.colorwheelname 

```
Name of installed color wheel
Type: string
```
7. 0. 442 system.date.availabletimezones 

```
An array of all available time zones and their information.
Type: object[ ]
```
```
name : string
```
7. 0. 443 system.date.ntp.connected 

```
True if there is a connection to the NTP-server.
Type: bool
```
7. 0. 444 system.date.ntp.enabled 

```
True if NTP time synchronization should be used.
Type: bool
```
7. 0. 445 system.date.ntp.server 

```
The NTP server hostname or address.
Type: string
```
7. 0. 446 system.date.timezone 

```
The configured time zone of the system.
Type: string
```
7. 0. 447 system.eco.available 

```
Returns true if state is available for this projector
Type: bool
```
7. 0. 448 system.eco.enable

```
Enable/disable the use of this state. Check if available first.
Type: bool
```
7. 0. 449 system.familyname 


Page 106 of 171 JSON RPC Reference Platinum API

```
Family name.
Type: string
```
7. 0. 450 system.firmwareversion 

```
Firmware version.
Type: string
```
7. 0. 451 system.health 

```
The current global health state of the projector. State error means the projector can not safely be operated. Warning means
the show can go on, but it is strongly advised to find the cause of the warning and solve it. Normal means the projector is
performing normally.
Type: enum
```
```
Normal
Warning
Error
```
7. 0. 452 system.initialstate

```
State to transition to when the unit is started
Type: enum
```
```
boot
eco
standby
ready
conditioning
on
service
deconditioning
error
```
7. 0. 453 system.license.applicable 

```
Applicability of the license file.
Type: bool
```
7. 0. 454 system.license.available 

```
Availability of a license file.
Type: bool
```
7. 0. 455 system.license.options 

```
A dictionary of options and their values.
Type: object[ ]
```

Platinum API JSON RPC Reference Page 107 of 171

```
key : string
value : string
```
7. 0. 456 system.license.register.mandatory 

```
Shows if registering the product is mandatory or optional
Type: bool
```
7. 0. 457 system.license.register.remaining 

```
Time left in minutes until registration must be performed.
Type: int
```
7. 0. 458 system.license.register.total 

```
Total grace period in minutes until registration must be performed.
Type: int
```
7. 0. 459 system.license.register.valid 

```
True when the product has been successfully registered.
Type: bool
```
7. 0. 460 system.license.valid 

```
Validity of the license file.
Type: bool
```
7. 0. 461 system.modelname 

```
Model name.
Type: string
```
7. 0. 462 system.name 

```
Custom name for this device.
Type: string
```
7. 0. 463 system.on.timeout.duration

```
Time (in seconds) to wait in this state before entering lower state.
Type: int
```
```
Min: 60
```

Page 108 of 171 JSON RPC Reference Platinum API

```
Max: 7200
```
```
Precision: 1
```
```
Step size: 30
```
7. 0. 464 system.on.timeout.enable

```
Enable/disable the timeout.
Type: bool
```
7. 0. 465 system.on.timeout.remaining 

```
The remaining amount of seconds before the timer will timeout.
Type: int
```
7. 0. 466 system.operationalmodes.availablemodes 

```
List of available operational modes
Type: enum[ ]
```
7. 0. 467 system.operationalmodes.mode

```
The currently active operational mode
Type: enum
```
```
normal
silent
longlife
highbrightness
```
7. 0. 468 system.ready.timeout.duration

```
Time (in seconds) to wait in this state before entering lower state.
Type: int
```
```
Min: 60
```
```
Max: 7200
```
```
Precision: 1
```
```
Step size: 30
```
7. 0. 469 system.ready.timeout.enable

```
Enable/disable the timeout.
Type: bool
```

Platinum API JSON RPC Reference Page 109 of 171

7. 0. 470 system.ready.timeout.remaining 

```
The remaining amount of seconds before the timer will timeout.
Type: int
```
7. 0. 471 system.resetprogress 

```
Reset progress: [0..100]
Type: int
```
7. 0. 472 system.resetresult 

```
Description is missing!!!
```
```
Type: object
```
```
time : string
result : enum
UNKNOWN
SUCCESS
FAILED
```
7. 0. 473 system.resetstatus 

```
Reset status
Type: enum
```
```
Idle
Resetting
Failed
Finished
```
7. 0. 474 system.serialnumber 

```
Serial number.
Type: string
```
7. 0. 475 system.standby.available 

```
Returns true if state is available for this projector
Type: bool
```
7. 0. 476 system.standby.enable

```
Enable/disable the use of this state. Check if available first.
Type: bool
```

Page 110 of 171 JSON RPC Reference Platinum API

7. 0. 477 system.standby.timeout.duration

```
Time (in seconds) to wait in this state before entering lower state.
Type: int
```
```
Min: 60
```
```
Max: 7200
```
```
Precision: 1
```
```
Step size: 30
```
7. 0. 478 system.standby.timeout.enable

```
Enable/disable the timeout.
Type: bool
```
7. 0. 479 system.standby.timeout.remaining 

```
The remaining amount of seconds before the timer will timeout.
Type: int
```
7. 0. 480 system.state 

```
The current state of the unit
Type: enum
```
```
boot
eco
standby
ready
conditioning
on
service
deconditioning
error
```
7. 0. 481 system.targetstate 

```
The state the unit is transitioning into
Type: enum
```
```
boot
eco
standby
ready
conditioning
on
service
deconditioning
error
```

Platinum API JSON RPC Reference Page 111 of 171

7. 0. 482 ui.access.enduser 

```
True and available when the user has end user access privileges.
Type: bool
```
7. 0. 483 ui.backlight.state

```
Description is missing!!!
```
```
Type: enum
```
```
Off
On
Auto
```
7. 0. 484 ui.backlight.timeout

```
The amount of seconds after which the lcd backlight will be switched off when the menu and stealth mode are not active and
there is no activity.
Type: int
```
```
Min: 5
```
```
Max: 3600
```
```
Precision: 1
```
```
Step size: 1
```
7. 0. 485 ui.hasstealthmode 

```
Description is missing!!!
```
```
Type: bool
```
7. 0. 486 ui.language

```
The user interface language
Type: string
```
7. 0. 487 ui.layer.advancedblend.drawing

```
Drawing commands in the form of a JSON object
Type: string
```
7. 0. 488 ui.layer.advancedblend.enable

```
Enable or disable the layer
Type: bool
```

Page 112 of 171 JSON RPC Reference Platinum API

7. 0. 489 ui.layer.advancedblend.palette

```
Color palette that can be used when drawing the blend layer
Type: string[ ]
```
7. 0. 490 ui.layer.basicblacklevel.color

```
The edge color, e.g '#ffff00' or 'rgba(255,255,0,0.5)
Type: string
```
7. 0. 491 ui.layer.basicblacklevel.enable

```
Enable or disable the layer
Type: bool
```
7. 0. 492 ui.layer.basicblacklevel.selection

```
Toggle edge selection
Type: object
```
```
Bottom : bool
Left : bool
Right : bool
Top : bool
```
7. 0. 493 ui.layer.basicblacklevel.selectioncolor

```
The color to use for selected edges, e.g '#ff0000' or 'rgba(255,0,0,0.5)'
Type: string
```
7. 0. 494 ui.layer.basicblend.color

```
The edge color, e.g '#ffff00' or 'rgba(255,255,0,0.5)
Type: string
```
7. 0. 495 ui.layer.basicblend.enable

```
Enable or disable the layer
Type: bool
```
7. 0. 496 ui.layer.basicblend.selection

```
Toggle edge selection
Type: object
```

Platinum API JSON RPC Reference Page 113 of 171

```
Bottom : bool
Left : bool
Right : bool
Top : bool
```
7. 0. 497 ui.layer.basicblend.selectioncolor

```
The color to use for selected edges, e.g '#ff0000' or 'rgba(255,0,0,0.5)'
Type: string
```
7. 0. 498 ui.layer.blank.border

```
(Optional) Show/hide a border/outline of the screen
Type: bool
```
7. 0. 499 ui.layer.blank.bordercolor

```
(Optional) Specify the border color, e.g '#ff0000' or 'rgba(255,0,0,0.75)'
Type: string
```
7. 0. 500 ui.layer.blank.enable

```
Enable or disable the layer. When enabled, the screen will be covered in black.
Type: bool
```
7. 0. 501 ui.layer.blank.icon

```
A single UTF character from the Barco-Icons font set.
Type: string
```
7. 0. 502 ui.layer.blank.show

```
Used only for persisting whether or not to show the layer
Type: bool
```
7. 0. 503 ui.layer.blank.showtext

```
Show or hide the text
Type: bool
```
7. 0. 504 ui.layer.blank.text

```
(Optional) Specify a text to show at the center of the screen
Type: string
```

Page 114 of 171 JSON RPC Reference Platinum API

7. 0. 505 ui.layer.fourcorner.cornercolor

```
The color to use for unselected corners, e.g '#ff0000' or 'rgba(255,0,0,0.75)'
Type: string
```
7. 0. 506 ui.layer.fourcorner.enable

```
Enable or disable the layer
Type: bool
```
7. 0. 507 ui.layer.fourcorner.linecolor

```
The line color, e.g '#ffff00' or 'rgba(255,255,0,0.5)'
Type: string
```
7. 0. 508 ui.layer.fourcorner.lines

```
Show or hide lines between the corners
Type: bool
```
7. 0. 509 ui.layer.fourcorner.selection

```
Toggle corner selection
Type: object
```
```
TopLeft : bool
TopRight : bool
BottomRight : bool
BottomLeft : bool
```
7. 0. 510 ui.layer.fourcorner.selectioncolor

```
The color to use for selected corners, e.g '#ff0000' or 'rgba(255,0,0,0.75)'
Type: string
```
7. 0. 511 ui.layer.grid.color

```
Default color for grid points, e.g '#ff0000' or 'rgba(0,0,255,0.5)'
Type: string
```
7. 0. 512 ui.layer.grid.enable

```
Enable or disable the layer
Type: bool
```

Platinum API JSON RPC Reference Page 115 of 171

7. 0. 513 ui.layer.grid.lines

```
DEPRECATED. Use ShowLines instead. This is for backwards compability
Type: bool
```
7. 0. 514 ui.layer.grid.mark

```
List of row,column and color triplets for marking points in the grid. The color is specified as '#ff00ff' or 'rgba(0,255,255,0.75)'
Type: object[ ]
```
```
X : object
base : int
hints : object
signed :
bitwidth :
Y : object
base : int
hints : object
signed :
bitwidth :
Color : string
```
7. 0. 515 ui.layer.grid.points

```
Number of grid points
Type: enum
```
```
2x2
3x3
5x5
9x9
17x17
33x33
```
7. 0. 516 ui.layer.grid.showlines

```
Toggle drawing lines between grid points
Type: bool
```
7. 0. 517 ui.layer.grid.showpoints

```
Toggle drawing grid points
Type: bool
```
7. 0. 518 ui.length

```
Preferred unit for display of lengths and distances
Type: enum
```
```
M
```

Page 116 of 171 JSON RPC Reference Platinum API

### CM

### FT

### IN

7. 0. 519 ui.lensmenu

```
Show or hide the lens menu
Type: bool
```
7. 0. 520 ui.luminance

```
Preferred unit for luminance
Type: enum
```
```
NITS
FL
```
7. 0. 521 ui.menu

```
Show or hide the menu
Type: bool
```
7. 0. 522 ui.menuposition

```
Placement of menu related to full screen.
Type: enum
```
```
TopLeft
Top
TopRight
Right
BottomRight
Bottom
BottomLeft
Left
Center
```
7. 0. 523 ui.message 

```
The persistent message to show on the screen. Rich text allowed
Type: object
```
```
title : string
icon : string
message : string
```
7. 0. 524 ui.minimize

```
Minimize the menu when it is enabled
```

Platinum API JSON RPC Reference Page 117 of 171

```
Type: bool
```
7. 0. 525 ui.osd

```
Enable or disable on screen display
Type: bool
```
7. 0. 526 ui.patternmenu

```
Show or hide the pattern menu shortcut
Type: bool
```
7. 0. 527 ui.poweroffhint

```
When true, a dialog shows info about powering down
Type: bool
```
7. 0. 528 ui.showmessage 

```
Show a persistent message on the screen
Type: bool
```
7. 0. 529 ui.sourcemenu

```
Show or hide the input source shortcut menu
Type: bool
```
7. 0. 530 ui.sourcesignal

```
Show/hide the source signal information popup
Type: bool
```
7. 0. 531 ui.sourcesignalposition

```
Placement of the source signal information
Type: enum
```
```
TopLeft
Top
TopRight
Right
BottomRight
Bottom
BottomLeft
Left
Center
```

Page 118 of 171 JSON RPC Reference Platinum API

7. 0. 532 ui.splashscreen.show 

```
Value to indicate if the splash screen should be shown
Type: bool
```
7. 0. 533 ui.splashscreen.timeoutseconds 

```
Time (in seconds) the splash screen is shown on startup
Type: int
```
7. 0. 534 ui.stealthmode

```
When the projector is in stealth mode, all controllable LEDs are switched off.
Type: enum
```
```
Off
On
OnUntilReboot
```
7. 0. 535 ui.temperature

```
Preferred unit for display of temperature values
Type: enum
```
```
C
F
```
7. 0. 536 ui.theme

```
The theme setting of the user interface.
Type: enum
```
```
Light
Dark
```
7. 0. 537 ui.touchscreen.mode 

```
Enables or disables the touchscreen test.
Type: enum
```
```
Normal
Test
```
7. 0. 538 ui.touchscreen.status

```
Current status of the touchscreen text
Type: enum
```

Platinum API JSON RPC Reference Page 119 of 171

```
Inactive
Ongoing
Complete
```
7. 0. 539 user.admin.activesessioncount 

```
Description is missing!!!
```
```
Type: int
```
7. 0. 540 user.admin.enabled 

```
Description is missing!!!
```
```
Type: bool
```
7. 0. 541 user.admin.group 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 542 user.admin.publickey 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 543 user.admin.username 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 544 user.admin.userslug 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 545 user.authenticationrequired 

```
Require authentication of all users
Type: bool
```
7. 0. 546 user.availablegroups 

```
The available user groups
Type: string[ ]
```

Page 120 of 171 JSON RPC Reference Platinum API

7. 0. 547 user.currentuser.activesessioncount 

```
Description is missing!!!
```
```
Type: int
```
7. 0. 548 user.currentuser.enabled 

```
Description is missing!!!
```
```
Type: bool
```
7. 0. 549 user.currentuser.group 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 550 user.currentuser.publickey 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 551 user.currentuser.username 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 552 user.currentuser.userslug 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 553 user.list 

```
The list of all users
Type: object[ ]
```
```
Username : string
UserSlug : string
Group : string
Sessions : object
base : int
hints : object
signed :
bitwidth :
```

Platinum API JSON RPC Reference Page 121 of 171

7. 0. 554 user.pincodeauthenticationenabled 

```
Allow authenticating users with pin code
Type: bool
```
7. 0. 555 user.poweruser.activesessioncount 

```
Description is missing!!!
```
```
Type: int
```
7. 0. 556 user.poweruser.enabled 

```
Description is missing!!!
```
```
Type: bool
```
7. 0. 557 user.poweruser.group 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 558 user.poweruser.publickey 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 559 user.poweruser.username 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 560 user.poweruser.userslug 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 561 user.resetadministratorchallenge 

```
Challenge for resetting the administrator user
Type: int
```
7. 0. 562 user.user.activesessioncount 


Page 122 of 171 JSON RPC Reference Platinum API

```
Description is missing!!!
```
```
Type: int
```
7. 0. 563 user.user.enabled 

```
Description is missing!!!
```
```
Type: bool
```
7. 0. 564 user.user.group 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 565 user.user.publickey 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 566 user.user.username 

```
Description is missing!!!
```
```
Type: string
```
7. 0. 567 user.user.userslug 

```
Description is missing!!!
```
```
Type: string
```
7. 1 Methods

```
Alphabetical list of all methods.
```
7. 0. 1 authenticate

```
[DEPRECATED] Authenticate using pin code
Parameters
```
```
code : int
```
```
Returns
```
```
string
```

Platinum API JSON RPC Reference Page 123 of 171

7. 0. 2 dmx.listchannels

```
Return a list of available channel names
Parameters
```
```
None
```
```
Returns
```
```
string[ ] List of channel names
```
7. 0. 3 dmx.listmodes

```
Return a list of all modes
Parameters
```
```
None
```
```
Returns
```
```
string[ ] List of mode object names
```
7. 0. 4 environment.fanspeed.mainboard.fan1.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 5 environment.getalarminfo

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
object[ ]
severity : string
timestamp : string
source : string
description : string
```
7. 0. 6 environment.getallcontrolblocks

```
Description is missing!!!
```

Page 124 of 171 JSON RPC Reference Platinum API

```
Parameters
```
```
None
```
```
Returns
```
```
string[ ]
```
7. 0. 7 environment.getcontrolblocks

```
Description is missing!!!
Parameters
```
```
type : enum
Actuator
Alarm
Controller
Filter
GenericBlock
Sensor
```
```
valuetype : enum
ADC
Altitude
Angle
Any
Average
Comparison
Constant
Contamination
Coordinate
Current
Delay
Difference
Disabled
Driver
Formula
Humidity
Interpolation
Light
Limit
LiquidPressure
Manual
Median
Mode
Noise
PID
PWM
Peltier
Power
Pressure
Pump
Range
Ratio
Resistance
Simulation
Speed
```

Platinum API JSON RPC Reference Page 125 of 171

```
State
Temperature
Threshold
Upgrader
Voltage
Volume
Waveform
Weighting
```
```
Returns
```
```
object[ ]
key : string
value : object
base : float
hints : object
bitwidth :
```
7. 0. 8 environment.image-tilt.pitch.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 9 environment.image-tilt.roll.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 10 environment.imageorientation.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 11 environment.mainboard.fan1.pid.processvariable.getoutput

```
Description is missing!!!
```

Page 126 of 171 JSON RPC Reference Platinum API

```
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 12 environment.mainboard.fan1.setpoint.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 13 environment.mainboard.fan2.pid.processvariable.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 14 environment.mainboard.fan2.setpoint.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 15 environment.pwm.mainboard.fan1.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```

Platinum API JSON RPC Reference Page 127 of 171

7. 0. 16 environment.pwm.mainboard.fan2.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 17 environment.state.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 18 environment.temperature.mainboard.cpu.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 19 environment.tilt.pitch.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
float
```
7. 0. 20 environment.tilt.roll.getoutput

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```

Page 128 of 171 JSON RPC Reference Platinum API

```
float
```
7. 0. 21 generatenewtoken

```
Request a new token for the currently authenticated user
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 22 getchallenge

```
Get the challenge for key-based authentication
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 23 introspect

```
Introspect the API for a specified object path
Parameters
```
```
object : string
```
```
recursive : bool
```
```
descriptions : bool
```
```
Returns
```
```
object
```
7. 0. 24 keydispatcher.postevent

```
Create and send a synthetic key event
Parameters
```
```
eventtype : enum The event type
PRESS
RELEASE
REPEAT
CLICKED
```
```
key : enum The key name
RC_SHUTTER_OPEN
RC_SHUTTER_CLOSE
RC_POWER_ON
```

Platinum API JSON RPC Reference Page 129 of 171

### RC_POWER_OFF

### RC_OSD

### RC_LCD

### RC_PATTERN

### RC_RGB

### RC_ZOOM_PLUS

### RC_ZOOM_MINUS

### RC_SHIFT_LEFT

### RC_SHIFT_UP

### RC_SHIFT_RIGHT

### RC_SHIFT_DOWN

### RC_FOCUS_PLUS

### RC_FOCUS_MINUS

### RC_MENU

### RC_DEFAULT

### RC_BACK

### RC_UP

### RC_LEFT

### RC_OK

### RC_RIGHT

### RC_DOWN

### RC_ADDRESS

### RC_INPUT

### RC_MACRO

### RC_1

### RC_2

### RC_3

### RC_4

### RC_5

### RC_6

### RC_7

### RC_8

### RC_9

### RC_0

### RC_ASTERISK

### RC_NUMBER

### KP_LEFT

### KP_UP

### KP_OK

### KP_RIGHT

### KP_DOWN

### KP_MENU

### KP_POWER

### KP_BACK

### KP_OSD

### KP_LENS

### KP_PATTERN

### KP_SHUTTER

### KP_INPUT

### KP_STANDBY

### TP_TOUCH

### AP_POWER_OFF

```
Returns
```
```
None
```

Page 130 of 171 JSON RPC Reference Platinum API

7. 0. 25 led.activity

```
Activates the LEDS when enabled and restarts the LED timeout counter
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 26 led.list

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
string[ ]
```
7. 0. 27 login

```
Description is missing!!!
Parameters
```
```
Returns
```
7. 0. 28 logout

```
De-authenticate
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 29 network.list

```
List of logical device id, e.g: 'wired1', 'wifi1'
Parameters
```
```
None
```
```
Returns
```
```
string[ ] List of device names
```

Platinum API JSON RPC Reference Page 131 of 171

7. 0. 30 notification.caution.list

```
Retrieve all active notifications for the given severity
Parameters
```
```
None
```
```
Returns
```
```
object[ ]
severity : enum
INFO
CAUTION
WARNING
ERROR
id : string
code : string
timestamp : string
message : string
timeout : string
visibility : string
doc : string
actions : enum[ ]
NONE
OK
CANCEL
YES
NO
SUPPRESS
```
7. 0. 31 notification.dismiss

```
Dismiss the notification with the specified id
Parameters
```
```
id : string The ID of the notification to dismiss
```
```
response : enum The reason or response for dismissing the notification
NONE
OK
CANCEL
YES
NO
SUPPRESS
```
```
Returns
```
```
None
```
7. 0. 32 notification.error.list

```
Retrieve all active notifications for the given severity
Parameters
```
```
None
```

Page 132 of 171 JSON RPC Reference Platinum API

```
Returns
```
```
object[ ]
severity : enum
INFO
CAUTION
WARNING
ERROR
id : string
code : string
timestamp : string
message : string
timeout : string
visibility : string
doc : string
actions : enum[ ]
NONE
OK
CANCEL
YES
NO
SUPPRESS
```
7. 0. 33 notification.info.list

```
Retrieve all active notifications for the given severity
Parameters
```
```
None
```
```
Returns
```
```
object[ ]
severity : enum
INFO
CAUTION
WARNING
ERROR
id : string
code : string
timestamp : string
message : string
timeout : string
visibility : string
doc : string
actions : enum[ ]
NONE
OK
CANCEL
YES
NO
SUPPRESS
```
7. 0. 34 notification.list


Platinum API JSON RPC Reference Page 133 of 171

```
List all active notifications
Parameters
```
```
None
```
```
Returns
```
```
object[ ]
severity : enum
INFO
CAUTION
WARNING
ERROR
id : string
code : string
timestamp : string
arguments : string[ ]
message : string
timeout : string
visibility : string
doc : string
actions : enum[ ]
NONE
OK
CANCEL
YES
NO
SUPPRESS
messageTemplate : string
```
7. 0. 35 notification.listsuppressed

```
Get a list of suppressed notification codes
Parameters
```
```
None
```
```
Returns
```
```
string[ ]
```
7. 0. 36 notification.log

```
List received notifications
Parameters
```
```
minimumseverity : enum The minimum severity level to include
INFO
CAUTION
WARNING
ERROR
```
```
start : int Start at this index
```
```
count : int Return this many notifications
```

Page 134 of 171 JSON RPC Reference Platinum API

```
Returns
```
```
object[ ] A list of notifications that matches the criteria
severity : enum
INFO
CAUTION
WARNING
ERROR
id : string
code : string
timestamp : string
arguments : string[ ]
message : string
timeout : string
visibility : string
doc : string
actions : enum[ ]
NONE
OK
CANCEL
YES
NO
SUPPRESS
messageTemplate : string
```
7. 0. 37 notification.suppress

```
Add a notification code to suppress (log but do not show on the LCD/OSD)
Parameters
```
```
code : string
```
```
Returns
```
```
None
```
7. 0. 38 notification.unsuppress

```
No longer suppress a certain notification code
Parameters
```
```
code : string
```
```
Returns
```
```
None
```
7. 0. 39 notification.unsuppressall

```
No longer suppress any notification codes
Parameters
```
```
None
```
```
Returns
```

Platinum API JSON RPC Reference Page 135 of 171

```
None
```
7. 0. 40 notification.warning.list

```
Retrieve all active notifications for the given severity
Parameters
```
```
None
```
```
Returns
```
```
object[ ]
severity : enum
INFO
CAUTION
WARNING
ERROR
id : string
code : string
timestamp : string
message : string
timeout : string
visibility : string
doc : string
actions : enum[ ]
NONE
OK
CANCEL
YES
NO
SUPPRESS
```
7. 0. 41 remotecontrol.listsensors

```
Return a list of all the object names of the IR sensors
Parameters
```
```
None
```
```
Returns
```
```
string[ ] List of IR sensors object names
```
7. 0. 42 scheduler.create

```
Create a new action for scheduler.
Parameters
```
```
name : string
```
```
Returns
```
```
string
```

Page 136 of 171 JSON RPC Reference Platinum API

7. 0. 43 statistics.laser plate 1 bank 1 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 44 statistics.laser plate 1 bank 1 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 45 statistics.laser plate 1 bank 2 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 46 statistics.laser plate 1 bank 2 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
```

Platinum API JSON RPC Reference Page 137 of 171

```
percent
```
7. 0. 47 statistics.laser plate 1 bank 3 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 48 statistics.laser plate 1 bank 3 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 49 statistics.laser plate 2 bank 1 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 50 statistics.laser plate 2 bank 1 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
```

Page 138 of 171 JSON RPC Reference Platinum API

```
seconds
number
percent
```
7. 0. 51 statistics.laser plate 2 bank 2 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 52 statistics.laser plate 2 bank 2 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 53 statistics.laser plate 2 bank 3 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 54 statistics.laser plate 2 bank 3 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
```

Platinum API JSON RPC Reference Page 139 of 171

```
hours
minutes
seconds
number
percent
```
7. 0. 55 statistics.laser plate 3 bank 1 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 56 statistics.laser plate 3 bank 1 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 57 statistics.laser plate 3 bank 2 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 58 statistics.laser plate 3 bank 2 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```

Page 140 of 171 JSON RPC Reference Platinum API

```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 59 statistics.laser plate 3 bank 3 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 60 statistics.laser plate 3 bank 3 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 61 statistics.laser plate 4 bank 1 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 62 statistics.laser plate 4 bank 1 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```

Platinum API JSON RPC Reference Page 141 of 171

```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 63 statistics.laser plate 4 bank 2 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 64 statistics.laser plate 4 bank 2 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 65 statistics.laser plate 4 bank 3 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 66 statistics.laser plate 4 bank 3 runtime.getunit

```
Unit of measurements
Parameters
```

Page 142 of 171 JSON RPC Reference Platinum API

```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 67 statistics.laser plate 5 bank 1 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 68 statistics.laser plate 5 bank 1 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 69 statistics.laser plate 5 bank 2 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 70 statistics.laser plate 5 bank 2 runtime.getunit


Platinum API JSON RPC Reference Page 143 of 171

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 71 statistics.laser plate 5 bank 3 runtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 72 statistics.laser plate 5 bank 3 runtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 73 statistics.laserruntime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```

Page 144 of 171 JSON RPC Reference Platinum API

7. 0. 74 statistics.laserruntime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 75 statistics.listcounters

```
List all counter names
Parameters
```
```
None
```
```
Returns
```
```
object[ ]
name : string
value : object
base : int
hints : object
signed :
bitwidth :
unit : enum
none
hours
minutes
seconds
number
percent
```
7. 0. 76 statistics.projectorruntime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 77 statistics.projectorruntime.getunit


Platinum API JSON RPC Reference Page 145 of 171

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 78 statistics.systemtime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```
7. 0. 79 statistics.systemtime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 80 statistics.uptime.getname

```
Name of the counter
Parameters
```
```
None
```
```
Returns
```
```
string
```

Page 146 of 171 JSON RPC Reference Platinum API

7. 0. 81 statistics.uptime.getunit

```
Unit of measurements
Parameters
```
```
None
```
```
Returns
```
```
enum
none
hours
minutes
seconds
number
percent
```
7. 0. 82 system.activity

```
Signal user activity (resets timeout countdown timers)
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 83 system.boards.getboardlist

```
Retrieve list of detected boards
Parameters
```
```
None
```
```
Returns
```
```
string[ ]
```
7. 0. 84 system.boards.getmissingboardlist

```
Retrieve list of missing boards
Parameters
```
```
None
```
```
Returns
```
```
string[ ]
```
7. 0. 85 system.date.getlocaldate

```
Returns the system date as local time.
```

Platinum API JSON RPC Reference Page 147 of 171

```
Parameters
```
```
None
```
```
Returns
```
```
object
year : object
base : int
hints : object
signed :
bitwidth :
month : object
base : int
hints : object
signed :
bitwidth :
day : object
base : int
hints : object
signed :
bitwidth :
hour : object
base : int
hints : object
signed :
bitwidth :
minute : object
base : int
hints : object
signed :
bitwidth :
second : object
base : int
hints : object
signed :
bitwidth :
```
7. 0. 86 system.date.getsystemdate

```
Returns the system date as UTC time.
Parameters
```
```
None
```
```
Returns
```
```
object
year : object
base : int
hints : object
signed :
bitwidth :
month : object
base : int
hints : object
signed :
bitwidth :
day : object
base : int
```

Page 148 of 171 JSON RPC Reference Platinum API

```
hints : object
signed :
bitwidth :
hour : object
base : int
hints : object
signed :
bitwidth :
minute : object
base : int
hints : object
signed :
bitwidth :
second : object
base : int
hints : object
signed :
bitwidth :
```
7. 0. 87 system.getidentification

```
Description is missing!!!
Parameters
```
```
identification : string
```
```
Returns
```
```
string
```
7. 0. 88 system.getidentifications

```
Description is missing!!!
Parameters
```
```
None
```
```
Returns
```
```
object[ ]
key : string
value : string
```
7. 0. 89 system.getsystemdate

```
Description is missing!!!
Parameters
```
```
Returns
```
7. 0. 90 system.gotoeco

```
Set the device in the eco state
```

Platinum API JSON RPC Reference Page 149 of 171

```
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 91 system.gotoready

```
Set the device from standby state to ready state
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 92 system.license.file.saveregistrationtousb

```
Save registration file to usb memory device
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 93 system.license.file.uploadfromusb

```
Upload license from usb memory device
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 94 system.listresetdomains

```
Returns the list of available reset domains
Parameters
```
```
None
```
```
Returns
```
```
enum[ ]
Dmx
Environment
Gpio
Gsm
```

Page 150 of 171 JSON RPC Reference Platinum API

```
Illumination
ImageBlend
ImageCapture
ImageConnector
ImageConvergence
ImageDisplay
ImageFeatures
ImageOrientation
ImageRealColor
ImageResolution
ImageSource
ImageStereo
ImageTestPattern
ImageTiltedBrightness
ImageUniformity
ImageWarp
LightMeasurement
LightSteering
LinkedServices
Macro
MediaPlayer
Network
Optics
Peripheral
PJLink
Profiles
Scheduler
Screen
Snmp
System
Time
User
UserInterface
```
7. 0. 95 system.poweroff

```
Power off the unit
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 96 system.poweron

```
Power on the unit
Parameters
```
```
None
```
```
Returns
```
```
None
```

Platinum API JSON RPC Reference Page 151 of 171

7. 0. 97 system.reset

```
Asynchronously starts reset of selected domains. The completion of the domains are signalled by one ore more 'Performed'-
signals. Subsequent calls to 'ResetAll' or 'Reset' will fail until all domains have completed.
Parameters
```
```
domains : enum[ ]
Dmx
Environment
Gpio
Gsm
Illumination
ImageBlend
ImageCapture
ImageConnector
ImageConvergence
ImageDisplay
ImageFeatures
ImageOrientation
ImageRealColor
ImageResolution
ImageSource
ImageStereo
ImageTestPattern
ImageTiltedBrightness
ImageUniformity
ImageWarp
LightMeasurement
LightSteering
LinkedServices
Macro
MediaPlayer
Network
Optics
Peripheral
PJLink
Profiles
Scheduler
Screen
Snmp
System
Time
User
UserInterface
```
```
Returns
```
```
None
```
7. 0. 98 system.resetall

```
Asynchronously starts reset of all domains. The completion of the domains are signalled by one ore more 'Performed'-signals.
Subsequent calls to 'ResetAll' or 'Reset' will fail until all domains have completed.
Parameters
```
```
None
```

Page 152 of 171 JSON RPC Reference Platinum API

```
Returns
```
```
enum[ ] The list of the actual domains that are going to be reset
Dmx
Environment
Gpio
Gsm
Illumination
ImageBlend
ImageCapture
ImageConnector
ImageConvergence
ImageDisplay
ImageFeatures
ImageOrientation
ImageRealColor
ImageResolution
ImageSource
ImageStereo
ImageTestPattern
ImageTiltedBrightness
ImageUniformity
ImageWarp
LightMeasurement
LightSteering
LinkedServices
Macro
MediaPlayer
Network
Optics
Peripheral
PJLink
Profiles
Scheduler
Screen
Snmp
System
Time
User
UserInterface
```
7. 0. 99 ui.leds.setstate

```
Set the state and color of the key LEDs
Parameters
```
```
key : enum
Back
Down
Input
Left
Lens
Menu
Ok
OsdOff
Pattern
```

Platinum API JSON RPC Reference Page 153 of 171

```
Right
Up
```
```
state : enum
Off
White
Blue
```
```
Returns
```
```
None
```
7. 0. 100 ui.settings.get

```
Get the value of the specified key
Parameters
```
```
key : string The name of the key
```
```
Returns
```
```
string The value of the key
```
7. 0. 101 ui.settings.getfonticons

```
Return a dictionary of icons for the specified category. Then icon is returned as a string containing the font set class name
and the icon class name.
Parameters
```
```
category : enum The icon category
Source
Connector
TestPattern
```
```
Returns
```
```
object[ ] A list of key/value pairs with all icons for the speciffied category
key : string
value : string
```
7. 0. 102 ui.settings.geticons

```
Return a dictionary of icons for the specified category. The icon is return as a SVG sprite name.
Parameters
```
```
category : enum The icon category
Source
Connector
TestPattern
```
```
Returns
```
```
object[ ] A list of key/value pairs with all icons for the specified category
key : string
value : string
```

Page 154 of 171 JSON RPC Reference Platinum API

7. 0. 103 ui.settings.keys

```
Return a list of all the keys
Parameters
```
```
None
```
```
Returns
```
```
string[ ] The list of all the keys
```
7. 0. 104 ui.settings.list

```
Return a list of key/value pairs of all the settings
Parameters
```
```
None
```
```
Returns
```
```
object[ ] A list of key/value pairs of all the settings
key : string
value : string
```
7. 0. 105 ui.settings.remove

```
Remove the specfied key and value
Parameters
```
```
key : string The key to remove
```
```
Returns
```
```
None
```
7. 0. 106 ui.settings.set

```
Set the key to the specified value
Parameters
```
```
key : string The name of the key
```
```
value : string The value of the key
```
```
Returns
```
```
None
```
7. 0. 107 ui.togglelensmenu

```
Toggle lens menu on or off
Parameters
```

Platinum API JSON RPC Reference Page 155 of 171

```
None
```
```
Returns
```
```
None
```
7. 0. 108 ui.togglemenu

```
Toggle menu on/off
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 109 ui.toggleosd

```
Toggle on screen display on or off
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 110 ui.togglepatternmenu

```
Toggle the pattern menu on or off
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 111 ui.togglesourcemenu

```
Toggle the source menu on or off
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 112 ui.togglestealthmode

```
This method is depreciated.
```

Page 156 of 171 JSON RPC Reference Platinum API

```
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 113 ui.touchscreen.tapped

```
Called from touchpanel when the touchpanel is in Test mode
Parameters
```
```
x : int
```
```
y : int Vertical position of touch event
```
```
Returns
```
```
None
```
7. 0. 114 user.admin.changegroup

```
Change the user group
Parameters
```
```
newgroup : string
```
```
Returns
```
```
None
```
7. 0. 115 user.admin.changepassword

```
Change the password
Parameters
```
```
newpassword : string
```
```
Returns
```
```
None
```
7. 0. 116 user.admin.changepincode

```
Change the 6-digit PIN code
Parameters
```
```
newpincode : int
```
```
Returns
```
```
None
```

Platinum API JSON RPC Reference Page 157 of 171

7. 0. 117 user.admin.changepublickey

```
Change the public key
Parameters
```
```
newpublickey : string
```
```
Returns
```
```
None
```
7. 0. 118 user.admin.changeusername

```
Change the username
Parameters
```
```
newusername : string
```
```
Returns
```
```
string
```
7. 0. 119 user.admin.disable

```
Disable the user
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 120 user.admin.enable

```
Enable the user
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 121 user.admin.invalidatetokens

```
Invalidate all tokens
Parameters
```
```
None
```
```
Returns
```

Page 158 of 171 JSON RPC Reference Platinum API

```
None
```
7. 0. 122 user.admin.logouteverywhere

```
Invalidate all tokens and log out of all active sessions
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 123 user.admin.removepassword

```
Remove the password
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 124 user.admin.removepincode

```
Remove the 6-digit PIN code
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 125 user.currentuser.changegroup

```
Change the user group
Parameters
```
```
newgroup : string
```
```
Returns
```
```
None
```
7. 0. 126 user.currentuser.changepassword

```
Change the password
Parameters
```
```
newpassword : string
```

Platinum API JSON RPC Reference Page 159 of 171

```
Returns
```
```
None
```
7. 0. 127 user.currentuser.changepincode

```
Change the 6-digit PIN code
Parameters
```
```
newpincode : int
```
```
Returns
```
```
None
```
7. 0. 128 user.currentuser.changepublickey

```
Change the public key
Parameters
```
```
newpublickey : string
```
```
Returns
```
```
None
```
7. 0. 129 user.currentuser.changeusername

```
Change the username
Parameters
```
```
newusername : string
```
```
Returns
```
```
string
```
7. 0. 130 user.currentuser.disable

```
Disable the user
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 131 user.currentuser.enable

```
Enable the user
```

Page 160 of 171 JSON RPC Reference Platinum API

```
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 132 user.currentuser.invalidatetokens

```
Invalidate all tokens
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 133 user.currentuser.logouteverywhere

```
Invalidate all tokens and log out of all active sessions
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 134 user.currentuser.removepassword

```
Remove the password
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 135 user.currentuser.removepincode

```
Remove the 6-digit PIN code
Parameters
```
```
None
```
```
Returns
```
```
None
```

Platinum API JSON RPC Reference Page 161 of 171

7. 0. 136 user.poweruser.changegroup

```
Change the user group
Parameters
```
```
newgroup : string
```
```
Returns
```
```
None
```
7. 0. 137 user.poweruser.changepassword

```
Change the password
Parameters
```
```
newpassword : string
```
```
Returns
```
```
None
```
7. 0. 138 user.poweruser.changepincode

```
Change the 6-digit PIN code
Parameters
```
```
newpincode : int
```
```
Returns
```
```
None
```
7. 0. 139 user.poweruser.changepublickey

```
Change the public key
Parameters
```
```
newpublickey : string
```
```
Returns
```
```
None
```
7. 0. 140 user.poweruser.changeusername

```
Change the username
Parameters
```
```
newusername : string
```
```
Returns
```

Page 162 of 171 JSON RPC Reference Platinum API

```
string
```
7. 0. 141 user.poweruser.disable

```
Disable the user
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 142 user.poweruser.enable

```
Enable the user
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 143 user.poweruser.invalidatetokens

```
Invalidate all tokens
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 144 user.poweruser.logouteverywhere

```
Invalidate all tokens and log out of all active sessions
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 145 user.poweruser.removepassword

```
Remove the password
Parameters
```

Platinum API JSON RPC Reference Page 163 of 171

```
None
```
```
Returns
```
```
None
```
7. 0. 146 user.poweruser.removepincode

```
Remove the 6-digit PIN code
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 147 user.resetadministrator

```
Reset the administrator account using the response provided by barco
Parameters
```
```
response : int
```
```
Returns
```
```
None
```
7. 0. 148 user.user.changegroup

```
Change the user group
Parameters
```
```
newgroup : string
```
```
Returns
```
```
None
```
7. 0. 149 user.user.changepassword

```
Change the password
Parameters
```
```
newpassword : string
```
```
Returns
```
```
None
```
7. 0. 150 user.user.changepincode

```
Change the 6-digit PIN code
```

Page 164 of 171 JSON RPC Reference Platinum API

```
Parameters
```
```
newpincode : int
```
```
Returns
```
```
None
```
7. 0. 151 user.user.changepublickey

```
Change the public key
Parameters
```
```
newpublickey : string
```
```
Returns
```
```
None
```
7. 0. 152 user.user.changeusername

```
Change the username
Parameters
```
```
newusername : string
```
```
Returns
```
```
string
```
7. 0. 153 user.user.disable

```
Disable the user
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 154 user.user.enable

```
Enable the user
Parameters
```
```
None
```
```
Returns
```
```
None
```

Platinum API JSON RPC Reference Page 165 of 171

7. 0. 155 user.user.invalidatetokens

```
Invalidate all tokens
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 156 user.user.logouteverywhere

```
Invalidate all tokens and log out of all active sessions
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 157 user.user.removepassword

```
Remove the password
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 0. 158 user.user.removepincode

```
Remove the 6-digit PIN code
Parameters
```
```
None
```
```
Returns
```
```
None
```
7. 1 Signals

```
Alphabetical list of all signals.
```
7. 0. 1 dmx.shutdownrequest


Page 166 of 171 JSON RPC Reference Platinum API

```
Description is missing!!!
Parameters
```
```
None
```
7. 0. 2 keydispatcher.keyevent

```
Raised when the user has pressed a physical key on an input device.
Parameters
```
```
key : string The logical key name that was pressed
```
```
type : enum Type of event: press, repeat, release, clicked.
PRESS
RELEASE
REPEAT
CLICKED
```
```
source : string The source of the event, e.g remote control or keypad
```
7. 0. 3 loggedout

```
Will be raised whenever the user is logged out
Parameters
```
```
reason : enum
Disable
InternalError
LogoutEverywhere
Reauthentication
Reboot
Remove
Request
Reset
Restore
```
7. 0. 4 modelupdated

```
Signals whenever functionality for an object appears or disappears
Parameters
```
```
object : string The object name (JSON-RPC dot-notation)
```
```
newobject : bool True if functionality is added and false if functionality is removed
```
```
reason : string The reason for this ModelUpdated signal, either an object was added, removed or changed.
```
```
accesslevel : enum Minimum access level for this object
UNAUTHENTICATED_END_USER
END_USER
POWER_USER
ADMINISTRATOR
SERVICE_PARTNER
MANUFACTURING
```

Platinum API JSON RPC Reference Page 167 of 171

### DEVELOPMENT

### INACCESSIBLE

7. 0. 5 network.added

```
Raised when a new device has been added
Parameters
```
```
id : string The logical device id of the new device, e.g: 'wifi1
```
7. 0. 6 network.removed

```
Raised when a device has been removed
Parameters
```
```
id : string The logical device id of the device that was removed, e.g: 'wired2'
```
7. 0. 7 notification.caution.dismissed

```
Signal the dismissal of a notification of the given severity level
Parameters
```
```
None
```
7. 0. 8 notification.caution.emitted

```
Signal the emission of a new notification of the given severity level
Parameters
```
```
None
```
7. 0. 9 notification.dismissed

```
Description is missing!!!
Parameters
```
```
id : string The ID of the dismissed notification
```
```
response : enum The reason or response for dismissing the notification
NONE
OK
CANCEL
YES
NO
SUPPRESS
```
7. 0. 10 notification.emitted


Page 168 of 171 JSON RPC Reference Platinum API

```
Description is missing!!!
Parameters
```
```
notification : object The new notification
severity : enum
INFO
CAUTION
WARNING
ERROR
id : string
code : string
timestamp : string
arguments : string[ ]
message : string
timeout : string
visibility : string
doc : string
actions : enum[ ]
NONE
OK
CANCEL
YES
NO
SUPPRESS
messageTemplate : string
```
7. 0. 11 notification.error.dismissed

```
Signal the dismissal of a notification of the given severity level
Parameters
```
```
None
```
7. 0. 12 notification.error.emitted

```
Signal the emission of a new notification of the given severity level
Parameters
```
```
None
```
7. 0. 13 notification.info.dismissed

```
Signal the dismissal of a notification of the given severity level
Parameters
```
```
None
```
7. 0. 14 notification.info.emitted

```
Signal the emission of a new notification of the given severity level
```

Platinum API JSON RPC Reference Page 169 of 171

```
Parameters
```
```
None
```
7. 0. 15 notification.warning.dismissed

```
Signal the dismissal of a notification of the given severity level
Parameters
```
```
None
```
7. 0. 16 notification.warning.emitted

```
Signal the emission of a new notification of the given severity level
Parameters
```
```
None
```
7. 0. 17 system.date.systemdatechanged

```
Signals if date/time has changed.
Parameters
```
```
None
```
7. 0. 18 system.identificationchanged

```
Will be raised whenever an identification is changed
Parameters
```
```
identification : string
```
7. 0. 19 system.license.licensechanged

```
Description is missing!!!
Parameters
```
```
None
```
7. 0. 20 system.performed

```
Emitted when one or more domains have completed resetting. This signal might be emitted several times, every time with one
or more domains, until all requested domains are done resetting. 'All domains' in this context is either the list of domains
supplied to a call to 'Reset' or the list of domains returned from 'ResetAll'.
Parameters
```
```
domains : enum[ ]
Dmx
```

Page 170 of 171 JSON RPC Reference Platinum API

```
Environment
Gpio
Gsm
Illumination
ImageBlend
ImageCapture
ImageConnector
ImageConvergence
ImageDisplay
ImageFeatures
ImageOrientation
ImageRealColor
ImageResolution
ImageSource
ImageStereo
ImageTestPattern
ImageTiltedBrightness
ImageUniformity
ImageWarp
LightMeasurement
LightSteering
LinkedServices
Macro
MediaPlayer
Network
Optics
Peripheral
PJLink
Profiles
Scheduler
Screen
Snmp
System
Time
User
UserInterface
```
7. 0. 21 ui.settings.added

```
Fired when a new key/value pair was added
Parameters
```
```
key : string The key name
```
```
value : string The key value
```
7. 0. 22 ui.settings.changed

```
Fired when a key has an updated value
Parameters
```
```
key : string The key name
```
```
value : string The value of the key
```

Platinum API JSON RPC Reference Page 171 of 171

7. 0. 23 ui.settings.removed

```
Fired when a key was removed
Parameters
```
```
key : string The key name
```
