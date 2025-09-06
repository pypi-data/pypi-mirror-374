"""
Business Central MCP Server setup and initialization.

This module handles MCP server setup and request-scoped dependency injection.
All component factories have been moved to their respective semantic modules.
"""

from typing import Tuple, Any, Mapping
from fastmcp import FastMCP

from .logging import setup_logging, get_logger
from .auth import build_clients_from_headers, get_default_auth_manager
from .api import BCAPIClient, CompanyManager, get_default_api_client, get_default_company_manager

# Initialize logging with MCP-safe configuration
setup_logging()

# Enable verbose logging if requested via environment variable
import os
if os.getenv('MCP_VERBOSE', '').lower() == 'true':
    from .logging import enable_verbose_logging
    enable_verbose_logging()

logger = get_logger(__name__)

# Initialize MCP server
mcp = FastMCP(
    name="mcp-business-central-server",
    instructions=(
        "This server provides tools to interact with Microsoft Dynamics 365 Business Central. "
        "Companies are auto-discovered and the server supports multi-tenant operations with "
        "professional-grade architecture and comprehensive business data access."
    )
)


# --- Request-scoped auth support (headers-driven) ---


def get_request_clients(ctx: Any) -> Tuple[BCAPIClient, CompanyManager]:
    """
    Resolve per-request clients from context headers, or fall back to default singletons.
    
    This is the core dependency injection function that enables both:
    1. Header-based per-request authentication (FastMCP Cloud multi-tenant)
    2. Environment-based singleton authentication (local development)
    
    Args:
        ctx: MCP request context containing headers
        
    Returns:
        Tuple of (BCAPIClient, CompanyManager) for the request
        
    Raises:
        RuntimeError: If neither headers nor environment provide valid authentication
    """
    try:
        headers: Mapping[str, str] = {}
        req = getattr(ctx, 'request', None)
        if req is not None:
            headers = getattr(req, 'headers', {}) or {}
        
        built = build_clients_from_headers(headers)
        if built is not None:
            return built
    except Exception as e:
        logger.debug(f"Header parsing failed: {e}")
        # Continue to fallback

    # Fallback to environment-backed default singletons
    try:
        return get_default_api_client(), get_default_company_manager()
    except RuntimeError as e:
        # No environment config and no valid headers
        logger.error("Authentication failed: No valid environment variables or request headers found")
        raise RuntimeError("Missing required environment variables: BC_TENANT_ID, BC_CLIENT_ID, BC_CLIENT_SECRET") from e


# --- Tool registration ---
# Importing the tools module registers all tools on the FastMCP instance.
# Do this after mcp, logger, and get_request_clients are defined to avoid circular import issues.
try:
    from .tools import mcp_tools  # noqa: F401
except Exception as _tool_import_error:
    logger.error(f"Failed to register tools: {_tool_import_error}")

# Make the server available for FastMCP CLI
server = mcp
