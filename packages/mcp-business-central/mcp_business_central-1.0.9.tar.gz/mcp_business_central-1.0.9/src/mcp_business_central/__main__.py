"""
Module entry point for `python -m mcp_business_central`.

Starts the MCP server and registers tools.
"""

import os

from .server import mcp


def main_entry() -> None:
  try:
    # Configure HTTP transport per FastMCP docs
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port_str = os.getenv("MCP_PORT", "8000")
    try:
      port = int(port_str)
    except ValueError:
      port = 8000

    # Use the synchronous run() method with HTTP transport
    mcp.run(transport="http", host=host, port=port)
  except KeyboardInterrupt:
    pass


if __name__ == "__main__":
  main_entry()


