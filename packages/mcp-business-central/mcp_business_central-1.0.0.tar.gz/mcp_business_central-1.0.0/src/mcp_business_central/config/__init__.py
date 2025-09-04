"""
Configuration and utility modules for Business Central MCP server.

This module provides configuration management, logging setup, exceptions,
and utility functions used throughout the application.
"""

from .settings import BCServerConfig, LoggingConfig
from .exceptions import (
    BCServerError, AuthenticationError, CompanyNotFoundError,
    ResourceNotFoundError, ValidationError, APIError, ConfigurationError
)
from .logging import setup_logging, get_logger
from .utils import (
    safe_int_convert, validate_resource_name, validate_field_name,
    build_odata_filter, escape_odata_string, sanitize_log_data
)

__all__ = [
    # Configuration
    "BCServerConfig", "LoggingConfig",
    # Exceptions
    "BCServerError", "AuthenticationError", "CompanyNotFoundError",
    "ResourceNotFoundError", "ValidationError", "APIError", "ConfigurationError",
    # Logging
    "setup_logging", "get_logger",
    # Utilities
    "safe_int_convert", "validate_resource_name", "validate_field_name",
    "build_odata_filter", "escape_odata_string", "sanitize_log_data"
]
