#!/usr/bin/env python3
"""Test HTTP/0.9-style JSON-RPC communication with Barco projector."""

import asyncio
import json


async def test_http09_jsonrpc(host: str, port: int = 9090):
    """Test HTTP/0.9-style communication (POST without expecting HTTP response headers)."""
    print(f"Testing at {host}:{port}\n")

    # Test 1: Get serial number
    print("Test 1: Getting system.serialnumber")
    request = {
        "jsonrpc": "2.0",
        "method": "property.get",
        "params": {"property": "system.serialnumber"},
        "id": 1,
    }
    print(f"Request: {json.dumps(request)}\n")

    try:
        reader, writer = await asyncio.open_connection(host, port)

        # Send HTTP POST request
        json_data = json.dumps(request)
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

        # Read response (might be HTTP/0.9 - just JSON without headers)
        data = await reader.read(4096)
        response_text = data.decode()

        print(f"Raw response:\n{response_text}\n")

        # Try to extract JSON (skip HTTP headers if present)
        json_start = response_text.find("{")
        if json_start >= 0:
            json_text = response_text[json_start:]
            result = json.loads(json_text)
            print(f"✓ Parsed response: {json.dumps(result, indent=2)}\n")
        else:
            print("✗ No JSON found in response\n")

        writer.close()
        await writer.wait_closed()

        print("✓ Test successful! HTTP POST with raw JSON response works.")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.30.206"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9090

    asyncio.run(test_http09_jsonrpc(host, port))
