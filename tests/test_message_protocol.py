"""
Tests for message protocol module.

Simple test class following CLAUDE.md guidelines.
"""

import json
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phone_agent_server')))

# Import from phone_agent_server directory
import message_protocol

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TestMessageProtocol:
    """Test message protocol parsing and formatting."""

    def test_parse_execute_request(self):
        """Test parsing execute request."""
        logger.info("Testing parse_execute_request...")

        # Valid request
        request_json = json.dumps({
            "action": "execute",
            "task": "打开微信",
            "device_id": "device123"
        })

        result = message_protocol.parse_request(request_json)
        logger.info(f"Parsed request: {result}")

        assert result["action"] == "execute"
        assert result["task"] == "打开微信"
        assert result["device_id"] == "device123"

        logger.info("✓ parse_execute_request passed")

    def test_parse_ping_request(self):
        """Test parsing ping request."""
        logger.info("Testing parse_ping_request...")

        request_json = json.dumps({"action": "ping"})
        result = message_protocol.parse_request(request_json)

        assert result["action"] == "ping"
        logger.info("✓ parse_ping_request passed")

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        logger.info("Testing parse_invalid_json...")

        try:
            message_protocol.parse_request("not json")
            logger.error("✗ Should have raised MessageProtocolError")
        except message_protocol.MessageProtocolError as e:
            logger.info(f"✓ Correctly raised error: {e}")

    def test_parse_missing_action(self):
        """Test parsing request with missing action."""
        logger.info("Testing parse_missing_action...")

        try:
            message_protocol.parse_request(json.dumps({"task": "test"}))
            logger.error("✗ Should have raised MessageProtocolError")
        except message_protocol.MessageProtocolError as e:
            logger.info(f"✓ Correctly raised error: {e}")

    def test_parse_missing_task(self):
        """Test parsing execute request with missing task."""
        logger.info("Testing parse_missing_task...")

        try:
            message_protocol.parse_request(json.dumps({"action": "execute"}))
            logger.error("✗ Should have raised MessageProtocolError")
        except message_protocol.MessageProtocolError as e:
            logger.info(f"✓ Correctly raised error: {e}")

    def test_format_progress(self):
        """Test formatting progress message."""
        logger.info("Testing format_progress...")

        message = message_protocol.format_progress(
            task_id="test-123",
            step=1,
            action={"action": "Tap", "element": [100, 200]},
            thinking="正在分析屏幕",
            message="执行成功"
        )

        data = json.loads(message)
        logger.info(f"Formatted progress: {data}")

        assert data["type"] == "progress"
        assert data["task_id"] == "test-123"
        assert data["step"] == 1
        assert data["action"]["action"] == "Tap"
        assert data["thinking"] == "正在分析屏幕"
        assert "timestamp" in data

        logger.info("✓ format_progress passed")

    def test_format_completed(self):
        """Test formatting completed message."""
        logger.info("Testing format_completed...")

        message = message_protocol.format_completed(
            task_id="test-123",
            result={"success": True},
            total_steps=5
        )

        data = json.loads(message)
        logger.info(f"Formatted completed: {data}")

        assert data["type"] == "completed"
        assert data["task_id"] == "test-123"
        assert data["total_steps"] == 5
        assert data["result"]["success"] is True
        assert "timestamp" in data

        logger.info("✓ format_completed passed")

    def test_format_error(self):
        """Test formatting error message."""
        logger.info("Testing format_error...")

        message = message_protocol.format_error(
            task_id="test-123",
            error="Device not found",
            error_type="execution_error"
        )

        data = json.loads(message)
        logger.info(f"Formatted error: {data}")

        assert data["type"] == "error"
        assert data["task_id"] == "test-123"
        assert data["error"] == "Device not found"
        assert data["error_type"] == "execution_error"
        assert "timestamp" in data

        logger.info("✓ format_error passed")

    def test_format_pong(self):
        """Test formatting pong message."""
        logger.info("Testing format_pong...")

        message = message_protocol.format_pong()
        data = json.loads(message)

        assert data["type"] == "pong"
        assert "timestamp" in data

        logger.info("✓ format_pong passed")

    def test_generate_task_id(self):
        """Test task ID generation."""
        logger.info("Testing generate_task_id...")

        task_id1 = message_protocol.generate_task_id()
        task_id2 = message_protocol.generate_task_id()

        logger.info(f"Generated task IDs: {task_id1}, {task_id2}")

        assert task_id1 != task_id2
        assert len(task_id1) == 36  # UUID format

        logger.info("✓ generate_task_id passed")


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Running Message Protocol Tests")
    logger.info("=" * 60)

    tester = TestMessageProtocol()

    # Run all test methods
    test_methods = [
        tester.test_parse_execute_request,
        tester.test_parse_ping_request,
        tester.test_parse_invalid_json,
        tester.test_parse_missing_action,
        tester.test_parse_missing_task,
        tester.test_format_progress,
        tester.test_format_completed,
        tester.test_format_error,
        tester.test_format_pong,
        tester.test_generate_task_id,
    ]

    passed = 0
    failed = 0

    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except AssertionError as e:
            logger.error(f"✗ {test_method.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            logger.error(f"✗ {test_method.__name__} error: {e}", exc_info=True)
            failed += 1

    logger.info("=" * 60)
    logger.info(f"Results: {passed} passed, {failed} failed")
    logger.info("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
