import httpx
 
from a2a.client.client import ClientConfig
from a2a.client.client_factory import ClientFactory
from a2a.types import AgentCard, Message, SendMessageResponse
#TODO: Enable when auth is implemented
#from a2a.client.auth.interceptor import AuthInterceptor


class AgentClient:
    """A class to hold the connections to the remote agents.

    This class manages connections to remote agents using the A2A protocol.
    It provides methods for retrieving agent information and sending messages
    to remote agents.

    Attributes:
        _httpx_client (httpx.AsyncClient): The HTTP client used for asynchronous requests.
        agent_card (AgentCard): The agent card containing metadata about the remote agent.
    """

    def __init__(self, agent_card: AgentCard):
        """Initialize a connection to a remote agent.

        Args:
            agent_card (AgentCard): The agent card containing metadata about the remote agent.

        Raises:
            None

        Returns:
            None
        """
        self._httpx_client = httpx.AsyncClient(timeout=60)
        self.card = agent_card

        config = ClientConfig(httpx_client=self._httpx_client)
        factory = ClientFactory(config=config)
        self.agent_client = factory.create(agent_card)

    def get_agent(self) -> AgentCard:
        """Get the agent card for this remote agent connection.

        Returns:
            AgentCard: The agent card containing metadata about the remote agent.
        """
        return self.card

    async def send_message(self, message_request: Message) -> SendMessageResponse:
        """Send a message to the remote agent.

        Args:
            message_request (Message): The message request to send to the remote agent.

        Returns:
            SendMessageResponse: The response from the remote agent.
        """
        async for response in self.agent_client.send_message(message_request):
            yield response
