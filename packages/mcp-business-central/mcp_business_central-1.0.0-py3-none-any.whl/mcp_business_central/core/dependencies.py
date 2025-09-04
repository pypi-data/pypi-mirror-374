"""
Dependency injection container for the Business Central MCP server.

This module provides centralized dependency injection and component
initialization for the entire application.
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..config import BCServerConfig, LoggingConfig, setup_logging, get_logger
from ..auth import BCAuthManager
from ..api import BCAPIClient
from .company_manager import CompanyManager

# Load configuration silently during import (MCP protocol requirement)
try:
    config = BCServerConfig.from_environment()
except Exception as e:
    raise

# Initialize logging with MCP-safe configuration
setup_logging()

# Enable verbose logging if requested via environment variable
import os
if os.getenv('MCP_VERBOSE', '').lower() == 'true':
    from ..config.logging import enable_verbose_logging
    enable_verbose_logging()

logger = get_logger(__name__)

# Initialize components
auth_manager = BCAuthManager(config)
api_client = BCAPIClient(config, auth_manager)
company_manager = CompanyManager(api_client)

# Initialize MCP server
mcp = FastMCP(
    name="business-central-mcp-server",
    instructions=(
        "This server provides tools to interact with Microsoft Dynamics 365 Business Central. "
        "Companies are auto-discovered and the server supports multi-tenant operations with "
        "professional-grade architecture and comprehensive business data access."
    )
)


# Legacy function wrappers for backward compatibility
# These will be removed in the future, use the new components directly

async def bc_request(method: str, resource: str, item_id: Optional[str] = None, 
                    params: Optional[dict] = None, data: Optional[dict] = None,
                    company_id: Optional[str] = None) -> dict:
    """Legacy wrapper for API requests - use api_client.request() instead."""
    from ..config.exceptions import APIError
    
    try:
        if not company_id:
            company_id = await company_manager.get_active_company_id()
        
        result = await api_client.request(method, resource, item_id, params, data, company_id)
        return result
    except APIError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


async def discover_companies():
    """Legacy wrapper for company discovery - use company_manager.discover_companies() instead."""
    try:
        companies = await company_manager.discover_companies()
        return [{"id": c.id, "name": c.name, "displayName": c.display_name} for c in companies]
    except Exception:
        return []


async def get_default_company():
    """Legacy wrapper for default company - use company_manager.get_default_company() instead."""
    try:
        company = await company_manager.get_default_company()
        return {"id": company.id, "name": company.name} if company else None
    except Exception:
        return None


async def set_company(company_id: str) -> bool:
    """Legacy wrapper for setting company - use company_manager.set_active_company() instead."""
    try:
        await company_manager.set_active_company(company_id)
        return True
    except Exception:
        return False


async def get_active_company_id() -> Optional[str]:
    """Legacy wrapper for active company ID - use company_manager.get_active_company_id() instead."""
    try:
        return await company_manager.get_active_company_id()
    except Exception:
        return None
