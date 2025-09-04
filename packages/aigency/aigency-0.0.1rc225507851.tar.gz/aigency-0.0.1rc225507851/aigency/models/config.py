"""Configuration models for agents."""

from typing import List, Optional, Union

from pydantic import BaseModel

from aigency.models.core import Capabilities, ModelConfig, Skill
from aigency.models.tools import FunctionTool, McpTool, Tool

#class SecurityScheme(BaseModel):
#    """Define un esquema de seguridad individual."""
#    type: str
#    description: Optional[str] = None
#    scheme: str
#    bearerFormat: Optional[str] = None
#
#class AuthConfig(BaseModel):
#    """Configuración de autenticación."""
#    type: str
#    securitySchemes: Optional[Dict[str, SecurityScheme]] = None
#    security: Optional[List[Dict[str, List[str]]]] = None

# --- Modelos para secciones opcionales ---

#class MonitoringConfig(BaseModel):
#    """Configuración de monitorización y observabilidad."""
#    phoenix_host: Optional[str] = None
#    phoenix_port: Optional[int] = None

#class RemoteAgent(BaseModel):
#    """Configuración para la comunicación con un agente remoto."""
#    name: str
#    host: str
#    port: int
    #auth: Optional[AuthConfig] = None # Reutilizamos la configuración de Auth

# --- Clase Principal que une todo ---

class AgentConfig(BaseModel):
    """Root Pydantic model for complete agent configuration."""
    # Configuración Básica
    name: str
    description: str
    url: str
    version: str
    default_input_modes: Optional[List[str]] = None
    default_output_modes: Optional[List[str]] = None
    capabilities: Optional[Capabilities] = None

    # Autenticación
    #auth: Optional[AuthConfig] = None
    
    # Configuración del Modelo
    model: ModelConfig
        
    # Comportamiento
    instruction: Optional[str] = None
    skills: Optional[List[Skill]] = None

    # Herramientas
    tools: Optional[List[Union[FunctionTool, McpTool, Tool]]] = None

    # Comunicación Multi-Agente
    #remote_agents_addresses: Optional[List[RemoteAgent]] = None
    
    # Monitorización
    #monitoring: Optional[MonitoringConfig] = None
    

