#!/usr/bin/env python3
"""Introspect Barco projector API to discover available methods and properties."""

import asyncio
import json
import sys


async def introspect_api(host: str, port: int = 9090):
    """Introspect projector API."""
    print(f"Connecting to {host}:{port}...")

    try:
        reader, writer = await asyncio.open_connection(host, port)

        # Test 1: Introspect root
        print("\n" + "=" * 60)
        print("ROOT INTROSPECTION")
        print("=" * 60)
        request = {"jsonrpc": "2.0", "method": "introspect", "params": {}, "id": 1}

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

        data = await reader.read(16384)
        response_text = data.decode()

        json_start = response_text.find("{")
        if json_start >= 0:
            json_text = response_text[json_start:]
            result = json.loads(json_text)
            if "result" in result:
                print(json.dumps(result["result"], indent=2))
            else:
                print(f"Error: {result}")

        writer.close()
        await writer.wait_closed()

        # Test 2: Introspect system
        print("\n" + "=" * 60)
        print("SYSTEM INTROSPECTION")
        print("=" * 60)
        reader, writer = await asyncio.open_connection(host, port)
        request = {
            "jsonrpc": "2.0",
            "method": "introspect",
            "params": {"object": "system"},
            "id": 2,
        }

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

        data = await reader.read(16384)
        response_text = data.decode()

        json_start = response_text.find("{")
        if json_start >= 0:
            json_text = response_text[json_start:]
            result = json.loads(json_text)
            if "result" in result:
                print(json.dumps(result["result"], indent=2))
            else:
                print(f"Error: {result}")

        writer.close()
        await writer.wait_closed()

        # Test 3: Get all system properties
        print("\n" + "=" * 60)
        print("SYSTEM PROPERTIES")
        print("=" * 60)
        reader, writer = await asyncio.open_connection(host, port)
        request = {
            "jsonrpc": "2.0",
            "method": "property.get",
            "params": {"property": "system"},
            "id": 3,
        }

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

        data = await reader.read(16384)
        response_text = data.decode()

        json_start = response_text.find("{")
        if json_start >= 0:
            json_text = response_text[json_start:]
            result = json.loads(json_text)
            if "result" in result:
                print(json.dumps(result["result"], indent=2))
            else:
                print(f"Error: {result}")

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.30.206"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9090

    asyncio.run(introspect_api(host, port))
