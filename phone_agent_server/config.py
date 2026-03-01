"""
Configuration management for Phone Agent WebSocket Server.

Reuses environment variables from the main Open-AutoGLM project.
Supports loading from .env file using python-dotenv.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    # Load .env from project root
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")
except ImportError:
    # python-dotenv not installed, use system environment variables only
    pass

# WebSocket Server Configuration
WEBSOCKET_HOST = os.getenv("PHONE_AGENT_WS_HOST", "0.0.0.0")
WEBSOCKET_PORT = int(os.getenv("PHONE_AGENT_WS_PORT", "8765"))
MAX_CONNECTIONS = int(os.getenv("PHONE_AGENT_WS_MAX_CONNECTIONS", "10"))
HEARTBEAT_INTERVAL = int(os.getenv("PHONE_AGENT_WS_HEARTBEAT_INTERVAL", "30"))  # seconds
TASK_TIMEOUT = int(os.getenv("PHONE_AGENT_WS_TASK_TIMEOUT", "300"))  # seconds

# Model Configuration (reuse from main project)
MODEL_BASE_URL = os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1")
MODEL_NAME = os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b")
MODEL_API_KEY = os.getenv("PHONE_AGENT_API_KEY", "EMPTY")

# Device Configuration (reuse from main project)
DEVICE_TYPE = os.getenv("PHONE_AGENT_DEVICE_TYPE", "adb")
DEVICE_ID = os.getenv("PHONE_AGENT_DEVICE_ID", None)
LANG = os.getenv("PHONE_AGENT_LANG", "cn")
MAX_STEPS = int(os.getenv("PHONE_AGENT_MAX_STEPS", "100"))

# Logging Configuration
LOG_LEVEL = os.getenv("PHONE_AGENT_LOG_LEVEL", "INFO")

# Cache for device type enum
_cached_device_type = None


def get_model_config():
    """Get model configuration as a dictionary."""
    return {
        "base_url": MODEL_BASE_URL,
        "model_name": MODEL_NAME,
        "api_key": MODEL_API_KEY,
    }


def get_agent_config():
    """Get agent configuration as a dictionary."""
    return {
        "max_steps": MAX_STEPS,
        "device_id": DEVICE_ID,
        "lang": LANG,
        "verbose": False,  # Disable verbose mode for WebSocket server
    }


def get_server_config():
    """Get server configuration as a dictionary."""
    return {
        "host": WEBSOCKET_HOST,
        "port": WEBSOCKET_PORT,
        "max_connections": MAX_CONNECTIONS,
        "heartbeat_interval": HEARTBEAT_INTERVAL,
        "task_timeout": TASK_TIMEOUT,
    }


def get_device_type_enum():
    """Get device type as enum (cached)."""
    global _cached_device_type
    if _cached_device_type is None:
        from phone_agent.device_factory import DeviceType
        type_map = {
            "adb": DeviceType.ADB,
            "hdc": DeviceType.HDC,
            "ios": DeviceType.IOS,
        }
        _cached_device_type = type_map.get(DEVICE_TYPE.lower(), DeviceType.ADB)
    return _cached_device_type


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
