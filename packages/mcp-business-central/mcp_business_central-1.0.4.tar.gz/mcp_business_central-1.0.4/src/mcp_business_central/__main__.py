"""
Module entry point for `python -m mcp_business_central`.

Starts the MCP server and registers tools.
"""

import os
import asyncio

from . import server as mcp


async def main() -> None:
  try:
    # Import tools to register them with the MCP server
    from .tools import mcp_tools  # noqa: F401

    # Configure HTTP transport per FastMCP docs
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port_str = os.getenv("MCP_PORT", "8000")
    try:
      port = int(port_str)
    except ValueError:
      port = 8000

    await mcp.run_async(transport="http", host=host, port=port)
  except KeyboardInterrupt:
    pass


def main_entry() -> None:
  asyncio.run(main())


if __name__ == "__main__":
  main_entry()


