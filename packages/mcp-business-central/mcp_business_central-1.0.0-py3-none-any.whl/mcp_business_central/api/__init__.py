"""
API layer for Business Central integration.

This module provides the HTTP client and API endpoint abstractions
for communicating with Microsoft Dynamics 365 Business Central.
"""

from .client import BCAPIClient

__all__ = ["BCAPIClient"]
