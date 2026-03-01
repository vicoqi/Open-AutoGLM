"""
WebSocket connection handler for Phone Agent Server.

Manages individual WebSocket connections, message routing, and heartbeat.
"""

import asyncio
import logging
from typing import Optional
import websockets

from . import message_protocol
from .task_executor import TaskExecutor

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """
    Handles a single WebSocket connection.

    Manages connection lifecycle, message routing, heartbeat, and task execution.
    """

    def __init__(
        self,
        websocket: websockets.WebSocketServerProtocol,
        task_executor: TaskExecutor,
        heartbeat_interval: int = 30,
    ):
        """
        Initialize WebSocket handler.

        Args:
            websocket: WebSocket connection
            task_executor: TaskExecutor instance
            heartbeat_interval: Heartbeat interval in seconds
        """
        self.websocket = websocket
        self.task_executor = task_executor
        self.heartbeat_interval = heartbeat_interval
        self.current_task_id: Optional[str] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.running = False

    async def handle_connection(self):
        """
        Handle WebSocket connection lifecycle.

        Main entry point for connection handling.
        """
        client_addr = self.websocket.remote_address
        logger.info(f"Client connected: {client_addr}")

        self.running = True

        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        try:
            # Message handling loop
            async for message in self.websocket:
                try:
                    await self._handle_message(message)
                except message_protocol.MessageProtocolError as e:
                    logger.warning(f"Protocol error: {e}")
                    await self._send_error(None, str(e), "protocol_error")
                except Exception as e:
                    logger.error(f"Error handling message: {e}", exc_info=True)
                    await self._send_error(None, str(e), "internal_error")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_addr}")
        except Exception as e:
            logger.error(f"Connection error: {e}", exc_info=True)
        finally:
            await self._cleanup()

    async def _handle_message(self, message: str):
        """
        Handle incoming message.

        Args:
            message: Raw message string from client
        """
        # Parse request
        request = message_protocol.parse_request(message)
        action = request["action"]

        logger.debug(f"Received action: {action}")

        if action == "execute":
            await self._handle_execute(request)
        elif action == "ping":
            await self._handle_ping()
        elif action == "cancel":
            await self._handle_cancel()
        else:
            raise message_protocol.MessageProtocolError(f"Unknown action: {action}")

    async def _handle_execute(self, request: dict):
        """
        Handle task execution request.

        Args:
            request: Parsed request dictionary
        """
        task = request["task"]
        device_id = request.get("device_id")

        # Generate task ID
        task_id = message_protocol.generate_task_id()
        self.current_task_id = task_id

        logger.info(f"Executing task {task_id}: {task}")

        # Set progress callback (closure captures task_id)
        async def progress_callback(progress_data):
            await self._send_progress(task_id, progress_data)

        self.task_executor.set_progress_callback(progress_callback)

        try:
            # Execute task
            result = await self.task_executor.execute_task(task, device_id)

            # Send completion or error
            if result.get("success"):
                await self._send_completed(task_id, result)
            else:
                await self._send_error(
                    task_id,
                    result.get("error", "Unknown error"),
                    "execution_error"
                )

        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            await self._send_error(task_id, str(e), "execution_error")
        finally:
            self.current_task_id = None

    async def _handle_ping(self):
        """Handle ping request."""
        pong_message = message_protocol.format_pong()
        await self.websocket.send(pong_message)

    async def _handle_cancel(self):
        """Handle task cancellation request."""
        if self.current_task_id:
            logger.warning(f"Task cancellation requested for {self.current_task_id} (not supported in MVP)")
        else:
            logger.warning("Cancel requested but no task is running")

    async def _send_progress(self, task_id: str, progress_data: dict):
        """
        Send progress update to client.

        Args:
            task_id: Task identifier
            progress_data: Progress data from PhoneAgent
        """
        # Extract fields once
        step = progress_data.get("step", 0)
        action = progress_data.get("action")
        thinking = progress_data.get("thinking")
        message = progress_data.get("message")

        msg = message_protocol.format_progress(
            task_id=task_id,
            step=step,
            action=action,
            thinking=thinking,
            message=message,
        )
        await self.websocket.send(msg)

    async def _send_completed(self, task_id: str, result: dict):
        """
        Send completion message to client.

        Args:
            task_id: Task identifier
            result: Task execution result
        """
        message = message_protocol.format_completed(
            task_id=task_id,
            result=result.get("result", {}),
            total_steps=result.get("total_steps", 0),
        )
        await self.websocket.send(message)

    async def _send_error(self, task_id: Optional[str], error: str, error_type: str):
        """
        Send error message to client.

        Args:
            task_id: Task identifier (None if no task)
            error: Error description
            error_type: Type of error
        """
        message = message_protocol.format_error(
            task_id=task_id or "unknown",
            error=error,
            error_type=error_type,
        )
        await self.websocket.send(message)

    async def _heartbeat_loop(self):
        """
        Heartbeat loop to keep connection alive.

        Sends ping messages at regular intervals.
        """
        try:
            while self.running:
                await asyncio.sleep(self.heartbeat_interval)
                try:
                    await self.websocket.ping()
                except Exception as e:
                    logger.warning(f"Heartbeat failed: {e}")
                    break
        except asyncio.CancelledError:
            pass

    async def _cleanup(self):
        """Clean up resources."""
        self.running = False

        # Cancel heartbeat
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

        # Cleanup task executor
        self.task_executor.cleanup()

        logger.info("Connection handler cleaned up")
