#!/usr/bin/env python3
"""Example script demonstrating preset functionality with Barco Pulse API."""

import asyncio
import json


async def example_preset_workflow():
    """Demonstrate the preset workflow."""
    print("=== Barco Pulse Preset API Example ===\n")

    # Example 1: Get preset assignments
    print("1. Getting preset assignments...")
    print("   Request:")
    request1 = {
        "jsonrpc": "2.0",
        "method": "property.get",
        "id": 1,
        "params": "profile.presetassignments",
    }
    print(f"   {json.dumps(request1, indent=2)}")
    print("\n   Response:")
    response1 = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "1": "Cinema",
            "2": "Gaming",
            "3": "Sports",
            "4": "Presentation",
        },
    }
    print(f"   {json.dumps(response1, indent=2)}\n")

    # Example 2: Get available profiles
    print("2. Getting available profiles...")
    print("   Request:")
    request2 = {
        "jsonrpc": "2.0",
        "method": "property.get",
        "id": 2,
        "params": "profile.profiles",
    }
    print(f"   {json.dumps(request2, indent=2)}")
    print("\n   Response:")
    response2 = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": ["Cinema", "Gaming", "Sports", "Presentation", "Unassigned"],
    }
    print(f"   {json.dumps(response2, indent=2)}\n")

    # Example 3: Activate preset by number (recommended)
    print("3. Activating preset #1 (Cinema)...")
    print("   Request:")
    request3 = {
        "jsonrpc": "2.0",
        "method": "profile.activatepreset",
        "id": 3,
        "params": 1,
    }
    print(f"   {json.dumps(request3, indent=2)}")
    print("\n   Response:")
    response3 = {"jsonrpc": "2.0", "id": 3, "result": True}
    print(f"   {json.dumps(response3, indent=2)}\n")

    # Example 4: Alternative - Activate profile by name
    print("4. Alternative: Activating profile by name...")
    print("   Request:")
    request4 = {
        "jsonrpc": "2.0",
        "method": "profile.activateprofile",
        "id": 4,
        "params": "Gaming",
    }
    print(f"   {json.dumps(request4, indent=2)}")
    print("\n   Response:")
    response4 = {"jsonrpc": "2.0", "id": 4, "result": True}
    print(f"   {json.dumps(response4, indent=2)}\n")

    # Example 5: Get profile for preset
    print("5. Getting profile name for preset #2...")
    print("   Request:")
    request5 = {
        "jsonrpc": "2.0",
        "method": "profile.profileforpreset",
        "id": 5,
        "params": 2,
    }
    print(f"   {json.dumps(request5, indent=2)}")
    print("\n   Response:")
    response5 = {"jsonrpc": "2.0", "id": 5, "result": "Gaming"}
    print(f"   {json.dumps(response5, indent=2)}\n")

    # Example 6: Error case - projector not ready
    print("6. Error case: Projector in standby (state-dependent property)...")
    print("   Request:")
    request6 = {
        "jsonrpc": "2.0",
        "method": "property.get",
        "id": 6,
        "params": "profile.presetassignments",
    }
    print(f"   {json.dumps(request6, indent=2)}")
    print("\n   Response:")
    response6 = {
        "jsonrpc": "2.0",
        "id": 6,
        "error": {
            "code": -32601,
            "message": "Property not found",
        },
    }
    print(f"   {json.dumps(response6, indent=2)}")
    print("   → Handled as BarcoStateError in coordinator\n")

    # Show Home Assistant UI representation
    print("=== Home Assistant UI Representation ===\n")
    print("Entity: select.barco_pulse_preset")
    print("Name: Preset")
    print("Icon: mdi:palette")
    print("State: None (no way to track active preset)")
    print("Options:")
    print("  - 1: Cinema")
    print("  - 2: Gaming")
    print("  - 3: Sports")
    print("  - 4: Presentation")
    print("\nAvailable: True (only when projector is on/ready)")
    print("\nWhen user selects '2: Gaming':")
    print("  1. Parse '2: Gaming' → preset_num = 2")
    print("  2. Call device.activate_preset(2)")
    print("  3. Refresh coordinator data")


if __name__ == "__main__":
    asyncio.run(example_preset_workflow())
