"""
Module entry point for `python -m mcp_business_central`.

Starts the MCP server and registers tools.
"""

import asyncio

from . import server as mcp


async def main() -> None:
  try:
    # Import tools to register them with the MCP server
    from .tools import mcp_tools  # noqa: F401
    await mcp.run_stdio_async()
  except KeyboardInterrupt:
    pass


def main_entry() -> None:
  asyncio.run(main())


if __name__ == "__main__":
  main_entry()


