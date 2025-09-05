from pydantic import BaseModel

class Capabilities(BaseModel):
    """Capacidades técnicas del servicio del agente."""
    streaming: bool