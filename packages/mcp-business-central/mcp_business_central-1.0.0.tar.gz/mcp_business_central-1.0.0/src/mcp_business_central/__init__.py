"""
Microsoft Dynamics 365 Business Central MCP Server.

This package provides MCP tools for interacting with Business Central APIs,
featuring OAuth2 authentication, company management, and comprehensive
business data access with a professional, scalable architecture.
"""

import asyncio
from .core import main

def main_entry():
    """Main entry point for the package."""
    asyncio.run(main())

__all__ = [
    "main_entry",
    "main",
    # Core modules
    "core",
    "api", 
    "auth",
    "models",
    "tools",
    "config"
]

__version__ = "1.0.0"
