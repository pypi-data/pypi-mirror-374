"""
Microsoft Dynamics 365 Business Central MCP Server.

This package provides MCP tools for interacting with Business Central APIs,
featuring OAuth2 authentication, company management, and comprehensive
business data access with a professional, scalable architecture.
"""

from .server import mcp
server = mcp

__all__ = [
    # Entrypoints
    "server",  # FastMCP Cloud entry point
    "mcp",     # Direct MCP server access
    # Main modules
    "api",      # Everything to work with BC APIs
    "auth",     # Everything to work with BC auth  
    "tools",    # MCP tools definitions
    "logging",  # Logging and error handling
    "utils"     # Helper functions
]

__version__ = "1.0.0"
