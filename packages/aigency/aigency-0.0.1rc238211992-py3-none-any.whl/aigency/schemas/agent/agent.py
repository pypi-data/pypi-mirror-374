from pydantic import BaseModel
from typing import List, Optional
from aigency.schemas.agent.model import AgentModel
from aigency.schemas.agent.skills import Skill
from aigency.schemas.agent.tools import Tool
from aigency.schemas.agent.remote_agent import RemoteAgent


class Agent(BaseModel):
    """El 'cerebro' del agente: su lógica, modelo y capacidades."""

    model: AgentModel
    instruction: str
    skills: List[Skill]
    tools: Optional[List[Tool]] = []
    remote_agents: Optional[List[RemoteAgent]] = []
