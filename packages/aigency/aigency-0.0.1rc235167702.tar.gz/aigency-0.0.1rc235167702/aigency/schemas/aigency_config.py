from pydantic import BaseModel
from typing import Optional
from aigency.schemas.observability.observability import Observability
from aigency.schemas.metadata.metadata import Metadata
from aigency.schemas.agent.agent import Agent
from aigency.schemas.service.service import Service

class AigencyConfig(BaseModel):
    """Root Pydantic model for complete agent configuration."""

    metadata: Metadata
    service: Service
    agent: Agent
    observability: Optional[Observability] = None
