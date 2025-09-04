"""
Core business logic for Business Central MCP integration.

This module contains the central business logic components including
server setup and company management.
"""

from .server import main
from .company_manager import CompanyManager

__all__ = ["main", "CompanyManager"]
