"""
Task executor for Phone Agent WebSocket Server.

Wraps PhoneAgent with progress callbacks for real-time updates.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig
from phone_agent.agent import AgentConfig
from phone_agent.device_factory import set_device_type

from . import config as server_config

logger = logging.getLogger(__name__)


class WebSocketPhoneAgent(PhoneAgent):
    """
    WebSocket version of PhoneAgent with progress callback support.

    Inherits from PhoneAgent and adds a progress callback hook that is
    called after each step execution.
    """

    def __init__(self, *args, progress_callback=None, **kwargs):
        """
        Initialize WebSocketPhoneAgent.

        Args:
            progress_callback: Callable that receives progress updates
            *args, **kwargs: Arguments passed to PhoneAgent
        """
        super().__init__(*args, **kwargs)
        self.progress_callback = progress_callback

    def _execute_step(self, user_prompt=None, is_first=False):
        """
        Execute a single step and call progress callback.

        Overrides PhoneAgent._execute_step to add progress reporting.

        Args:
            user_prompt: User prompt for first step
            is_first: Whether this is the first step

        Returns:
            StepResult object
        """
        # Call parent method to execute the step
        result = super()._execute_step(user_prompt, is_first)

        # Send progress update if callback is provided
        if self.progress_callback:
            try:
                self.progress_callback({
                    'step': self.step_count,
                    'success': result.success,
                    'finished': result.finished,
                    'action': result.action,
                    'thinking': result.thinking,
                    'message': result.message,
                })
            except Exception as e:
                logger.error(f"Error in progress callback: {e}", exc_info=True)

        return result


class TaskExecutor:
    """
    Executes phone automation tasks using WebSocketPhoneAgent.

    Handles async/sync integration and progress streaming.
    """

    def __init__(
        self,
        model_config: Dict[str, Any],
        agent_config: Dict[str, Any],
    ):
        """
        Initialize TaskExecutor.

        Args:
            model_config: Model configuration dictionary
            agent_config: Agent configuration dictionary
        """
        self.model_config = ModelConfig(**model_config)
        self.base_agent_config = AgentConfig(**agent_config)
        # Use cached device type enum from config
        self.device_type_enum = server_config.get_device_type_enum()
        self.agent = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.progress_callback_async = None
        self.loop = None

    def set_progress_callback(self, callback: Callable):
        """
        Set async progress callback.

        Args:
            callback: Async callable that receives progress updates
        """
        self.progress_callback_async = callback
        self.loop = asyncio.get_event_loop()

    def _sync_progress_callback(self, progress_data: Dict[str, Any]):
        """
        Synchronous progress callback that schedules async callback.

        This is called from the worker thread and safely schedules
        the async callback in the main event loop.

        Args:
            progress_data: Progress update dictionary
        """
        if self.progress_callback_async and self.loop:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.progress_callback_async(progress_data),
                    self.loop
                )
            except Exception as e:
                logger.error(f"Error scheduling async callback: {e}", exc_info=True)

    async def execute_task(
        self,
        task: str,
        device_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a phone automation task.

        Args:
            task: Task description in natural language
            device_id: Optional specific device ID

        Returns:
            Result dictionary with success status and details

        Raises:
            Exception: If task execution fails
        """
        logger.info(f"Starting task execution: {task}")

        # Run synchronous PhoneAgent in thread pool
        result = await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self._run_task,
            task,
            device_id
        )

        logger.info(f"Task execution completed: {result.get('success')}")
        return result

    def _run_task(self, task: str, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run task in worker thread (synchronous).

        Args:
            task: Task description
            device_id: Optional device ID

        Returns:
            Result dictionary
        """
        try:
            # Set device type (use cached enum)
            set_device_type(self.device_type_enum)

            # Build per-task agent config to avoid cross-request state leakage
            task_agent_config = self._build_task_agent_config(device_id)

            # Create WebSocketPhoneAgent instance
            self.agent = WebSocketPhoneAgent(
                model_config=self.model_config,
                agent_config=task_agent_config,
                progress_callback=self._sync_progress_callback,
            )

            # Execute task
            result = self.agent.run(task)

            return {
                'success': True,
                'result': result,
                'total_steps': self.agent.step_count,
            }

        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'total_steps': self.agent.step_count if self.agent else 0,
            }

    def _build_task_agent_config(self, device_id: Optional[str]) -> AgentConfig:
        """
        Build an isolated AgentConfig for a single task execution.

        Args:
            device_id: Optional per-request device ID override

        Returns:
            AgentConfig instance for the current task
        """
        resolved_device_id = (
            device_id
            if device_id is not None
            else self.base_agent_config.device_id
        )

        return AgentConfig(
            max_steps=self.base_agent_config.max_steps,
            device_id=resolved_device_id,
            lang=self.base_agent_config.lang,
            system_prompt=self.base_agent_config.system_prompt,
            verbose=self.base_agent_config.verbose,
        )

    def cleanup(self):
        """Clean up resources."""
        self.agent = None
        if self.executor:
            self.executor.shutdown(wait=False)
