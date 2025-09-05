from pydantic import BaseModel


class Metadata(BaseModel):
    """Metadatos descriptivos del agente."""
    name: str
    version: str
    description: str