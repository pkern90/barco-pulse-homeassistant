#!/usr/bin/env python3
"""Test authentication-first approach with Barco projector."""

import asyncio
import json
import sys


async def test_auth_first(host: str, port: int = 9090):
    """Test if projector requires authentication before any requests."""
    print(f"Connecting to {host}:{port}...")

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=5.0
        )
        print("✓ Connected!\n")

        # Try authenticating with code 00000 (common default)
        auth_request = {
            "jsonrpc": "2.0",
            "method": "authenticate",
            "params": {"code": 0},
            "id": 1,
        }

        print("Trying authentication with code: 00000")
        print(f"Sending: {json.dumps(auth_request)}\n")

        message = json.dumps(auth_request) + "\n"
        writer.write(message.encode("utf-8"))
        await writer.drain()

        print("Waiting for authentication response...")
        try:
            line = await asyncio.wait_for(reader.readline(), timeout=3.0)
            if line:
                print(f"✓ Received: {line.decode('utf-8').strip()}\n")

                # Now try getting a property
                prop_request = {
                    "jsonrpc": "2.0",
                    "method": "property.get",
                    "params": {"property": "system.serialnumber"},
                    "id": 2,
                }

                print("Now trying to get property...")
                print(f"Sending: {json.dumps(prop_request)}\n")

                message = json.dumps(prop_request) + "\n"
                writer.write(message.encode("utf-8"))
                await writer.drain()

                print("Waiting for property response...")
                line = await asyncio.wait_for(reader.readline(), timeout=3.0)
                if line:
                    response = json.loads(line.decode("utf-8"))
                    print(f"✓ Success! Response:\n{json.dumps(response, indent=2)}")
                else:
                    print("✗ No response to property request")
            else:
                print("✗ No authentication response")

        except TimeoutError:
            print("✗ Timeout waiting for response")
            print("\nTrying without authentication...")

            # Maybe it doesn't need auth - try property.get directly
            prop_request = {
                "jsonrpc": "2.0",
                "method": "property.get",
                "params": {"property": "system.serialnumber"},
                "id": 3,
            }

            print(f"Sending: {json.dumps(prop_request)}\n")
            message = json.dumps(prop_request) + "\n"
            writer.write(message.encode("utf-8"))
            await writer.drain()

            print("Waiting for response...")
            line = await asyncio.wait_for(reader.readline(), timeout=3.0)
            if line:
                response = json.loads(line.decode("utf-8"))
                print(f"✓ Success! Response:\n{json.dumps(response, indent=2)}")

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.30.206"
    asyncio.run(test_auth_first(host))
