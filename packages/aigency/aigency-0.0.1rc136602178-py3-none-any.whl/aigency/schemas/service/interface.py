from typing import List
from pydantic import BaseModel

class Interface(BaseModel):
    """Define los modos de comunicación del agente."""
    default_input_modes: List[str]
    default_output_modes: List[str]