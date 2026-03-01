"""
Message protocol for Phone Agent WebSocket Server.

Implements the request/response message format defined in PRD-001.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MessageProtocolError(Exception):
    """Exception raised for message protocol errors."""
    pass


def _get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def parse_request(message: str) -> Dict[str, Any]:
    """
    Parse incoming JSON request message.

    Expected format:
    {
        "action": "execute",
        "task": "task description",
        "device_id": "optional_device_id",
        "options": {}
    }

    Args:
        message: JSON string from client

    Returns:
        Parsed request dictionary

    Raises:
        MessageProtocolError: If message format is invalid
    """
    try:
        data = json.loads(message)
    except json.JSONDecodeError as e:
        raise MessageProtocolError(f"Invalid JSON: {e}")

    # Validate required fields
    if "action" not in data:
        raise MessageProtocolError("Missing required field: action")

    action = data["action"]

    if action == "execute":
        if "task" not in data:
            raise MessageProtocolError("Missing required field: task")
        if not isinstance(data["task"], str) or not data["task"].strip():
            raise MessageProtocolError("Task must be a non-empty string")
    elif action == "ping":
        # Ping doesn't require additional fields
        pass
    elif action == "cancel":
        # Cancel doesn't require additional fields
        pass
    else:
        raise MessageProtocolError(f"Unknown action: {action}")

    return data


def format_progress(
    task_id: str,
    step: int,
    action: Optional[Dict[str, Any]] = None,
    thinking: Optional[str] = None,
    message: Optional[str] = None,
) -> str:
    """
    Format progress message.

    Args:
        task_id: Unique task identifier
        step: Current step number
        action: Action details dictionary
        thinking: AI thinking process
        message: Result message

    Returns:
        JSON string of progress message
    """
    data = {
        "type": "progress",
        "task_id": task_id,
        "step": step,
        "timestamp": _get_utc_timestamp(),
    }

    if action:
        data["action"] = action
    if thinking:
        data["thinking"] = thinking
    if message:
        data["message"] = message

    return json.dumps(data, ensure_ascii=False)


def format_completed(
    task_id: str,
    result: Dict[str, Any],
    total_steps: int,
) -> str:
    """
    Format task completion message.

    Args:
        task_id: Unique task identifier
        result: Task execution result
        total_steps: Total number of steps executed

    Returns:
        JSON string of completion message
    """
    data = {
        "type": "completed",
        "task_id": task_id,
        "result": result,
        "total_steps": total_steps,
        "timestamp": _get_utc_timestamp(),
    }

    return json.dumps(data, ensure_ascii=False)


def format_error(
    task_id: str,
    error: str,
    error_type: str = "execution_error",
) -> str:
    """
    Format error message.

    Args:
        task_id: Unique task identifier
        error: Error description
        error_type: Type of error (protocol_error, execution_error, etc.)

    Returns:
        JSON string of error message
    """
    data = {
        "type": "error",
        "task_id": task_id,
        "error": error,
        "error_type": error_type,
        "timestamp": _get_utc_timestamp(),
    }

    return json.dumps(data, ensure_ascii=False)


def format_pong() -> str:
    """
    Format pong response to ping.

    Returns:
        JSON string of pong message
    """
    data = {
        "type": "pong",
        "timestamp": _get_utc_timestamp(),
    }

    return json.dumps(data, ensure_ascii=False)


def generate_task_id() -> str:
    """
    Generate a unique task ID.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())
