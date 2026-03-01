"""
Simple integration test for WebSocket server.

Tests basic server startup and connection handling.
"""

import asyncio
import json
import logging
import sys
import os

# Add phone_agent_server to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phone_agent_server')))

import websockets

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TestWebSocketIntegration:
    """Integration tests for WebSocket server."""

    def __init__(self):
        self.server_uri = "ws://localhost:8765"
        self.server_process = None

    async def test_connection(self):
        """Test basic connection to server."""
        logger.info("Testing connection...")

        try:
            async with websockets.connect(self.server_uri, open_timeout=5) as websocket:
                logger.info("✓ Connected successfully")
                return True
        except Exception as e:
            logger.error(f"✗ Connection failed: {e}")
            return False

    async def test_ping_pong(self):
        """Test ping/pong functionality."""
        logger.info("Testing ping/pong...")

        try:
            async with websockets.connect(self.server_uri, open_timeout=5) as websocket:
                # Send ping
                ping_msg = json.dumps({"action": "ping"})
                await websocket.send(ping_msg)

                # Wait for pong
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)

                if data.get("type") == "pong":
                    logger.info("✓ Ping/pong successful")
                    return True
                else:
                    logger.error(f"✗ Unexpected response: {data}")
                    return False

        except Exception as e:
            logger.error(f"✗ Ping/pong failed: {e}")
            return False

    async def test_invalid_message(self):
        """Test handling of invalid message."""
        logger.info("Testing invalid message handling...")

        try:
            async with websockets.connect(self.server_uri, open_timeout=5) as websocket:
                # Send invalid JSON
                await websocket.send("not json")

                # Should receive error response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)

                if data.get("type") == "error" and data.get("error_type") == "protocol_error":
                    logger.info("✓ Invalid message handled correctly")
                    return True
                else:
                    logger.error(f"✗ Unexpected response: {data}")
                    return False

        except Exception as e:
            logger.error(f"✗ Test failed: {e}")
            return False


async def run_tests():
    """Run all integration tests."""
    logger.info("=" * 60)
    logger.info("WebSocket Integration Tests")
    logger.info("=" * 60)
    logger.info("NOTE: Server must be running on ws://localhost:8765")
    logger.info("Start server with: python -m phone_agent_server.server")
    logger.info("=" * 60)

    tester = TestWebSocketIntegration()

    # Run tests
    tests = [
        ("Connection", tester.test_connection),
        ("Ping/Pong", tester.test_ping_pong),
        ("Invalid Message", tester.test_invalid_message),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        logger.info(f"\n[{test_name}]")
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"✗ Test error: {e}", exc_info=True)
            failed += 1

    logger.info("\n" + "=" * 60)
    logger.info(f"Results: {passed} passed, {failed} failed")
    logger.info("=" * 60)

    return 0 if failed == 0 else 1


def main():
    """Main entry point."""
    return asyncio.run(run_tests())


if __name__ == '__main__':
    sys.exit(main())
