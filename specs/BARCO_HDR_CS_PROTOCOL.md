# Barco Pulse Protocol Specification

**Protocol Version:** JSON-RPC 2.0
**Transport:** TCP Port 9090
**Tested Models:** Barco HDR CS
**Last Updated:** October 18, 2025

## Protocol Overview

Barco Pulse projectors use a **hybrid HTTP/0.9-style protocol** that combines modern HTTP requests with simplified responses:

- **Request Format:** HTTP POST with JSON-RPC 2.0 payload (standard HTTP/1.1)
- **Response Format:** Raw JSON **without HTTP response headers** (HTTP/0.9-like behavior)


This is unusual because:
1. Modern HTTP servers typically send full HTTP responses with status line and headers
2. The projector accepts HTTP/1.1 POST requests but responds like HTTP/0.9 (raw content only)
3. Standard HTTP libraries (like `aiohttp` or `urllib`) may fail because they expect HTTP response headers

## Protocol Details

### Connection

- **Protocol:** TCP
- **Port:** 9090 (default)
- **Encoding:** UTF-8
- **Format:** HTTP POST with JSON-RPC 2.0 payload

### Request Format

Requests must be sent as HTTP/1.1 POST requests with the following structure:

```http
POST / HTTP/1.1
Host: <projector-ip>
Content-Type: application/json
Content-Length: <payload-length>

<json-rpc-payload>
```

**JSON-RPC 2.0 Payload Structure:**
```json
{
  "jsonrpc": "2.0",
  "method": "<method-name>",
  "params": {<parameters>},
  "id": <request-id>
}
```

**Example Request:**
```http
POST / HTTP/1.1
Host: 192.168.1.100
Content-Type: application/json
Content-Length: 93

{"jsonrpc":"2.0","method":"property.get","params":{"property":"system.serialnumber"},"id":1}
```

### Response Format

**Critical:** Responses contain **only raw JSON** without HTTP status line or headers (HTTP/0.9 behavior).

**JSON-RPC 2.0 Response Structure:**
```json
{
  "jsonrpc": "2.0",
  "id": <request-id>,
  "result": <result-value>
}
```

**Error Response:**
```json
{
  "jsonrpc": "2.0",
  "id": <request-id>,
  "error": {
    "code": <error-code>,
    "message": "<error-message>"
  }
}
```

**Example Response:**
```json
{"jsonrpc":"2.0","id":1,"result":"2590381267"}
```

## Testing the Protocol

### Using curl

The `--http0.9` flag is required to handle responses without HTTP headers:

```bash
curl --http0.9 -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"property.get","params":{"property":"system.serialnumber"},"id":1}' \
  http://<projector-ip>:9090
```

### Using Raw TCP Sockets

Since standard HTTP libraries expect HTTP response headers, raw TCP sockets are recommended:

**Python Example (asyncio):**
```python
import asyncio
import json

async def send_jsonrpc_request(host, method, params=None):
    # Connect to projector
    reader, writer = await asyncio.open_connection(host, 9090)
    
    # Build JSON-RPC request
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": 1
    }
    json_payload = json.dumps(request)
    
    # Build HTTP POST request
    http_request = (
        f"POST / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(json_payload)}\r\n"
        f"\r\n"
        f"{json_payload}"
    )
    
    # Send request
    writer.write(http_request.encode())
    await writer.drain()
    
    # Read raw JSON response (no HTTP headers)
    response_data = await reader.read(8192)
    response = json.loads(response_data.decode())
    
    # Cleanup
    writer.close()
    await writer.wait_closed()
    
    return response
```

## Common API Methods

### Property Access

**Get Property:**
```json
{
  "jsonrpc": "2.0",
  "method": "property.get",
  "params": {"property": "system.serialnumber"},
  "id": 1
}
```

**Set Property:**
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

### Power Control

**Power On:**
```json
{
  "jsonrpc": "2.0",
  "method": "system.poweron",
  "params": {},
  "id": 3
}
```

**Power Off:**
```json
{
  "jsonrpc": "2.0",
  "method": "system.poweroff",
  "params": {},
  "id": 4
}
```

### API Discovery

**Introspect:**
```json
{
  "jsonrpc": "2.0",
  "method": "introspect",
  "params": {"object": "", "recursive": true},
  "id": 5
}
```

Returns the complete API structure including all available methods and properties.

## Authentication

Some methods may require authentication:

```json
{
  "jsonrpc": "2.0",
  "method": "authenticate",
  "params": {"code": "12345"},
  "id": 6
}
```

The authentication code is typically a 5-digit PIN configured on the projector.

## Implementation Considerations

### Protocol Compatibility

- **Standard HTTP Libraries:** Not recommended (expect HTTP response headers)
- **Raw TCP Sockets:** Recommended approach for maximum control
- **Connection Management:** Each request typically uses a new connection (stateless)

### Error Handling

1. **TCP Connection Errors:** Network issues, projector offline
2. **JSON-RPC Errors:** Invalid method, missing parameters, authentication required
3. **Timeout:** No response within expected timeframe (consider 5-10 second timeout)

### Best Practices

1. **Always close connections** after receiving response
2. **Handle JSON parsing errors** gracefully
3. **Implement retry logic** for transient network errors
4. **Validate JSON-RPC responses** (check for `error` field)
5. **Use unique request IDs** to correlate responses (though single request/response pattern is typical)

## Model Variations

**Note:** This protocol description is based on testing with the Barco HDR CS model. Other Barco Pulse projector models may use:

- Standard HTTP with full response headers
- Pure TCP with newline-delimited JSON
- WebSocket-based communication

Always test protocol behavior with your specific projector model.

## Related Documentation

- **Barco Pulse API Reference:** See `pulse-api-docs.md` for complete method and property documentation
- **HDR CS State Properties:** See `HDR_CS_STATE_DEPENDENT_PROPERTIES.md` for state-dependent behavior
- **JSON-RPC 2.0 Specification:** https://www.jsonrpc.org/specification
- **HTTP/0.9 Reference:** Simple-Response format (body only, no headers)

## Appendix: Troubleshooting

### Symptom: Connection succeeds but no response

**Cause:** Not sending HTTP POST headers, or using standard HTTP library that can't parse headerless response

**Solution:** Use raw TCP sockets with HTTP POST request format

### Symptom: `400 Bad Request` or `Expected HTTP/...` error

**Cause:** HTTP library (e.g., aiohttp) trying to parse response as HTTP but receiving raw JSON

**Solution:** Switch to raw TCP socket implementation

### Symptom: JSON parsing error

**Cause:** Partial response read, or response contains HTTP headers you're not stripping

**Solution:** 
- Ensure reading enough bytes (4096-8192 typical)
- Verify response is pure JSON (no HTTP headers)
- Check for complete JSON objects (balanced braces)

### Symptom: Timeout on all requests

**Possible Causes:**
1. Wrong port (verify 9090)
2. Projector requires authentication first
3. Network firewall blocking connection
4. Projector in deep standby mode (may need wake-on-LAN or physical power on)

**Debugging Steps:**
1. Test with `curl --http0.9` command
2. Verify TCP connection with `telnet <ip> 9090`
3. Try `introspect` method to validate basic connectivity
4. Check projector network settings and authentication requirements
