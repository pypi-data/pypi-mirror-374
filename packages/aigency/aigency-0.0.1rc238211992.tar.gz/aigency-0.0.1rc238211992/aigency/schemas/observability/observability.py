from pydantic import BaseModel
from aigency.schemas.observability.phoenix import Phoenix

class Monitoring(BaseModel):
    """Configuración de las herramientas de monitoreo."""
    phoenix: Phoenix

class Observability(BaseModel):
    """Agrupa todas las configuraciones de observabilidad."""
    monitoring: Monitoring