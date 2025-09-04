#!/usr/bin/env python3
"""
Main entry point for the Business Central MCP Server.

This file allows the package to be executed with: python -m mcp_business_central
"""

import asyncio
from .core.server import main

if __name__ == "__main__":
    asyncio.run(main())
