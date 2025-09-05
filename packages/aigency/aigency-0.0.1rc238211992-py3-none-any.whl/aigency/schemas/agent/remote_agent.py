from pydantic import BaseModel, Field


class RemoteAgent(BaseModel):
    """Remote agent configuration."""

    name: str
    host: str
    port: int = Field(..., ge=1, le=65535)
