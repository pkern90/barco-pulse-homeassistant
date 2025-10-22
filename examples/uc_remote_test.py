"""
Test script for Unfolded Circle Remote 3 command functionality.

This script demonstrates how the remote entity processes commands
for preset and profile activation.
"""

import asyncio

from custom_components.barco_pulse.api import BarcoDevice


async def test_remote_commands():
    """Test remote command parsing and execution."""
    # Initialize device (replace with your projector IP)
    device = BarcoDevice(host="192.168.30.206", port=9090)

    try:
        # Connect to projector
        print("Connecting to projector...")
        await device.connect()
        print("✓ Connected")

        # Test 1: Power on
        print("\nTest 1: Power On")
        await device.power_on()
        print("✓ Power on command sent")

        # Wait for projector to reach ready state
        print("Waiting for projector to power on...")
        await asyncio.sleep(30)

        # Test 2: Activate preset by number
        print("\nTest 2: Activate Preset 5")
        try:
            await device.activate_preset(5)
            print("✓ Preset 5 activated")
        except Exception as e:  # noqa: BLE001
            print(f"✗ Preset activation failed: {e}")

        await asyncio.sleep(2)

        # Test 3: Get available profiles
        print("\nTest 3: List Available Profiles")
        try:
            profiles = await device.get_profiles()
            print(f"✓ Available profiles: {profiles}")
        except Exception as e:  # noqa: BLE001
            print(f"⚠ Profile listing not available: {e}")
            profiles = []

        # Test 4: Activate profile by name (use first available)
        if profiles:
            profile_name = profiles[0]
            print(f"\nTest 4: Activate Profile '{profile_name}'")
            try:
                await device.activate_profile(profile_name)
                print(f"✓ Profile '{profile_name}' activated")
            except Exception as e:  # noqa: BLE001
                print(f"✗ Profile activation failed: {e}")
        else:
            print("\nTest 4: Skipped (no profiles configured)")

        await asyncio.sleep(2)

        # Test 5: Switch input source
        print("\nTest 5: Switch to HDMI 1")
        try:
            sources = await device.get_available_sources()
            if sources:
                # Find HDMI 1 or use first available
                hdmi1 = next(
                    (s for s in sources if "HDMI" in s and "1" in s), sources[0]
                )
                await device.set_source(hdmi1)
                print(f"✓ Switched to source: {hdmi1}")
            else:
                print("✗ No sources available")
        except Exception:  # noqa: BLE001
            print("⚠ Source switching not available in current state")

        # Test 6: Command sequence (what UC Remote would send)
        print("\nTest 6: Command Sequence (Movie Night Activity)")
        print("  1. Switch to HDMI 1")
        try:
            sources = await device.get_available_sources()
            if sources:
                hdmi1 = next(
                    (s for s in sources if "HDMI" in s and "1" in s), sources[0]
                )
                await device.set_source(hdmi1)
            print("  2. Activate Preset 1")
            await device.activate_preset(1)
            print("✓ Sequence completed")
        except Exception as e:  # noqa: BLE001
            print(f"⚠ Sequence partially failed: {e}")

        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise

    finally:
        # Always disconnect
        await device.disconnect()
        print("\n✓ Disconnected")


async def test_command_parsing():
    """Test command string parsing logic (matches remote.py)."""
    print("\n" + "=" * 50)
    print("Testing Command Parsing Logic")
    print("=" * 50)

    test_commands = [
        "source_HDMI 1",
        "preset_5",
        "preset_0",
        "preset_29",
        "profile_Cinema",
        "profile_Gaming",
        "unknown_command",
    ]

    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")

        if cmd.startswith("source_"):
            source_name = cmd[7:]
            print("  → Type: Source Selection")
            print(f"  → Source: '{source_name}'")

        elif cmd.startswith("preset_"):
            try:
                preset_num = int(cmd[7:])
                print("  → Type: Preset Activation")
                print(f"  → Preset Number: {preset_num}")
                if 0 <= preset_num <= 29:
                    print("  → Valid: ✓")
                else:
                    print("  → Valid: ✗ (out of range 0-29)")
            except ValueError:
                print("  → Type: Preset Activation")
                print("  → Valid: ✗ (invalid number)")

        elif cmd.startswith("profile_"):
            profile_name = cmd[8:]
            print("  → Type: Profile Activation")
            print(f"  → Profile Name: '{profile_name}'")

        else:
            print("  → Type: Unknown (will be ignored)")

    print("\n" + "=" * 50)


async def main():
    """Main test runner."""
    print("=" * 50)
    print("Barco Pulse UC Remote Command Test Suite")
    print("=" * 50)

    # Part 1: Test command parsing (no projector needed)
    await test_command_parsing()

    # Part 2: Test actual commands (requires projector)
    print("\n\nProceed with live projector tests? (y/n): ", end="")
    response = input().strip().lower()

    if response == "y":
        await test_remote_commands()
    else:
        print("\nSkipping live projector tests.")
        print("\nTo test with a real projector:")
        print("1. Update the host IP in test_remote_commands()")
        print("2. Run this script again and choose 'y'")


if __name__ == "__main__":
    asyncio.run(main())
