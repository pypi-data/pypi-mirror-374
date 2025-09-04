"""
API response structures and data transfer objects.

This module defines the standard response structures used
for API communication and data transfer.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


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
