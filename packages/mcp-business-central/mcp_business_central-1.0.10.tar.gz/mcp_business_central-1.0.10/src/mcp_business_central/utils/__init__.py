"""
Utility functions for the Business Central MCP server.

This module contains various utility functions used throughout the application
for data validation, conversion, and other common operations.
"""

import logging
from typing import Any, Union, Optional
from ..logging.exceptions import ValidationError

logger = logging.getLogger(__name__)


def validate_resource_name(resource: str) -> str:
    """
    Validate and normalize a resource name.
    
    Args:
        resource: Resource name to validate
        
    Returns:
        Normalized resource name
        
    Raises:
        ValidationError: If resource name is invalid
    """
    if not resource or not isinstance(resource, str):
        raise ValidationError("Resource name must be a non-empty string")
    
    # Remove any leading/trailing whitespace
    resource = resource.strip()
    
    if not resource:
        raise ValidationError("Resource name cannot be empty")
    
    return resource


def validate_field_name(field: str) -> str:
    """
    Validate a field name.
    
    Args:
        field: Field name to validate
        
    Returns:
        Validated field name
        
    Raises:
        ValidationError: If field name is invalid
    """
    if not field or not isinstance(field, str):
        raise ValidationError("Field name must be a non-empty string")
    
    field = field.strip()
    if not field:
        raise ValidationError("Field name cannot be empty")
    
    return field


def escape_odata_string(value: str) -> str:
    """
    Escape a string value for use in OData filters.
    
    Args:
        value: String value to escape
        
    Returns:
        Escaped string value
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Escape single quotes by doubling them
    return value.replace("'", "''")


def build_odata_filter(field: str, value: Any, operator: str = "eq") -> str:
    """
    Build an OData filter expression.
    
    Args:
        field: Field name
        value: Field value
        operator: OData operator (eq, ne, gt, lt, etc.)
        
    Returns:
        OData filter expression
        
    Raises:
        ValidationError: If inputs are invalid
    """
    field = validate_field_name(field)
    
    if value is None:
        raise ValidationError("Filter value cannot be None")
    
    # Handle different value types
    if isinstance(value, str):
        escaped_value = escape_odata_string(value)
        return f"{field} {operator} '{escaped_value}'"
    elif isinstance(value, (int, float)):
        return f"{field} {operator} {value}"
    elif isinstance(value, bool):
        return f"{field} {operator} {str(value).lower()}"
    else:
        # Convert to string and escape
        escaped_value = escape_odata_string(str(value))
        return f"{field} {operator} '{escaped_value}'"


def sanitize_log_data(data: Any, max_length: int = 1000) -> str:
    """
    Sanitize data for logging by limiting length and removing sensitive info.
    
    Args:
        data: Data to sanitize
        max_length: Maximum length of the sanitized string
        
    Returns:
        Sanitized string representation
    """
    if data is None:
        return "None"
    
    # Convert to string
    data_str = str(data)
    
    # Redact potential sensitive information
    sensitive_patterns = [
        ('authorization', '[REDACTED]'),
        ('password', '[REDACTED]'),
        ('secret', '[REDACTED]'),
        ('token', '[REDACTED]'),
        ('key', '[REDACTED]')
    ]
    
    data_lower = data_str.lower()
    for pattern, replacement in sensitive_patterns:
        if pattern in data_lower:
            # This is a simple approach - in production you might want more sophisticated detection
            data_str = f"[POTENTIALLY SENSITIVE DATA: {len(data_str)} chars]"
            break
    
    # Limit length
    if len(data_str) > max_length:
        data_str = data_str[:max_length] + "..."
    
    return data_str


def convert_to_int(value, param_name, allow_negative=False):
    """
    Convert a value to integer, handling both string and integer inputs.
    
    Args:
        value: Value to convert (int, str, or None)
        param_name: Name of the parameter for error messages
        allow_negative: Whether to allow negative values (default: False)
    
    Returns:
        int or None: Converted integer value or None if input was None
    
    Raises:
        ValidationError: If value cannot be converted to valid integer
    """
    if value is None:
        return None
    
    try:
        int_value = int(value)
        if not allow_negative and int_value < 0:
            raise ValidationError(f"'{param_name}' parameter must be non-negative, got {int_value}")
        return int_value
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid '{param_name}' parameter: must be a valid integer, got {value}")


