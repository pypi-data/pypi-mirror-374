from pydantic import BaseModel
from aigency.schemas.service.interface import Interface
from aigency.schemas.service.capabilities import Capabilities

class Service(BaseModel):
    """Configuración de red y comunicación del agente."""
    url: str
    interface: Interface
    capabilities: Capabilities