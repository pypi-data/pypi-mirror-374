"""
Main server module for the Business Central MCP server.

This module handles server startup, initialization, and MCP server execution.
"""

import asyncio
from .dependencies import logger, mcp


async def main() -> None:
    """
    Main entry point for the Business Central MCP server.
    
    Initializes all components and starts the MCP server to handle client requests.
    """
    try:
        # Import tools to register them with the MCP server
        from ..tools import implementations  # noqa: F401
        
        # Run the MCP server - logging happens after protocol establishment
        await mcp.run_stdio_async()
        
    except KeyboardInterrupt:
        # Silent shutdown for MCP compatibility
        pass
    except Exception as e:
        # Only log critical errors that would prevent server startup
        import sys
        print(f"Critical server error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    # Direct script execution entry point
    asyncio.run(main())