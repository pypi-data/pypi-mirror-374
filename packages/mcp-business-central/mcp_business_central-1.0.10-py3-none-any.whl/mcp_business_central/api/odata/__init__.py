"""
OData-related utilities for Business Central API.

This subpackage exposes OData metadata parsing and search helpers.
"""

from .metadata import (
    parse_metadata_xml,
    get_metadata_summary,
    search_entities,
    search_enums,
    search_properties,
    search_relationships,
)

__all__ = [
    "parse_metadata_xml",
    "get_metadata_summary",
    "search_entities",
    "search_enums",
    "search_properties",
    "search_relationships",
]


