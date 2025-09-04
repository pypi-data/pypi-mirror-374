"""Tool models for agent configuration."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class ToolType(str, Enum):
    """Enum for tool types."""
    MCP = "mcp"
    FUNCTION = "function"

class Tool(BaseModel):
    """Define an external tool that the agent can use."""
    type: ToolType
    name: str
    description: str

class FunctionTool(Tool):
    """Configuration for function-based tools."""
    module_path: str
    function_name: str

class McpTypeStreamable(BaseModel):
    """Model for streamable tool type."""
    url: str
    port: int
    path: str = "/"

class McpTypeStdio(BaseModel):
    """Model for stdio tool type."""
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None

class McpTool(Tool):
    """Configuration for MCP-based tools."""
    mcp_config: McpTypeStreamable | McpTypeStdio