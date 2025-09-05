import uuid
from typing import Any, Awaitable, List

from a2a.types import Message, Task
from google.adk.tools.tool_context import ToolContext

from aigency.utils.logger import get_logger

logger = get_logger()

class Communicator:
    """Clase base para la comunicación entre agentes (Agent-to-Agent)."""

    def __init__(self, remote_agent_connections: dict[str, Any] | None = None):
        """Inicializa el comunicador con las conexiones a los agentes remotos.

        Args:
            remote_agent_connections: Un diccionario que mapea nombres de agentes
                a sus objetos de conexión de cliente.
        """
        self.remote_agent_connections: dict[str, Any] = remote_agent_connections or {}

    async def send_message(
        self, agent_name: str, task: str, tool_context: ToolContext
    ) -> Awaitable[Task | None]:
        """Delega una tarea a un agente remoto específico.

        Este método envía un mensaje a un agente remoto, solicitando que realice una
        tarea. Gestiona la creación del payload del mensaje y la comunicación.

        Args:
            agent_name: Nombre del agente remoto al que se envía la tarea.
            task: Descripción detallada de la tarea para el agente remoto.
            tool_context: Objeto de contexto que contiene el estado y otra información.

        Returns:
            Un objeto Task si la comunicación es exitosa, o None en caso contrario.

        Raises:
            ValueError: Si el agente especificado no se encuentra en las conexiones.
        """
        logger.info(
            f"`send_message` iniciado para el agente: '{agent_name}' con la tarea: '{task}'"
        )
        client = self.remote_agent_connections.get(agent_name)
        if not client:
            available_agents = list(self.remote_agent_connections.keys())
            logger.error(
                f"El LLM intentó llamar a '{agent_name}', pero no se encontró. "
                f"Agentes disponibles: {available_agents}"
            )
            raise ValueError(f"Agente '{agent_name}' no encontrado. Agentes disponibles: {available_agents}")

        state = tool_context.state

        # Simplifica la creación y obtención de contextos de agente usando setdefault
        contexts = state.setdefault("remote_agent_contexts", {})
        agent_context = contexts.setdefault(agent_name, {"context_id": str(uuid.uuid4())})
        context_id = agent_context["context_id"]

        # Obtiene IDs de forma más segura y clara
        task_id = state.get("task_id")
        input_metadata = state.get("input_message_metadata", {})
        message_id = input_metadata.get("message_id")

        # El message_id se pasa directamente al creador del payload
        payload = self.create_send_message_payload(
            text=task, task_id=task_id, context_id=context_id, message_id=message_id
        )
        logger.debug("`send_message` con el siguiente payload: %s", payload)

        send_response = None
        # Este bucle está diseñado para consumir un generador asíncrono y obtener
        # la última respuesta, que suele ser el resultado final.
        async for resp in client.send_message(
            message_request=Message(**payload["message"])
        ):
            send_response = resp

        if isinstance(send_response, tuple):
            send_response, _ = send_response

        if not isinstance(send_response, Task):
            logger.warning(
                f"La respuesta recibida del agente '{agent_name}' no es un objeto Task. "
                f"Tipo recibido: {type(send_response)}"
            )
            return None

        return send_response

    @staticmethod
    def create_send_message_payload(
        text: str,
        task_id: str | None = None,
        context_id: str | None = None,
        message_id: str | None = None,
    ) -> dict[str, Any]:
        """Crea el payload de un mensaje para enviarlo a un agente remoto.

        Args:
            text: El contenido de texto del mensaje.
            task_id: ID de tarea opcional para asociar con el mensaje.
            context_id: ID de contexto opcional para asociar con el mensaje.
            message_id: ID de mensaje opcional. Si es None, se generará uno nuevo.

        Returns:
            Un diccionario que contiene el payload del mensaje formateado.
        """
        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": text}],
                "message_id": message_id or uuid.uuid4().hex,
            },
        }
        if task_id:
            payload["message"]["task_id"] = task_id
        if context_id:
            payload["message"]["context_id"] = context_id
        return payload