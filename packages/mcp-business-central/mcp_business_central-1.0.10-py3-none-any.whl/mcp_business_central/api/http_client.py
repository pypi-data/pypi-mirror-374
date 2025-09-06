"""
Business Central API client.

This module provides the main API client for interacting with
Microsoft Dynamics 365 Business Central APIs.
"""

from typing import Any, Dict, List, Optional, Union
import aiohttp

import logging
from .config import BCServerConfig
from ..logging.exceptions import APIError, AuthenticationError
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class BCAPIClient:
    """Business Central API client for making authenticated requests."""
    
    def __init__(self, config: BCServerConfig, auth_manager: Any) -> None:
        """Initialize the API client."""
        self.config = config
        self.auth_manager = auth_manager
        
    async def _get_headers(self, include_content_type: bool = False) -> Dict[str, str]:
        """
        Get standard headers for API requests.
        
        Args:
            include_content_type: Whether to include Content-Type header
            
        Returns:
            Dict of headers
            
        Raises:
            AuthenticationError: If token acquisition fails
        """
        try:
            token = await self.auth_manager.get_access_token()
        except Exception as e:
            raise AuthenticationError(f"Failed to get access token: {str(e)}") from e
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        if include_content_type:
            headers['Content-Type'] = 'application/json'
            
        return headers
    
    def _build_url(self, resource: str, company_id: Optional[str] = None, 
                   item_id: Optional[str] = None) -> str:
        """
        Build URL for Business Central API endpoints.
        
        Args:
            resource: API resource name
            company_id: Optional company ID
            item_id: Optional item ID
            
        Returns:
            Complete API URL
        """
        if company_id:
            base = f"{self.config.base_url}/companies({company_id})"
        else:
            base = self.config.base_url
        
        if not resource:  # Empty resource for discovery
            return base
        
        if item_id:
            return f"{base}/{resource}({item_id})"
        else:
            return f"{base}/{resource}"
    
    async def _handle_etag_request(self, method: str, url: str, 
                                   headers: Dict[str, str]) -> Dict[str, str]:
        """
        Handle ETag retrieval for PATCH/DELETE requests.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            
        Returns:
            Updated headers with ETag
            
        Raises:
            APIError: If ETag retrieval fails
        """
        if method not in ['PATCH', 'DELETE']:
            return headers
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        etag = response.headers.get('ETag')
                        if etag:
                            headers = headers.copy()
                            headers['If-Match'] = etag
                        return headers
                    else:
                        error_text = await response.text()
                        raise APIError(
                            f"Failed to fetch ETag: HTTP {response.status}: {error_text}",
                            status_code=response.status
                        )
        except Exception as e:
            if isinstance(e, APIError):
                raise
            raise APIError(f"ETag retrieval failed: {str(e)}") from e
    
    async def request(self, method: str, resource: str, item_id: Optional[str] = None,
                      params: Optional[Dict[str, Any]] = None, 
                      data: Optional[Dict[str, Any]] = None,
                      company_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a Business Central API request.
        
        Args:
            method: HTTP method
            resource: API resource name
            item_id: Optional item ID
            params: Optional query parameters
            data: Optional request body data
            company_id: Optional company ID
            
        Returns:
            API response data
            
        Raises:
            APIError: If the API request fails
        """
        headers = await self._get_headers(include_content_type=(data is not None))
        url = self._build_url(resource, company_id, item_id)
        
        # Log request details (without sensitive auth header)
        log_headers = {k: '[REDACTED]' if 'Authorization' in k else v 
                      for k, v in headers.items()}
        logger.info(f"Making {method} request to: {url}")
        logger.debug(f"Request params: {params}")
        logger.debug(f"Request headers: {log_headers}")
        
        # Handle ETag for PATCH/DELETE requests
        if method in ['PATCH', 'DELETE'] and item_id:
            headers = await self._handle_etag_request(method, url, headers)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data
                ) as response:
                    
                    if response.status in [200, 201, 204]:
                        if method == 'DELETE':
                            return {"success": True}
                        else:
                            return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"API error: HTTP {response.status}: {error_text}")
                        raise APIError(
                            f"HTTP {response.status}: {error_text}",
                            status_code=response.status
                        )
                        
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise APIError(f"Request failed: {str(e)}") from e
    
    async def discover_companies(self) -> List[Dict[str, Any]]:
        """
        Discover available companies in the Business Central environment.
        
        Returns:
            List of raw company dictionaries as returned by the API
            
        Raises:
            APIError: If company discovery fails
        """
        logger.info("Discovering Business Central companies...")
        
        try:
            result = await self.request("GET", "companies")
            companies_data = result.get('value', [])
            logger.info(f"Discovered {len(companies_data)} companies")
            return companies_data
            
        except Exception as e:
            logger.error(f"Error discovering companies: {e}")
            raise APIError(f"Company discovery failed: {str(e)}") from e


@dataclass
class APIResponse:
    """Standard API response structure."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    count: Optional[int] = None
    
    @classmethod
    def success_response(cls, data: Any, count: Optional[int] = None) -> 'APIResponse':
        """Create a successful response."""
        if isinstance(data, dict) and 'value' in data:
            actual_count = len(data['value']) if count is None else count
        else:
            actual_count = 1 if count is None else count
            
        return cls(
            success=True,
            data=data if isinstance(data, dict) else {'result': data},
            count=actual_count
        )
    
    @classmethod
    def error_response(cls, error_message: str) -> 'APIResponse':
        """Create an error response."""
        return cls(
            success=False,
            error=error_message
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {'success': self.success}
        
        if self.data is not None:
            result['data'] = self.data
        if self.error is not None:
            result['error'] = self.error
        if self.count is not None:
            result['count'] = self.count
            
        return result
