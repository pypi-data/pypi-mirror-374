"""
API layer for Business Central integration.

This module provides everything needed to work with Business Central APIs:
- Configuration and settings
- HTTP client and API abstractions  
- Data models and response structures
- Company management
- OData metadata parsing
"""

from .http_client import BCAPIClient
from .companies import CompanyManager
from .config import BCServerConfig, build_business_central_url
from .entities import SchemaInfo
from .companies import Company
from .http_client import APIResponse
from . import odata

# Lazy API component singletons
_api_client = None
_company_manager = None

def get_default_api_client():
    """Get API client, creating it lazily when first needed."""
    global _api_client
    if _api_client is None:
        from ..auth import get_default_auth_manager
        from .config import get_default_config
        _api_client = BCAPIClient(get_default_config(), get_default_auth_manager())
    return _api_client

def get_default_company_manager():
    """Get company manager, creating it lazily when first needed."""
    global _company_manager
    if _company_manager is None:
        _company_manager = CompanyManager(get_default_api_client())
    return _company_manager

__all__ = [
    # Core API classes
    "BCAPIClient", "CompanyManager",
    # Configuration
    "BCServerConfig", "build_business_central_url", 
    # Models
    "Company", "SchemaInfo", "APIResponse",
    # Factory functions
    "get_default_api_client", "get_default_company_manager",
    # Modules
    "odata"
]
