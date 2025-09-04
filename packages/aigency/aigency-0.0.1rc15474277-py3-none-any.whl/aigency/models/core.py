"""Core models for agent configuration."""

from typing import Dict, List, Optional

from pydantic import BaseModel


class ProviderConfig(BaseModel):
    """Configuration for AI model provider."""
    name: str
    endpoint: Optional[str] = None

class ModelConfig(BaseModel):
    """Configuration for AI model."""
    name: str
    provider: Optional[ProviderConfig] = None

class Capabilities(BaseModel):
    """Agent capabilities, such as streaming."""
    streaming: Optional[bool] = None

class Skill(BaseModel):
    """Define a specific agent skill."""
    id: str
    name: str
    description: str
    tags: Optional[List[str]] = None
    examples: Optional[List[str]] = None