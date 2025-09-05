import logging
import uuid
from typing import Any
from a2a.types import Message, Task
from google.adk.tools.tool_context import ToolContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Communicator:
    """Base class for Agent-to-Agent communication."""

    def __init__(self, remote_agent_connections=None):
        self.remote_agent_connections = remote_agent_connections

    async def send_message(self, agent_name: str, task: str, tool_context: ToolContext):
        """Delegate a task to a specified remote agent.

        This method sends a message to a remote agent, requesting it to perform a task.
        It handles the creation of the message payload and manages the communication
        with the remote agent.

        Args:
            agent_name: Name of the remote agent to send the task to.
            task: Detailed description of the task for the remote agent to perform.
            tool_context: Context object containing state and other information.

        Returns:
            Task object if successful, None otherwise.

        Raises:
            ValueError: If the specified agent is not found in the available connections.
        """
        logger.info(
            f"`send_message` triggered with agent_name: {agent_name}, task: {task}"
        )
        if agent_name not in self.remote_agent_connections:
            logger.error(
                f"LLM tried to call '{agent_name}' but it was not found. "
                f"Available agents: {list(self.remote_agent_connections.keys())}"
            )
            raise ValueError(f"Agent '{agent_name}' not found.")

        state = tool_context.state
        client = self.remote_agent_connections[agent_name]

        if "remote_agent_contexts" not in state:
            state["remote_agent_contexts"] = {}

        if agent_name not in state["remote_agent_contexts"]:
            logger.debug(f"Creating new context for agent: {agent_name}")
            state["remote_agent_contexts"][agent_name] = {
                "context_id": str(uuid.uuid4())
            }
        context_id = state["remote_agent_contexts"][agent_name]["context_id"]
        task_id = state.get("task_id", None)
        message_id = state.get("input_message_metadata", {}).get(
            "message_id", str(uuid.uuid4())
        )

        payload = self.create_send_message_payload(task, task_id, context_id)
        payload["message"]["message_id"] = message_id
        logger.debug("`send_message` triggered with payload: %s", payload)

        send_response = None
        async for resp in client.send_message(
            message_request=Message(**payload.get("message"))
        ):
            send_response = resp

        if isinstance(send_response, tuple):
            send_response, _ = send_response

        if not isinstance(send_response, Task):
            return None
        return send_response

    @staticmethod
    def create_send_message_payload(
        text: str,
        task_id: str | None = None,
        context_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a message payload for sending to a remote agent.

        Args:
            text: The text content of the message.
            task_id: Optional task ID to associate with the message.
            context_id: Optional context ID to associate with the message.

        Returns:
            dict: A dictionary containing the formatted message payload ready
                to be sent to a remote agent.
        """
        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": text}],
                "message_id": uuid.uuid4().hex,
            },
        }
        if task_id:
            payload["message"]["task_id"] = task_id
        if context_id:
            payload["message"]["context_id"] = context_id
        return payload
