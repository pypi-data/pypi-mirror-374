"""
Authentication management for Business Central APIs.

This module handles OAuth2 authentication with Azure AD for accessing
Microsoft Dynamics 365 Business Central APIs.
"""

from .manager import BCAuthManager

__all__ = ["BCAuthManager"]
