"""
MCP tools for Business Central integration.

This module contains all the MCP tools that provide the interface 
for interacting with Business Central through the MCP protocol.
"""

# Tools are automatically registered when the module is imported
# Import the tools to register them all with the MCP server
from . import mcp_tools

__all__ = ["mcp_tools"]
