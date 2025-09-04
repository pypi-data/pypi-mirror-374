"""Agent generator module for creating A2A agents."""

from typing import Any, Dict, List

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from aigency.agents.executor import AgentA2AExecutor
from aigency.models.config import AgentConfig
from aigency.tools.generator import ToolGenerator


class AgentA2AGenerator:
    """Generator for creating A2A agents and related components."""

    @staticmethod
    def create_agent(agent_config: AgentConfig) -> Agent:

        tools = [ToolGenerator.create_tool(tool_cfg) for tool_cfg in agent_config.tools]
        
        return Agent(
            name=agent_config.name,
            model=agent_config.model.name,
            instruction=agent_config.instruction,
            tools=tools,
        )

    @staticmethod
    def build_agent_card(agent_config: AgentConfig) -> AgentCard:

        # TODO: Parse properly
        capabilities = AgentCapabilities(streaming=agent_config.capabilities.streaming)

        skills = [
            AgentSkill(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                tags=skill.tags,
                examples=skill.examples,
            )
            for skill in agent_config.skills
        ]

        return AgentCard(
            name=agent_config.name,
            description=agent_config.description,
            url=agent_config.url,
            version=agent_config.version,
            default_input_modes=agent_config.default_input_modes,
            default_output_modes=agent_config.default_output_modes,
            capabilities=capabilities,
            skills=skills,
        )

    @staticmethod
    def build_executor(
        agent: Agent, agent_card: AgentCard
    ) -> AgentA2AExecutor:

        runner = Runner(
            app_name=agent.name,
            agent=agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        return AgentA2AExecutor(runner=runner, card=agent_card)
