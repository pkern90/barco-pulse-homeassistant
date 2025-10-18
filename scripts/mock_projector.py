#!/usr/bin/env python3
"""Mock Barco Pulse projector server for testing."""

import asyncio
import json
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

# Mock projector state
STATE = {
    "system.serialnumber": "MOCK123456",
    "system.modelname": "Barco Pulse (Mock)",
    "system.firmwareversion": "1.0.0-mock",
    "system.state": "on",
    "image.window.main.source": "DisplayPort 1",
}


class MockProjectorProtocol(asyncio.Protocol):
    """Protocol handler for mock projector."""

    def __init__(self):
        """Initialize protocol."""
        self.transport = None
        self.authenticated = False

    def connection_made(self, transport):
        """Handle new connection."""
        peername = transport.get_extra_info("peername")
        _LOGGER.info("Connection from %s", peername)
        self.transport = transport

    def data_received(self, data):
        """Handle received data."""
        try:
            message = data.decode("utf-8").strip()
            _LOGGER.debug("Received: %s", message)

            request = json.loads(message)
            response = self.handle_request(request)

            if response:
                response_str = json.dumps(response) + "\n"
                _LOGGER.debug("Sending: %s", response)
                self.transport.write(response_str.encode("utf-8"))
        except Exception as e:
            _LOGGER.exception("Error handling request: %s", e)

    def handle_request(self, request):
        """Process JSON-RPC request and return response."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        # Handle authentication
        if method == "authenticate":
            code = params.get("code")
            _LOGGER.info("Authentication request with code: %s", code)
            # Accept any 5-digit code for testing
            if code and 10000 <= code <= 99999:
                self.authenticated = True
                return {
                    "jsonrpc": "2.0",
                    "result": 0,
                    "id": request_id,
                }
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": "Invalid authentication code",
                },
                "id": request_id,
            }

        # Handle property.get
        if method == "property.get":
            property_name = params.get("property")

            # Handle list of properties
            if isinstance(property_name, list):
                result = {}
                for prop in property_name:
                    result[prop] = STATE.get(prop)
                return {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id,
                }
            # Handle single property
            result = STATE.get(property_name)
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id,
            }

        # Handle property.set
        if method == "property.set":
            property_name = params.get("property")
            value = params.get("value")
            if property_name in STATE:
                STATE[property_name] = value
                _LOGGER.info("Set %s = %s", property_name, value)
            return {
                "jsonrpc": "2.0",
                "result": 0,
                "id": request_id,
            }

        # Handle system.poweron
        if method == "system.poweron":
            STATE["system.state"] = "on"
            _LOGGER.info("Power ON")
            return {
                "jsonrpc": "2.0",
                "result": 0,
                "id": request_id,
            }

        # Handle system.poweroff
        if method == "system.poweroff":
            STATE["system.state"] = "standby"
            _LOGGER.info("Power OFF")
            return {
                "jsonrpc": "2.0",
                "result": 0,
                "id": request_id,
            }

        # Unknown method
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}",
            },
            "id": request_id,
        }

    def connection_lost(self, exc):
        """Handle connection closed."""
        _LOGGER.info("Connection closed")


async def main():
    """Start mock projector server."""
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9090

    loop = asyncio.get_running_loop()
    server = await loop.create_server(MockProjectorProtocol, host, port)

    addr = server.sockets[0].getsockname()
    _LOGGER.info("Mock Barco Pulse projector listening on %s:%s", addr[0], addr[1])
    _LOGGER.info("Press Ctrl+C to stop")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
