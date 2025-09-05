"""Tool Factory for dynamically loading and managing agent tools.

This module provides a flexible way to load different types of tools based on
configuration. It uses the Strategy pattern and Pydantic for validation.
"""

import importlib
from typing import Any, Optional

from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
    StreamableHTTPConnectionParams,
)

from aigency.schemas.agent.tools import (
    FunctionTool,
    McpTool,
    McpTypeStdio,
    McpTypeStreamable,
    Tool,
    ToolType,
)
from aigency.utils.utils import expand_env_vars


class ToolGenerator:
    """Generator for creating tools based on configuration."""

    @staticmethod
    def load_function_tool(config: FunctionTool) -> Any:
        """Load a function tool from configuration."""
        try:
            module = importlib.import_module(config.module_path)
            return getattr(module, config.function_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Error loading function tool: {e}")

    @staticmethod
    def load_mcp_tool(config: McpTool) -> Any:
        """Load an MCP tool from configuration."""

        if isinstance(config.mcp_config, McpTypeStreamable):
            url = f"http://{config.mcp_config.url}:{config.mcp_config.port}{config.mcp_config.path}"
            return MCPToolset(connection_params=StreamableHTTPConnectionParams(url=url))
        elif isinstance(config.mcp_config, McpTypeStdio):
            command = config.mcp_config.command
            args = config.mcp_config.args
            env = expand_env_vars(config.mcp_config.env)

            return MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command=command, args=args, env=env
                    )
                )
            )

    STRATEGIES = {
        ToolType.MCP: load_mcp_tool,
        ToolType.FUNCTION: load_function_tool,
    }

    @staticmethod
    def create_tool(tool: Tool) -> Optional[Any]:
        """Create a tool based on its configuration.

        Args:
            tool: Tool configuration

        Returns:
            The created tool or None if creation failed

        Raises:
            ValueError: If tool type is not supported or config is invalid
        """

        return ToolGenerator.STRATEGIES[tool.type](tool)
