"""
Authentication management for Business Central APIs.

This module handles OAuth2 authentication with Azure AD for accessing
Microsoft Dynamics 365 Business Central APIs.
"""

from .manager import BCAuthManager, BearerAuthManager, build_clients_from_headers

# Lazy auth manager singleton
_auth_manager = None

def get_default_auth_manager():
    """Get auth manager, creating it lazily when first needed."""
    global _auth_manager
    if _auth_manager is None:
        from ..api.config import get_default_config
        _auth_manager = BCAuthManager(get_default_config())
    return _auth_manager

__all__ = ["BCAuthManager", "BearerAuthManager", "build_clients_from_headers", "get_default_auth_manager"]
