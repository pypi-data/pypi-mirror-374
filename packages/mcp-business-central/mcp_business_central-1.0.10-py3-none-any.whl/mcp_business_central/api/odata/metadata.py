"""
OData metadata parsing utilities for Business Central.

This module contains utility functions for parsing and searching OData XML metadata
from Microsoft Dynamics 365 Business Central APIs.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Define OData namespaces used in Business Central metadata
ODATA_NAMESPACES = {
    'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
    'edm': 'http://docs.oasis-open.org/odata/ns/edm'
}


def parse_metadata_xml(xml_content: str) -> ET.Element:
    """
    Parse OData metadata XML and return the schema element.
    
    Args:
        xml_content: Raw XML metadata content
        
    Returns:
        Schema element from the parsed XML
        
    Raises:
        ET.ParseError: If XML parsing fails
        ValueError: If schema element is not found
    """
    root = ET.fromstring(xml_content)
    schema = root.find('.//edm:Schema', ODATA_NAMESPACES)
    
    if schema is None:
        raise ValueError("Could not find schema element in metadata XML")
    
    return schema


def get_metadata_summary(schema: ET.Element) -> Dict[str, Any]:
    """
    Get a summary of all entities, enums, and complex types in the metadata.
    
    Args:
        schema: Schema element from parsed OData metadata
        
    Returns:
        Dictionary containing summary information
    """
    summary = {
        "total_entities": 0,
        "total_enums": 0,
        "total_complex_types": 0,
        "entity_names": [],
        "enum_names": [],
        "complex_type_names": []
    }
    
    # Count and list EntityTypes
    for entity in schema.findall('.//edm:EntityType', ODATA_NAMESPACES):
        name = entity.get('Name')
        if name:
            summary["entity_names"].append(name)
            summary["total_entities"] += 1
    
    # Count and list EnumTypes
    for enum in schema.findall('.//edm:EnumType', ODATA_NAMESPACES):
        name = enum.get('Name')
        if name:
            summary["enum_names"].append(name)
            summary["total_enums"] += 1
    
    # Count and list ComplexTypes
    for complex_type in schema.findall('.//edm:ComplexType', ODATA_NAMESPACES):
        name = complex_type.get('Name')
        if name:
            summary["complex_type_names"].append(name)
            summary["total_complex_types"] += 1
    
    return summary


def search_entities(schema: ET.Element, search_term: str, 
                   include_properties: bool = True, 
                   include_relationships: bool = True) -> List[Dict[str, Any]]:
    """
    Search for entities matching the search term.
    
    Args:
        schema: Schema element from parsed OData metadata
        search_term: Search term to match against entity names (case-insensitive)
        include_properties: Whether to include property details
        include_relationships: Whether to include navigation properties
        
    Returns:
        List of matching entity information dictionaries
    """
    entities = []
    
    for entity in schema.findall('.//edm:EntityType', ODATA_NAMESPACES):
        name = entity.get('Name', '')
        if search_term in name.lower():
            entity_info = {
                "name": name,
                "abstract": entity.get('Abstract', 'false') == 'true'
            }
            
            # Get key properties
            key_elem = entity.find('edm:Key', ODATA_NAMESPACES)
            if key_elem is not None:
                keys = []
                for prop_ref in key_elem.findall('edm:PropertyRef', ODATA_NAMESPACES):
                    keys.append(prop_ref.get('Name'))
                entity_info['key_properties'] = keys
            
            # Get properties if requested
            if include_properties:
                entity_info['properties'] = _extract_entity_properties(entity)
            
            # Get navigation properties (relationships) if requested
            if include_relationships:
                entity_info['navigation_properties'] = _extract_navigation_properties(entity)
            
            entities.append(entity_info)
    
    return entities


def search_enums(schema: ET.Element, search_term: str) -> List[Dict[str, Any]]:
    """
    Search for enums matching the search term.
    
    Args:
        schema: Schema element from parsed OData metadata
        search_term: Search term to match against enum names (case-insensitive)
        
    Returns:
        List of matching enum information dictionaries
    """
    enums = []
    
    for enum in schema.findall('.//edm:EnumType', ODATA_NAMESPACES):
        name = enum.get('Name', '')
        if search_term in name.lower():
            enum_info = {
                "name": name,
                "members": []
            }
            
            for member in enum.findall('edm:Member', ODATA_NAMESPACES):
                member_info = {
                    "name": member.get('Name'),
                    "value": member.get('Value')
                }
                enum_info['members'].append(member_info)
            
            enums.append(enum_info)
    
    return enums


def search_properties(schema: ET.Element, search_term: str) -> List[Dict[str, Any]]:
    """
    Search for properties matching the search term across all entities.
    
    Args:
        schema: Schema element from parsed OData metadata
        search_term: Search term to match against property names (case-insensitive)
        
    Returns:
        List of entities containing matching properties
    """
    properties_found = []
    
    for entity in schema.findall('.//edm:EntityType', ODATA_NAMESPACES):
        entity_name = entity.get('Name', '')
        matching_props = []
        
        for prop in entity.findall('edm:Property', ODATA_NAMESPACES):
            prop_name = prop.get('Name', '')
            if search_term in prop_name.lower():
                prop_info = {
                    "name": prop_name,
                    "type": prop.get('Type'),
                    "nullable": prop.get('Nullable', 'true') == 'true'
                }
                max_length = prop.get('MaxLength')
                if max_length:
                    prop_info['max_length'] = max_length
                matching_props.append(prop_info)
        
        if matching_props:
            properties_found.append({
                "entity": entity_name,
                "properties": matching_props
            })
    
    return properties_found


def search_relationships(schema: ET.Element, search_term: str) -> List[Dict[str, Any]]:
    """
    Search for navigation properties/relationships matching the search term.
    
    Args:
        schema: Schema element from parsed OData metadata
        search_term: Search term to match against relationship names or types (case-insensitive)
        
    Returns:
        List of entities containing matching navigation properties
    """
    relationships = []
    
    for entity in schema.findall('.//edm:EntityType', ODATA_NAMESPACES):
        entity_name = entity.get('Name', '')
        matching_nav_props = []
        
        for nav_prop in entity.findall('edm:NavigationProperty', ODATA_NAMESPACES):
            nav_name = nav_prop.get('Name', '')
            nav_type = nav_prop.get('Type', '')
            
            if (search_term in nav_name.lower() or 
                search_term in nav_type.lower()):
                nav_info = {
                    "name": nav_name,
                    "type": nav_type,
                    "contains_target": nav_prop.get('ContainsTarget', 'false') == 'true'
                }
                partner = nav_prop.get('Partner')
                if partner:
                    nav_info['partner'] = partner
                matching_nav_props.append(nav_info)
        
        if matching_nav_props:
            relationships.append({
                "entity": entity_name,
                "navigation_properties": matching_nav_props
            })
    
    return relationships


def _extract_entity_properties(entity: ET.Element) -> List[Dict[str, Any]]:
    """
    Extract property information from an entity element.
    
    Args:
        entity: Entity element from parsed XML
        
    Returns:
        List of property information dictionaries
    """
    properties = []
    
    for prop in entity.findall('edm:Property', ODATA_NAMESPACES):
        prop_info = {
            "name": prop.get('Name'),
            "type": prop.get('Type'),
            "nullable": prop.get('Nullable', 'true') == 'true',
        }
        
        # Add optional attributes
        max_length = prop.get('MaxLength')
        if max_length:
            prop_info['max_length'] = max_length
            
        precision = prop.get('Precision')
        if precision:
            prop_info['precision'] = precision
            
        scale = prop.get('Scale')
        if scale:
            prop_info['scale'] = scale
            
        properties.append(prop_info)
    
    return properties


def _extract_navigation_properties(entity: ET.Element) -> List[Dict[str, Any]]:
    """
    Extract navigation property information from an entity element.
    
    Args:
        entity: Entity element from parsed XML
        
    Returns:
        List of navigation property information dictionaries
    """
    nav_props = []
    
    for nav_prop in entity.findall('edm:NavigationProperty', ODATA_NAMESPACES):
        nav_info = {
            "name": nav_prop.get('Name'),
            "type": nav_prop.get('Type'),
            "contains_target": nav_prop.get('ContainsTarget', 'false') == 'true'
        }
        
        # Add optional attributes
        partner = nav_prop.get('Partner')
        if partner:
            nav_info['partner'] = partner
            
        nullable = nav_prop.get('Nullable')
        if nullable:
            nav_info['nullable'] = nullable == 'true'
            
        nav_props.append(nav_info)
    
    return nav_props


def find_entity_by_name(schema: ET.Element, entity_name: str) -> Optional[Dict[str, Any]]:
    """
    Find a specific entity by exact name match.
    
    Args:
        schema: Schema element from parsed OData metadata
        entity_name: Exact name of the entity to find
        
    Returns:
        Entity information dictionary or None if not found
    """
    for entity in schema.findall('.//edm:EntityType', ODATA_NAMESPACES):
        name = entity.get('Name', '')
        if name == entity_name:
            return {
                "name": name,
                "abstract": entity.get('Abstract', 'false') == 'true',
                "properties": _extract_entity_properties(entity),
                "navigation_properties": _extract_navigation_properties(entity)
            }
    
    return None


def get_entity_relationships(schema: ET.Element, entity_name: str) -> List[Dict[str, Any]]:
    """
    Get all relationships for a specific entity.
    
    Args:
        schema: Schema element from parsed OData metadata
        entity_name: Name of the entity to get relationships for
        
    Returns:
        List of relationship information dictionaries
    """
    for entity in schema.findall('.//edm:EntityType', ODATA_NAMESPACES):
        name = entity.get('Name', '')
        if name == entity_name:
            return _extract_navigation_properties(entity)
    
    return []
