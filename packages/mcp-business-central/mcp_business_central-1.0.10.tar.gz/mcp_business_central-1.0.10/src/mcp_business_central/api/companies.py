"""
Company management for Business Central operations.

This module manages company discovery, selection, and caching
for Business Central operations.
"""

import logging
from typing import List, Optional, Any, Dict
from dataclasses import dataclass
from .http_client import BCAPIClient
from ..logging.exceptions import CompanyNotFoundError

@dataclass
class Company:
  """Represents a Business Central company."""

  id: str
  name: str
  display_name: Optional[str] = None
  business_profile_id: Optional[str] = None

  @classmethod
  def from_api_response(cls, data: Dict[str, Any]) -> 'Company':
    """Create a Company instance from API response data."""
    return cls(
      id=data.get('id', ''),
      name=data.get('name', ''),
      display_name=data.get('displayName'),
      business_profile_id=data.get('businessProfileId'),
    )

logger = logging.getLogger(__name__)


class CompanyManager:
    """Manages Business Central companies and company context."""
    
    def __init__(self, api_client: BCAPIClient) -> None:
        """Initialize the company manager."""
        self.api_client = api_client
        self._companies_cache: Optional[List[Company]] = None
        self._selected_company_id: Optional[str] = None
    
    async def discover_companies(self, refresh_cache: bool = False) -> List[Company]:
        """
        Discover available companies.
        
        Args:
            refresh_cache: Whether to refresh the company cache
            
        Returns:
            List of available companies
        """
        if self._companies_cache is None or refresh_cache:
            raw = await self.api_client.discover_companies()
            self._companies_cache = [Company.from_api_response(item) for item in raw]
        
        return self._companies_cache
    
    async def get_company_by_id(self, company_id: str) -> Company:
        """
        Get a company by its ID.
        
        Args:
            company_id: The company ID to search for
            
        Returns:
            Company object
            
        Raises:
            CompanyNotFoundError: If company is not found
        """
        companies = await self.discover_companies()
        
        for company in companies:
            if company.id == company_id:
                return company
        
        raise CompanyNotFoundError(f"Company with ID {company_id} not found")
    
    async def set_active_company(self, company_id: str) -> Company:
        """
        Set the active company by ID.
        
        Args:
            company_id: Company ID to set as active
            
        Returns:
            The selected company
            
        Raises:
            CompanyNotFoundError: If company is not found
        """
        company = await self.get_company_by_id(company_id)
        self._selected_company_id = company_id
        
        logger.info(f"Set active company to: {company.name} (ID: {company_id})")
        return company
    
    async def get_active_company(self) -> Optional[Company]:
        """
        Get the currently active company.
        
        Returns:
            Active company or None if no company is selected
        """
        if not self._selected_company_id:
            return None
        
        try:
            return await self.get_company_by_id(self._selected_company_id)
        except CompanyNotFoundError:
            # Clear invalid company selection
            self._selected_company_id = None
            return None
    
    async def get_active_company_id(self) -> Optional[str]:
        """
        Get the active company ID, defaulting to first available if none selected.
        
        Returns:
            Active company ID or None if no companies available
        """
        if self._selected_company_id:
            return self._selected_company_id
        
        # Default to first company if none selected
        companies = await self.discover_companies()
        if companies:
            self._selected_company_id = companies[0].id
            logger.info(f"Auto-selected first company: {companies[0].name}")
            return self._selected_company_id
        
        return None
    
    async def get_default_company(self) -> Optional[Company]:
        """
        Get the default (first available) company.
        
        Returns:
            First available company or None if no companies exist
        """
        companies = await self.discover_companies()
        return companies[0] if companies else None
    
    def clear_cache(self) -> None:
        """Clear the companies cache."""
        self._companies_cache = None
        logger.debug("Company cache cleared")
    
    def clear_selection(self) -> None:
        """Clear the active company selection."""
        self._selected_company_id = None
        logger.info("Active company selection cleared")
