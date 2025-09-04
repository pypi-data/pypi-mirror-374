from typing import Optional
from pydantic import BaseModel

class ProviderConfig(BaseModel):
    """Configuration for AI model provider."""
    name: str
    endpoint: Optional[str] = None

class AgentModel(BaseModel):
    """Configuration for AI model."""
    name: str
    provider: Optional[ProviderConfig] = None