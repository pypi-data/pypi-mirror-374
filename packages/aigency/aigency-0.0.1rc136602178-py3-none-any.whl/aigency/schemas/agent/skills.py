from pydantic import BaseModel
from typing import List

class Skill(BaseModel):
    """Define una habilidad específica del agente."""
    id: str
    name: str
    description: str
    tags: List[str]
    examples: List[str]