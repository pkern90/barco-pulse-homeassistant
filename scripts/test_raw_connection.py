#!/usr/bin/env python3
"""Raw TCP communication test with Barco projector."""

import asyncio
import json


async def test_raw_communication(host: str, port: int = 9090):
    """Test raw TCP communication with the projector."""
    print(f"Connecting to {host}:{port}...")

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=5.0
        )
        print("✓ Connected!\n")

        # Send a simple property.get request
        request = {
            "jsonrpc": "2.0",
            "method": "property.get",
            "params": {"property": "system.serialnumber"},
            "id": 1,
        }

        message = json.dumps(request) + "\n"
        print(f"Sending:\n{json.dumps(request, indent=2)}\n")

        writer.write(message.encode("utf-8"))
        await writer.drain()

        print("Waiting for response (5 seconds)...")

        try:
            # Try to read response
            line = await asyncio.wait_for(reader.readline(), timeout=5.0)
            if line:
                print("\n✓ Received response:")
                print(f"Raw bytes: {line}")
                try:
                    response = json.loads(line.decode("utf-8"))
                    print(f"Parsed JSON:\n{json.dumps(response, indent=2)}")
                except json.JSONDecodeError:
                    print(
                        f"Could not parse as JSON: {line.decode('utf-8', errors='replace')}"
                    )
            else:
                print("✗ No response received (connection closed)")

        except TimeoutError:
            print("✗ Timeout - no response received")
            print("\nThis could mean:")
            print("- The projector requires authentication first")
            print("- The projector doesn't support JSON-RPC 2.0")
            print("- The API is disabled on the projector")

        writer.close()
        await writer.wait_closed()

    except TimeoutError:
        print("✗ Connection timeout")
    except ConnectionRefusedError:
        print("✗ Connection refused - port may be closed")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.30.206"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9090

    asyncio.run(test_raw_communication(host, port))
