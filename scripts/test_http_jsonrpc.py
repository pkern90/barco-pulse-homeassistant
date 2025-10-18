#!/usr/bin/env python3
"""Simple HTTP JSON-RPC test for Barco HDR CS projector."""

import asyncio
import json

import aiohttp


async def test_http_jsonrpc(host: str, port: int = 9090):
    """Test HTTP-based JSON-RPC communication."""
    url = f"http://{host}:{port}"
    print(f"Testing HTTP JSON-RPC at {url}\n")

    async with aiohttp.ClientSession() as session:
        # Test 1: Get serial number
        print("Test 1: Getting system.serialnumber")
        request = {
            "jsonrpc": "2.0",
            "method": "property.get",
            "params": {"property": "system.serialnumber"},
            "id": 1,
        }
        print(f"Request: {json.dumps(request, indent=2)}")

        try:
            async with session.post(url, json=request) as response:
                result = await response.json()
                print(f"✓ Response: {json.dumps(result, indent=2)}\n")
        except Exception as e:
            print(f"✗ Error: {e}\n")
            return

        # Test 2: Get system state
        print("Test 2: Getting system.state")
        request = {
            "jsonrpc": "2.0",
            "method": "property.get",
            "params": {"property": "system.state"},
            "id": 2,
        }
        print(f"Request: {json.dumps(request, indent=2)}")

        try:
            async with session.post(url, json=request) as response:
                result = await response.json()
                print(f"✓ Response: {json.dumps(result, indent=2)}\n")
        except Exception as e:
            print(f"✗ Error: {e}\n")
            return

        # Test 3: Get multiple properties
        print("Test 3: Getting multiple properties")
        request = {
            "jsonrpc": "2.0",
            "method": "property.get",
            "params": {
                "property": [
                    "system.serialnumber",
                    "system.modelname",
                    "system.firmwareversion",
                ]
            },
            "id": 3,
        }
        print(f"Request: {json.dumps(request, indent=2)}")

        try:
            async with session.post(url, json=request) as response:
                result = await response.json()
                print(f"✓ Response: {json.dumps(result, indent=2)}\n")
        except Exception as e:
            print(f"✗ Error: {e}\n")
            return

        print("✓ All tests passed! HTTP JSON-RPC is working.")


if __name__ == "__main__":
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.30.206"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9090

    asyncio.run(test_http_jsonrpc(host, port))
