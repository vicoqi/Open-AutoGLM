"""
Main WebSocket server for Phone Agent.

Entry point for the WebSocket server that wraps Open-AutoGLM PhoneAgent.
"""

import asyncio
import logging
import signal
import sys
import websockets

from . import config
from .websocket_handler import WebSocketHandler
from .task_executor import TaskExecutor

logger = logging.getLogger(__name__)

# Global state
active_connections = set()
server = None


async def handle_client(websocket):
    """
    Handle new client connection.

    Args:
        websocket: WebSocket connection
    """
    # Check connection limit
    server_config = config.get_server_config()
    if len(active_connections) >= server_config["max_connections"]:
        logger.warning("Max connections reached, rejecting new connection")
        await websocket.close(1008, "Server at capacity")
        return

    # Add to active connections
    active_connections.add(websocket)

    try:
        # Create task executor for this connection
        task_executor = TaskExecutor(
            model_config=config.get_model_config(),
            agent_config=config.get_agent_config(),
        )

        # Create handler
        handler = WebSocketHandler(
            websocket=websocket,
            task_executor=task_executor,
            heartbeat_interval=server_config["heartbeat_interval"],
        )

        # Handle connection
        await handler.handle_connection()

    finally:
        # Remove from active connections
        active_connections.discard(websocket)


async def start_server(host: str, port: int):
    """
    Start WebSocket server.

    Args:
        host: Host address to bind to
        port: Port number to listen on

    Returns:
        WebSocket server instance
    """
    global server

    logger.info(f"Starting WebSocket server on ws://{host}:{port}")

    server = await websockets.serve(
        handle_client,
        host,
        port,
        ping_interval=None,  # We handle heartbeat manually
    )

    logger.info(f"WebSocket server started on ws://{host}:{port}")
    return server


async def shutdown(sig=None):
    """
    Graceful shutdown handler.

    Args:
        sig: Signal that triggered shutdown
    """
    if sig:
        logger.info(f"Received exit signal {sig.name}")

    logger.info("Shutting down server...")

    # Close all active connections
    if active_connections:
        logger.info(f"Closing {len(active_connections)} active connections")
        await asyncio.gather(
            *[conn.close() for conn in active_connections],
            return_exceptions=True
        )

    # Stop server
    if server:
        server.close()
        await server.wait_closed()

    logger.info("Server shutdown complete")


def main():
    """Main entry point."""
    # Setup logging
    config.setup_logging()

    logger.info("Phone Agent WebSocket Server starting...")
    logger.info(f"Model: {config.MODEL_NAME} at {config.MODEL_BASE_URL}")
    logger.info(f"Device type: {config.DEVICE_TYPE}")
    logger.info(f"Language: {config.LANG}")

    # Get server config
    server_config = config.get_server_config()

    # Setup event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Setup signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s))
        )

    try:
        # Start server
        loop.run_until_complete(
            start_server(server_config["host"], server_config["port"])
        )

        # Run forever
        loop.run_forever()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        loop.run_until_complete(shutdown())
        loop.close()


if __name__ == "__main__":
    main()
