"""
Authentication management for Business Central API.

This module handles OAuth2 authentication with Azure AD for Business Central,
providing token management and caching functionality.
"""

import asyncio
import time
from typing import Optional
import msal

import logging
from ..config import BCServerConfig
from ..config.exceptions import AuthenticationError

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
