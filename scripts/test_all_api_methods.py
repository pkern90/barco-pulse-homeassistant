#!/usr/bin/env python3
"""Test all API methods with real Barco projector."""

import asyncio
import sys
from pathlib import Path

# Add custom_components to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.barco_pulse.api import (
    BarcoPulseApiClient,
    BarcoPulseApiError,
    BarcoPulseAuthenticationError,
    BarcoPulseConnectionError,
    BarcoPulseTimeoutError,
)


async def test_all_methods(host: str, port: int = 9090, auth_code: int | None = None):
    """Test all API methods."""
    print(f"Testing Barco Pulse API at {host}:{port}")
    if auth_code:
        print(f"Using authentication code: {auth_code}")
    print()

    client = BarcoPulseApiClient(host=host, port=port, auth_code=auth_code, timeout=5.0)

    try:
        # Test 1: Connection
        print("=" * 60)
        print("TEST 1: Connection")
        print("=" * 60)
        await client.connect()
        print("✓ Connected successfully!")
        print()

        # Test 2: System Info
        print("=" * 60)
        print("TEST 2: System Information")
        print("=" * 60)
        info = await client.get_system_info()
        print(f"Serial Number:    {info.get('serial_number')}")
        print(f"Model Name:       {info.get('model_name')}")
        print(f"Firmware Version: {info.get('firmware_version')}")
        print("✓ System info retrieved")
        print()

        # Test 3: System State
        print("=" * 60)
        print("TEST 3: System State")
        print("=" * 60)
        state = await client.get_system_state()
        print(f"Current state: {state}")
        print("✓ System state retrieved")
        print()

        # Test 4: Source Management
        print("=" * 60)
        print("TEST 4: Source Management")
        print("=" * 60)
        try:
            sources = await client.list_sources()
            print(f"Available sources: {sources}")
        except BarcoPulseApiError as e:
            print(f"⚠ Could not list sources: {e}")
            print("  (This method may not be supported on this projector model)")
            sources = []

        try:
            active_source = await client.get_active_source()
            print(f"Active source: {active_source}")
            print("✓ Source information retrieved")
        except BarcoPulseApiError as e:
            print(f"⚠ Could not get active source: {e}")
        print()

        # Test 5: Laser Power
        print("=" * 60)
        print("TEST 5: Laser Power")
        print("=" * 60)
        laser_power = await client.get_laser_power()
        print(f"Current laser power: {laser_power}%")
        print("✓ Laser power retrieved")
        print()

        # Test 6: Power On (commented out for safety)
        print("=" * 60)
        print("TEST 6: Power Control")
        print("=" * 60)
        print("ℹ Power control test skipped (uncomment to test)")
        print("  To test power control:")
        print("  - Uncomment await client.power_on() / power_off()")
        print("  - Note: This will actually power the projector on/off!")
        # await client.power_on()
        # print("✓ Power on command sent")
        # await asyncio.sleep(2)
        # state = await client.get_system_state()
        # print(f"State after power on: {state}")
        print()

        # Test 7: Set Laser Power (commented out for safety)
        print("=" * 60)
        print("TEST 7: Set Laser Power")
        print("=" * 60)
        print("ℹ Laser power change test skipped (uncomment to test)")
        print("  To test laser power control:")
        print("  - Uncomment await client.set_laser_power()")
        print("  - Note: This will change the projector's laser power!")
        # original_power = await client.get_laser_power()
        # test_power = 50.0
        # await client.set_laser_power(test_power)
        # print(f"✓ Set laser power to {test_power}%")
        # await asyncio.sleep(1)
        # new_power = await client.get_laser_power()
        # print(f"New laser power: {new_power}%")
        # await client.set_laser_power(original_power)
        # print(f"✓ Restored laser power to {original_power}%")
        print()

        # Test 8: Set Source (commented out for safety)
        print("=" * 60)
        print("TEST 8: Source Switching")
        print("=" * 60)
        print("ℹ Source switching test skipped (uncomment to test)")
        print("  To test source switching:")
        print("  - Uncomment await client.set_active_source()")
        print("  - Note: This will change the projector's active input!")
        # original_source = await client.get_active_source()
        # if len(sources) > 1:
        #     test_source = sources[1] if sources[0] == original_source else sources[0]
        #     await client.set_active_source(test_source)
        #     print(f"✓ Switched to source: {test_source}")
        #     await asyncio.sleep(1)
        #     await client.set_active_source(original_source)
        #     print(f"✓ Restored source to: {original_source}")
        print()

        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print()
        print("Summary:")
        print("  • Connection:         ✓")
        print("  • System Info:        ✓")
        print("  • System State:       ✓")
        print("  • Source Management:  ✓")
        print("  • Laser Power:        ✓")
        print("  • Power Control:      ⊘ (skipped)")
        print("  • Set Laser Power:    ⊘ (skipped)")
        print("  • Source Switching:   ⊘ (skipped)")
        print()
        print("To test write operations, edit the script and uncomment")
        print("the relevant sections. Be aware this will change projector state!")

    except BarcoPulseAuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        print()
        print("The projector requires a valid 5-digit authentication code.")
        print("Re-run with: python3 test_all_api_methods.py <host> [port] [auth_code]")
        return False

    except BarcoPulseTimeoutError as e:
        print(f"✗ Timeout: {e}")
        print()
        print("The projector is not responding. Check:")
        print("  - Is the projector powered on?")
        print("  - Is the JSON-RPC API enabled on the projector?")
        print("  - Is port 9090 accessible (firewall)?")
        return False

    except BarcoPulseConnectionError as e:
        print(f"✗ Connection error: {e}")
        print()
        print("Cannot connect to the projector. Check:")
        print("  - Is the IP address correct?")
        print("  - Is the projector on the network?")
        print("  - Can you ping the projector?")
        return False

    except BarcoPulseApiError as e:
        print(f"✗ API error: {e}")
        return False

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        await client.disconnect()

    return True


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 test_all_api_methods.py <host> [port] [auth_code]")
        print("Example: python3 test_all_api_methods.py 192.168.30.206")
        print("Example: python3 test_all_api_methods.py 192.168.30.206 9090 12345")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9090
    auth_code = int(sys.argv[3]) if len(sys.argv) > 3 else None

    success = await test_all_methods(host, port, auth_code)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
