"""
Authentication management for Business Central API.

This module handles OAuth2 authentication with Azure AD for Business Central,
providing token management and caching functionality.
"""

import asyncio
import time
from typing import Optional, Tuple, Any, Mapping
import msal

import logging
from ..api.config import BCServerConfig
from ..logging.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class BCAuthManager:
    """Manages OAuth2 authentication with Azure AD for Business Central."""
    
    def __init__(self, config: BCServerConfig) -> None:
        """Initialize the auth manager with configuration."""
        self.config = config
        self._client_app = msal.ConfidentialClientApplication(
            client_id=config.client_id,
            client_credential=config.client_secret,
            authority=f"https://login.microsoftonline.com/{config.tenant_id}"
        )
        self._scopes = ["https://api.businesscentral.dynamics.com/.default"]
        
        # Token caching
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        
    async def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            str: Valid access token
            
        Raises:
            AuthenticationError: If token acquisition fails
        """
        current_time = time.time()
        
        # Check if we have a valid cached token (with 5-minute buffer)
        if self._access_token and current_time < self._token_expires_at - 300:
            return self._access_token
        
        logger.info("Acquiring new access token...")
        
        try:
            # Use client credentials flow for service-to-service authentication
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self._client_app.acquire_token_for_client(scopes=self._scopes)
            )
            
            if "access_token" in result:
                self._access_token = result["access_token"]
                self._token_expires_at = current_time + result.get("expires_in", 3600)
                logger.info("Successfully acquired access token")
                return self._access_token
            else:
                error_msg = result.get('error_description', 'Unknown authentication error')
                logger.error(f"Failed to acquire token: {error_msg}")
                raise AuthenticationError(f"Authentication failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error acquiring access token: {e}")
            raise AuthenticationError(f"Token acquisition error: {str(e)}") from e
    
    def invalidate_token(self) -> None:
        """Invalidate the current cached token."""
        self._access_token = None
        self._token_expires_at = 0
        logger.info("Token cache invalidated")
    
    @property
    def is_token_valid(self) -> bool:
        """Check if the current token is valid."""
        current_time = time.time()
        return bool(self._access_token and current_time < self._token_expires_at - 60)


class BearerAuthManager:
    """Simple auth manager that returns a pre-provided bearer token."""

    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    async def get_access_token(self) -> str:
        return self._access_token


def _lower_headers(headers: Mapping[str, str]) -> Mapping[str, str]:
    """
    Convert header keys to lowercase for case-insensitive lookup.
    
    Args:
        headers: Dictionary of HTTP headers
        
    Returns:
        Dictionary with lowercase keys
    """
    try:
        return {str(k).lower(): v for k, v in headers.items()}
    except Exception:
        return {}


def build_clients_from_headers(headers: Mapping[str, str]) -> Optional[Tuple[Any, Any]]:
    """Build API and company managers from HTTP headers if present.

    Supported headers (case-insensitive):
      - Authorization: Bearer <token>
      - X-BC-Tenant-Id: Tenant GUID or name (required for base URL)
      - X-BC-Environment: production|sandbox (default production)
      - X-BC-Client-Id / X-BC-Client-Secret (for client credentials path)
      
    Args:
        headers: HTTP headers dictionary
        
    Returns:
        Tuple of (BCAPIClient, CompanyManager) or None if headers insufficient
    """
    # Import here to avoid circular imports
    from ..api import BCAPIClient
    from ..api.companies import CompanyManager
    
    h = _lower_headers(headers or {})

    tenant_id = h.get('x-bc-tenant-id')
    environment = h.get('x-bc-environment', 'production')
    authz = h.get('authorization') or ''
    client_id = h.get('x-bc-client-id')
    client_secret = h.get('x-bc-client-secret')

    if not tenant_id:
        # Cannot construct base_url without tenant
        return None

    # Use the factory method to avoid duplicating config logic
    cfg = BCServerConfig.from_headers(
        tenant_id=tenant_id,
        environment=environment,
        client_id=client_id or "",
        client_secret=client_secret or ""
    )

    # Prefer bearer token if provided
    if authz.lower().startswith('bearer '):
        token = authz.split(' ', 1)[1].strip()
        auth = BearerAuthManager(token)
        api = BCAPIClient(cfg, auth)
        return api, CompanyManager(api)

    # Fall back to client credentials if both present
    if client_id and client_secret:
        auth = BCAuthManager(cfg)
        api = BCAPIClient(cfg, auth)
        return api, CompanyManager(api)

    return None
