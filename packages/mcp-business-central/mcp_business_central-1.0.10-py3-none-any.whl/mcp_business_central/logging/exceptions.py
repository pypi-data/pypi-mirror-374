"""
Custom exceptions for the Business Central MCP server.

This module defines all custom exceptions used throughout the application
to provide clear error handling and debugging information.
"""

from typing import Optional


class BCServerError(Exception):
    """Base exception for all Business Central server errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None) -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthenticationError(BCServerError):
    """Raised when authentication with Business Central fails."""
    pass


class CompanyNotFoundError(BCServerError):
    """Raised when a requested company cannot be found."""
    pass


class ResourceNotFoundError(BCServerError):
    """Raised when a requested resource cannot be found."""
    pass


class ValidationError(BCServerError):
    """Raised when input validation fails."""
    pass


class APIError(BCServerError):
    """Raised when Business Central API returns an error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 error_code: Optional[str] = None) -> None:
        self.status_code = status_code
        super().__init__(message, error_code)


class ConfigurationError(BCServerError):
    """Raised when server configuration is invalid or missing."""
    pass
