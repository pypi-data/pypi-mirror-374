import logging
import httpx
from typing import List
import asyncio

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.client import A2ACardResolver
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from aigency.agents.executor import AgentA2AExecutor
from aigency.agents.client import AgentClient
from aigency.schemas.aigency_config import AigencyConfig
from aigency.schemas.agent.remote_agent import RemoteAgent
from aigency.tools.generator import ToolGenerator
from aigency.utils.utils import generate_url, safe_async_run
from aigency.agents.communicator import Communicator
from aigency.utils.logger import get_logger

logger = get_logger()

class AgentA2AGenerator:

    @staticmethod
    def create_agent(agent_config: AigencyConfig) -> Agent:

        tools = [
            ToolGenerator.create_tool(tool_cfg) for tool_cfg in agent_config.agent.tools
        ]

        remote_agents = agent_config.agent.remote_agents
        if remote_agents:
            remote_agent_connections = AgentA2AGenerator.build_remote_agent_connections(
                agent_config
            )
            logger.info(f"Remote agent connections: {remote_agent_connections}")
            communicator = Communicator(
                remote_agent_connections=remote_agent_connections
            )
            tools.append(communicator.send_message)

        return Agent(
            name=agent_config.metadata.name,
            model=agent_config.agent.model.name,
            instruction=agent_config.agent.instruction,
            tools=tools,
        )

    @staticmethod
    def build_agent_card(agent_config: AigencyConfig) -> AgentCard:

        # TODO: Parse properly
        capabilities = AgentCapabilities(
            streaming=agent_config.service.capabilities.streaming
        )

        skills = [
            AgentSkill(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                tags=skill.tags,
                examples=skill.examples,
            )
            for skill in agent_config.agent.skills
        ]

        return AgentCard(
            name=agent_config.metadata.name,
            description=agent_config.metadata.description,
            url=agent_config.service.url,
            version=agent_config.metadata.version,
            default_input_modes=agent_config.service.interface.default_input_modes,
            default_output_modes=agent_config.service.interface.default_output_modes,
            capabilities=capabilities,
            skills=skills,
        )

    @staticmethod
    def build_executor(agent: Agent, agent_card: AgentCard) -> AgentA2AExecutor:

        runner = Runner(
            app_name=agent.name,
            agent=agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        return AgentA2AExecutor(runner=runner, card=agent_card)

    @staticmethod
    def build_remote_agent_connections(agent_config: AigencyConfig):
        """Initialize connections to all remote agents asynchronously.

        Tests each connection individually with detailed logging to help identify
        any connection issues. It attempts to connect to each remote agent address,
        retrieve its agent card, and store the connection for later use.

        Raises:
            No exceptions are raised, but errors are logged.
        """

        if not agent_config.agent.remote_agents:
            return {}

        remote_agent_configs = [
            {"url": generate_url(host=remote_agent.host, port=remote_agent.port)}
            for remote_agent in agent_config.agent.remote_agents
        ]

        async def _connect():
            remote_agent_connections = {}
            async with httpx.AsyncClient(timeout=60) as client:
                for config in remote_agent_configs:
                    address = config.get("url")
                    logger.debug(f"--- Attempting connection to: {address} ---")
                    try:
                        card_resolver = A2ACardResolver(client, address)
                        card = await card_resolver.get_agent_card()
                        remote_connection = AgentClient(agent_card=card)
                        remote_agent_connections[card.name] = remote_connection
                    except Exception as e:
                        logger.error(
                            f"--- CRITICAL FAILURE for address: {address} ---",
                            exc_info=True,
                        )
                        raise e
            return remote_agent_connections

        try:
            return safe_async_run(_connect())
        except Exception as e:
            logger.error("--- CRITICAL FAILURE", exc_info=True)
            raise e