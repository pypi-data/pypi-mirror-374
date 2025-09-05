from pydantic import BaseModel

class Phoenix(BaseModel):
    """Configuración del monitor Phoenix."""
    host: str
    port: int