"""Agent executor module for A2A integration."""

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import AgentCard, TaskState, UnsupportedOperationError
from a2a.utils.errors import ServerError
from google.adk.runners import Runner
from google.genai import types

from aigency.utils.logger import get_logger
from aigency.utils.utils import (
    convert_a2a_part_to_genai,
    convert_genai_part_to_a2a,
)

logger = get_logger()

# TODO: This needs to be changed
DEFAULT_USER_ID = "self"

class AgentA2AExecutor(AgentExecutor):
    """Agent executor for A2A integration with Google ADK runners."""

    def __init__(self, runner: Runner, card: AgentCard):
        """Initialize the BaseAgentA2AExecutor.

        Args:
            card (AgentCard): The agent card containing metadata about the agent.
        """
        self._card = card
        # Track active sessions for potential cancellation
        self._active_sessions: set[str] = set()
        self.runner = runner

    async def _upsert_session(self, session_id: str) -> "Session":
        """Retrieve a session if it exists, otherwise create a new one.

        Ensures that async session service methods are properly awaited.

        Args:
            session_id (str): The ID of the session to retrieve or create.

        Returns:
            Session: The retrieved or newly created session object.
        """
        logger.info("session_id: %s", session_id)
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name,
            user_id=DEFAULT_USER_ID,
            session_id=session_id,
        )
        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name,
                user_id=DEFAULT_USER_ID,
                session_id=session_id,
            )
        return session

    async def _process_request(
        self,
        new_message: types.Content,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        session_obj = await self._upsert_session(session_id)
        session_id = session_obj.id

        self._active_sessions.add(session_id)

        try:
            async for event in self.runner.run_async(
                session_id=session_id,
                user_id=DEFAULT_USER_ID,
                new_message=new_message,
            ):
                if event.is_final_response():
                    parts = []
                    if event.content:
                        parts = [
                            convert_genai_part_to_a2a(part)
                            for part in event.content.parts
                            if (part.text or part.file_data or part.inline_data)
                        ]
                    logger.debug("Yielding final response: %s", parts)
                    await task_updater.add_artifact(parts)
                    await task_updater.update_status(TaskState.completed, final=True)
                    break
                if not event.get_function_calls():
                    logger.debug("Yielding update response")
                    message_parts = []
                    if event.content:
                        message_parts = [
                            convert_genai_part_to_a2a(part)
                            for part in event.content.parts
                            if (part.text)
                        ]
                    await task_updater.update_status(
                        TaskState.working,
                        message=task_updater.new_agent_message(message_parts),
                    )
                else:
                    logger.debug("Skipping event")
        finally:
            # Remove from active sessions when done
            self._active_sessions.discard(session_id)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        # Run the agent until either complete or the task is suspended.
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        # Immediately notify that the task is submitted.
        if not context.current_task:
            await updater.update_status(TaskState.submitted)
        await updater.update_status(TaskState.working)
        await self._process_request(
            types.UserContent(
                parts=[
                    convert_a2a_part_to_genai(part) for part in context.message.parts
                ],
            ),
            context.context_id,
            updater,
        )

        logger.debug("[ADKAgentA2AExecutor] execute exiting")

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        session_id = context.context_id
        if session_id in self._active_sessions:
            logger.info("Cancellation requested for active session: %s", session_id)
            self._active_sessions.discard(session_id)
        else:
            logger.debug("Cancellation requested for inactive session: %s", session_id)

        raise ServerError(error=UnsupportedOperationError())
