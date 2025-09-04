"""Agent generator module for creating A2A agents."""

from typing import Any, Dict, List

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from aigency.agents.executor import AgentA2AExecutor
from aigency.schemas.aigency_config import AigencyConfig
from aigency.tools.generator import ToolGenerator


class AgentA2AGenerator:
    """Generator for creating A2A agents and related components."""

    @staticmethod
    def create_agent(agent_config: AigencyConfig) -> Agent:

        tools = [
            ToolGenerator.create_tool(tool_cfg) for tool_cfg in agent_config.agent.tools
        ]

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
