"""
Business entities and domain models.

This module defines the business domain models representing Business Central 
entities and their relationships.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


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


 
