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
        config = get_default_config()
        if config is None:
            return None  # No default auth manager when no config
        _auth_manager = BCAuthManager(config)
    return _auth_manager

__all__ = ["BCAuthManager", "BearerAuthManager", "build_clients_from_headers", "get_default_auth_manager"]
