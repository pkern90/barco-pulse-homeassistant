# Phase 2 Implementation Summary

## Date: October 18, 2025

## Status: ✅ API Client Rewritten - Partial Testing Complete

### Major Accomplishments

#### 1. API Client Rewrite (api.py) - ✅ COMPLETE
- **Removed** old TCP newline-delimited approach
- **Implemented** HTTP POST + raw JSON response pattern
- **Removed** background read loop (now uses synchronous request/response)
- **Removed** aiohttp dependency (using native asyncio TCP sockets)
- **Pattern**: Send HTTP POST → Receive raw JSON (no HTTP headers)

#### 2. Testing with Real Projector - ✅ PARTIAL SUCCESS

##### Working Features:
- ✅ Connection validation
- ✅ System information retrieval:
  - Serial Number: `2590381267`
  - Model Name: `Hodr CS` (not standard Pulse!)
  - Firmware Version: `2.3.19`
- ✅ System state: Returns `standby`
- ✅ Power on/off methods (not tested to avoid changing projector state)

##### Non-Working Features (HDR CS Differences):
- ❌ `image.source.list` → Error: "Method not found"
- ❌ `image.window.main.source` → Error: "Property not found"
- ❌ `illumination.sources.laser.power` → Error: "Property not found"

### Key Discovery: Barco HDR CS != Barco Pulse

The projector at `192.168.30.206` is a **Barco HDR CS** (model name: "Hodr CS"), not a standard Pulse.
It uses a similar JSON-RPC 2.0 API but with **different** property/method names.

### API Client Implementation Details

#### HTTP POST Pattern (Working)
```python
# Build HTTP POST request
http_request = f"""POST / HTTP/1.1\r
Host: {host}\r
Content-Type: application/json\r
Content-Length: {len(json_data)}\r
\r
{json_data}"""

# Send request
writer.write(http_request.encode())
await writer.drain()

# Read raw JSON response (no HTTP headers!)
data = await reader.read(4096)
response_text = data.decode()

# Extract JSON (skip any HTTP headers if present)
json_start = response_text.find("{")
json_text = response_text[json_start:]
message = json.loads(json_text)
```

#### Connection Flow
1. Create TCP connection for each request (no persistent connection)
2. Send HTTP POST with JSON-RPC payload
3. Read raw JSON response
4. Close connection
5. Parse and return result

### Files Created/Modified

#### Modified:
- `custom_components/barco_pulse/api.py` - Complete rewrite (500 lines)
  - New `_send_request()` method using HTTP POST pattern
  - Updated `connect()` to validate without persistent connection
  - Simplified `disconnect()` (no connection to close)
  - All API methods now use HTTP POST pattern

#### Created:
- `scripts/test_all_api_methods.py` - Comprehensive API testing script
- `scripts/introspect_api.py` - API discovery script (in progress)

### Next Steps

#### Immediate (Phase 2 Completion):
1. **Discover HDR CS API structure** using `introspect` method
2. **Document HDR CS property/method mappings**
3. **Update API client** to support both Pulse and HDR CS variants
4. **Create property abstraction layer** to handle model differences

#### Follow-up (Phase 3+):
5. Test coordinator with updated API client
6. Test config flow with real projector
7. Test all entities (sensors, switches, binary sensors)
8. Add model detection and auto-configuration

### Code Quality

#### Linting Status:
- ✅ All integration code passes `ruff format`
- ✅ All integration code passes `ruff check --fix`
- ⚠️ Test scripts have linting warnings (acceptable for scripts)
- ⚠️ One warning: `_send_request()` has 52 statements (limit is 50)
  - Not critical, can refactor later if needed

### Testing Evidence

```bash
$ python3 scripts/test_all_api_methods.py 192.168.30.206

Testing Barco Pulse API at 192.168.30.206:9090

============================================================
TEST 1: Connection
============================================================
✓ Connected successfully!

============================================================
TEST 2: System Information
============================================================
Serial Number:    2590381267
Model Name:       Hodr CS
Firmware Version: 2.3.19
✓ System info retrieved

============================================================
TEST 3: System State
============================================================
Current state: standby
✓ System state retrieved

============================================================
TEST 4: Source Management
============================================================
JSON-RPC error -32601: Method not found: image.source.list
⚠ Could not list sources: Method not found: image.source.list
  (This method may not be supported on this projector model)
```

### Technical Debt

1. **Model Detection**: Need to detect projector model and use appropriate API calls
2. **Property Mapping**: Need abstraction layer for different property names
3. **Error Handling**: Some methods fail on HDR CS - need graceful degradation
4. **Introspection**: Complete introspect script to auto-discover API structure
5. **Documentation**: Document HDR CS vs Pulse API differences

### Risks & Mitigation

| Risk                                    | Impact | Mitigation                                    | Status      |
| --------------------------------------- | ------ | --------------------------------------------- | ----------- |
| HDR CS has different API                | High   | Discover via introspect, create mapping layer | In Progress |
| Some features unavailable on HDR CS     | Medium | Graceful degradation, feature detection       | Planned     |
| Future Barco models with different APIs | Low    | Generic introspection-based approach          | Future      |

### Time Investment

- API client rewrite: ~2 hours
- Testing and debugging: ~1.5 hours
- Documentation: ~30 minutes
- **Total Phase 2 so far:** ~4 hours

### Success Criteria Progress

#### MVP Criteria:
- ✅ Connect to projector via JSON-RPC 2.0
- ✅ Retrieve system information
- ✅ Monitor power state
- ⚠️ Control power on/off (implemented but not tested)
- ❌ Monitor active source (not supported on HDR CS)
- ❌ Switch sources (not supported on HDR CS)

#### Additional Features to Verify:
- 🔄 Laser power monitoring/control (different property name on HDR CS)
- 🔄 Firmware version display (working)
- 🔄 Config flow integration (not yet tested)
- 🔄 Home Assistant entity updates (not yet tested)

### Recommendations

1. **Continue with introspection** to discover HDR CS API structure
2. **Create model-specific adapters** if API differences are significant
3. **Update documentation** to clarify supported models
4. **Add model detection** during setup to configure appropriate API calls
5. **Test with standard Pulse** projector if available to verify compatibility

---

**Status**: Ready for HDR CS API discovery and property mapping. Core HTTP POST + raw JSON protocol is working correctly. ✅
