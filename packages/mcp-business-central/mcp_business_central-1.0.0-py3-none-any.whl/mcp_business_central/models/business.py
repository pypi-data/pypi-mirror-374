"""
Business entities and domain models.

This module defines the business domain models representing
Business Central entities and their relationships.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


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
            business_profile_id=data.get('businessProfileId')
        )


@dataclass
class Resource:
    """Represents a Business Central API resource."""
    
    name: str
    kind: str
    url: str
    scope: str  # 'global' or 'company'


@dataclass
class SchemaInfo:
    """Schema information for a Business Central resource."""
    
    resource: str
    fields: List[str]
    sample_item: Optional[Dict[str, Any]] = None
    company_id: Optional[str] = None
    
    @property
    def field_count(self) -> int:
        """Get the number of fields in the schema."""
        return len(self.fields)
    
    @property
    def has_data(self) -> bool:
        """Check if schema has sample data."""
        return self.sample_item is not None and len(self.fields) > 0
