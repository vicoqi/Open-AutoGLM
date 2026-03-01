"""
Connection test script for Phone Agent WebSocket Server.

Tests basic connectivity and ping/pong.
"""

import asyncio
import json
import sys
import websockets


async def test_connection(uri: str):
    """
    Test connection to WebSocket server.

    Args:
        uri: WebSocket server URI
    """
    print(f"Testing connection to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected successfully!")

            # Test ping
            print("\nTesting ping...")
            ping_request = {"action": "ping"}
            await websocket.send(json.dumps(ping_request))

            # Wait for pong
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)

            if data.get("type") == "pong":
                print("✓ Ping/pong successful!")
            else:
                print(f"✗ Unexpected response: {data}")

            print("\n✓ All tests passed!")

    except asyncio.TimeoutError:
        print("✗ Timeout waiting for response")
        sys.exit(1)
    except websockets.exceptions.WebSocketException as e:
        print(f"✗ WebSocket error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


async def main():
    """Main entry point."""
    uri = "ws://localhost:8765"

    if len(sys.argv) > 1:
        uri = sys.argv[1]

    await test_connection(uri)


if __name__ == "__main__":
    print("Phone Agent WebSocket Server - Connection Test")
    print("=" * 60)

    asyncio.run(main())
