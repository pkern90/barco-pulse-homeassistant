#!/usr/bin/env python3
"""Test connection to real Barco Pulse projector."""

import asyncio
import sys

# Add parent directory to path to import the API
sys.path.insert(0, "/workspaces/barco-pulse-homeassistant")

from custom_components.barco_pulse.api import (
    BarcoPulseApiClient,
    BarcoPulseAuthenticationError,
    BarcoPulseConnectionError,
    BarcoPulseTimeoutError,
)


async def test_connection(host: str, port: int = 9090, auth_code: int | None = None):
    """Test connection to projector."""
    print(f"Testing connection to {host}:{port}")
    if auth_code:
        print(f"Using authentication code: {auth_code}")

    client = BarcoPulseApiClient(host=host, port=port, auth_code=auth_code, timeout=5.0)

    try:
        print("Connecting...")
        await client.connect()
        print("✓ Connected successfully!")

        print("\nGetting system information...")
        info = await client.get_system_info()
        print("✓ System information:")
        print(f"  Serial Number: {info.get('serial_number')}")
        print(f"  Model Name: {info.get('model_name')}")
        print(f"  Firmware Version: {info.get('firmware_version')}")

        print("\nGetting system state...")
        state = await client.get_system_state()
        print(f"✓ System state: {state}")

        print("\nConnection test successful!")
        return True

    except BarcoPulseAuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        print("  The projector requires a valid 5-digit authentication code.")
        return False

    except BarcoPulseTimeoutError as e:
        print(f"✗ Timeout: {e}")
        print("  The projector is not responding. Check:")
        print("  - Is the projector powered on?")
        print("  - Is the JSON-RPC API enabled on the projector?")
        print("  - Is port 9090 accessible (firewall)?")
        return False

    except BarcoPulseConnectionError as e:
        print(f"✗ Connection error: {e}")
        print("  Cannot connect to the projector. Check:")
        print("  - Is the IP address correct?")
        print("  - Is the projector on the network?")
        print("  - Can you ping the projector?")
        return False

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        await client.disconnect()
        print("\nDisconnected.")


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 test_projector_connection.py <host> [port] [auth_code]")
        print("Example: python3 test_projector_connection.py 192.168.30.206")
        print("Example: python3 test_projector_connection.py 192.168.30.206 9090 12345")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9090
    auth_code = int(sys.argv[3]) if len(sys.argv) > 3 else None

    await test_connection(host, port, auth_code)


if __name__ == "__main__":
    asyncio.run(main())
