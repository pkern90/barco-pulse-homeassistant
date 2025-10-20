# Barco HDR CS Protocol Discovery - Summary

**Date:** October 18, 2025
**Test Projector:** Barco HDR CS at 192.168.30.206
**Serial Number:** 2590381267

## Issue Summary

The initial API client implementation used standard JSON-RPC 2.0 over TCP with newline-delimited messages. The TCP connection succeeded, but the projector never responded to requests, resulting in timeout errors.

## Root Cause

The Barco HDR CS projector uses a **hybrid HTTP/0.9-style protocol**:

- **Request Format:** HTTP POST with JSON-RPC 2.0 payload (standard HTTP/1.1)
- **Response Format:** Raw JSON **without HTTP response headers** (HTTP/0.9-like behavior)

This is unusual because:
1. Modern HTTP servers typically send full HTTP responses with status line and headers
2. The projector accepts HTTP/1.1 POST requests but responds like HTTP/0.9 (raw content only)
3. Standard HTTP libraries (like `aiohttp`) fail because they expect HTTP response headers

## Discovery Process

### 1. Initial Symptoms
```
✓ TCP connection to 192.168.30.206:9090 succeeds
✗ Requests timeout - no response received
✗ Background read loop receives no data
```

### 2. Working curl Command
The user discovered this works:
```bash
curl --http0.9 -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"property.get","params":{"property":"system.serialnumber"},"id":1}' \
  http://192.168.30.206:9090
```

The `--http0.9` flag was the critical clue!

### 3. Test Results

**HTTP with aiohttp (Failed):**
```python
async with session.post(url, json=request) as response:
    result = await response.json()
```
Error: `400, message='Expected HTTP/...'`

**HTTP POST via TCP Socket (Success):**
```python
# Send HTTP POST request
http_request = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {host}\r\n"
    f"Content-Type: application/json\r\n"
    f"Content-Length: {len(json_data)}\r\n"
    f"\r\n"
    f"{json_data}"
)
writer.write(http_request.encode())
await writer.drain()

# Read raw JSON response (no HTTP headers)
data = await reader.read(4096)
json_text = data.decode()
result = json.loads(json_text)
```

✅ **Response:** `{"jsonrpc":"2.0","id":1,"result":"2590381267"}`

## Solution

Use TCP sockets (`asyncio.open_connection`) to:
1. **Send:** HTTP POST request with proper headers + JSON-RPC payload
2. **Receive:** Raw JSON response (no HTTP header parsing)
3. **Parse:** JSON directly from socket data

## Implementation Requirements

### Updated API Client Pattern

```python
class BarcoPulseApiClient:
    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(
            self._host, self._port
        )

    async def _send_request(self, method: str, params: dict | None = None):
        # Generate JSON-RPC request
        request_id = self._next_id()
        json_payload = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        })

        # Build HTTP POST request
        http_request = (
            f"POST / HTTP/1.1\r\n"
            f"Host: {self._host}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(json_payload)}\r\n"
            f"\r\n"
            f"{json_payload}"
        )

        # Send request
        self._writer.write(http_request.encode())
        await self._writer.drain()

        # Read raw JSON response (no HTTP headers!)
        response_data = await self._reader.read(8192)
        response_json = json.loads(response_data.decode())

        # Handle JSON-RPC response
        if "error" in response_json:
            raise BarcoPulseCommandError(response_json["error"]["message"])

        return response_json.get("result")
```

### Key Changes from Original Plan

| Original Design                              | Updated Design                              |
| -------------------------------------------- | ------------------------------------------- |
| Pure TCP with newline-delimited JSON         | TCP socket with HTTP POST headers           |
| Background `_read_loop()` for async messages | Synchronous request/response per connection |
| Parse JSON from readline()                   | Parse JSON from raw socket read()           |
| Support notifications (no `id` field)        | Request/response only (always has `id`)     |

### Removed Features (for now)

- **Background read loop** - Not needed for synchronous request/response
- **Notification handling** - Unclear if HDR CS sends async notifications
- **Request queue** - Single request at a time is simpler
- **aiohttp dependency** - Can't use it due to HTTP/0.9 responses

## Testing

### Test Scripts Created

1. **`scripts/test_http09.py`** - Validates HTTP POST + raw JSON response
   ```bash
   python3 scripts/test_http09.py 192.168.30.206
   ```

2. **`scripts/test_raw_connection.py`** - Raw TCP test
3. **`scripts/test_projector_connection.py`** - High-level connection test
4. **`scripts/test_http_jsonrpc.py`** - Failed aiohttp attempt (kept for reference)

### Verified Working Commands

```python
# Get serial number
{"jsonrpc":"2.0","method":"property.get","params":{"property":"system.serialnumber"},"id":1}
→ {"jsonrpc":"2.0","id":1,"result":"2590381267"}

# Introspect (API discovery)
{"jsonrpc":"2.0","method":"introspect","params":{"object":"","recursive":true},"id":520}
→ Returns full API structure
```

## Configuration Notes

### Logger Configuration
Fixed in `config/configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.barco_pulse: debug  # Was: integration_blueprint
```

### Model Compatibility Considerations

- **Barco HDR CS:** Confirmed working with HTTP POST + raw JSON
- **Other Barco Pulse models:** May use different protocols
  - Standard TCP with newline-delimited JSON?
  - Full HTTP with proper response headers?

**Recommendation:** Consider adding protocol detection or configuration option if supporting multiple Barco projector models in the future.

## Next Steps

1. ✅ Update `plan.md` with protocol discovery findings
2. ⏭️ Rewrite `api.py` to use HTTP POST + raw JSON pattern
3. ⏭️ Test all API methods (power, properties, sources, etc.)
4. ⏭️ Update coordinator to use new API client
5. ⏭️ Test config flow with real projector

## Files Modified/Created

### Documentation
- ✅ `plan.md` - Updated Phase 2 with protocol details
- ✅ `BARCO_HDR_CS_PROTOCOL.md` - This document
- ✅ `config/configuration.yaml` - Fixed logger configuration

### Test Scripts
- ✅ `scripts/test_http09.py` - Working HTTP POST + raw JSON test
- ✅ `scripts/test_raw_connection.py` - Raw TCP test
- ✅ `scripts/test_projector_connection.py` - Connection test
- ✅ `scripts/test_auth_first.py` - Authentication test
- ✅ `scripts/test_http_jsonrpc.py` - Failed aiohttp test
- ✅ `scripts/README_MOCK.md` - Mock server docs (not needed for real projector)
- ✅ `scripts/mock_projector.py` - Mock server (TCP-based, won't work for HDR CS)

### To Be Modified
- ⏭️ `custom_components/barco_pulse/api.py` - Rewrite for HTTP POST + raw JSON
- ⏭️ `custom_components/barco_pulse/manifest.json` - Remove `aiohttp` dependency if added

## References

- Barco Pulse API Documentation: `pulse-api-docs.md`
- HTTP/0.9 Spec: Simple-Response format (no status line or headers)
- curl `--http0.9` flag: Allows HTTP/0.9 servers (response without headers)
