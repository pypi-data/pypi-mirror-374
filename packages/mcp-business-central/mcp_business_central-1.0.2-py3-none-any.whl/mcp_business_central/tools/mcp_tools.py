"""
MCP tools for Business Central integration.

This module contains all the MCP tool implementations for interacting with
Microsoft Dynamics 365 Business Central APIs.
"""

from typing import Dict, Any, Optional, Union, Annotated
from pydantic import Field

from mcp.server.fastmcp import Context
from ..server import mcp, logger, get_request_clients
from ..logging.exceptions import ValidationError, APIError, CompanyNotFoundError
from ..api.http_client import APIResponse
from ..api.entities import SchemaInfo
from ..utils import validate_resource_name, validate_field_name, build_odata_filter, convert_to_int
from ..api.odata import (
    parse_metadata_xml, get_metadata_summary, search_entities,
    search_enums, search_properties, search_relationships,
)

@mcp.tool(name="list_companies", description="List all available companies in the Business Central environment.")
async def discover_companies_tool(ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Discover all available companies in Business Central."""
    logger.info("Tool 'list_companies' called")
    
    try:
        api, companies_mgr = get_request_clients(ctx)
        companies = await companies_mgr.discover_companies()
        companies_data = [
            {
                "id": company.id,
                "name": company.name,
                "displayName": company.display_name,
                "businessProfileId": company.business_profile_id
            }
            for company in companies
        ]
        
        response = APIResponse.success_response(
            {"companies": companies_data, "message": f"Found {len(companies)} companies"},
            count=len(companies)
        )
        return response.to_dict()
        
    except Exception as e:
        logger.error(f"Error discovering companies: {e}")
        return APIResponse.error_response(str(e)).to_dict()

@mcp.tool(name="set_active_company", description="Set the active company for subsequent Business Central operations.")
async def set_company_tool(
    company_id: Annotated[str, Field(description="Unique identifier of the company to set as active. UUID format (e.g., '12345678-1234-1234-1234-123456789abc'). Use list_companies to discover available company IDs.")],
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Set the active company for Business Central operations."""
    logger.info(f"Tool 'set_active_company' called with company_id={company_id}")
    
    try:
        api, companies_mgr = get_request_clients(ctx)
        company = await companies_mgr.set_active_company(company_id)
        response = APIResponse.success_response({
                    "company_id": company_id,
            "company_name": company.name,
                    "message": "Company set successfully"
        })
        return response.to_dict()
        
    except CompanyNotFoundError as e:
        logger.error(f"Company not found: {e}")
        return APIResponse.error_response(str(e)).to_dict()
    except Exception as e:
        logger.error(f"Error setting company: {e}")
        return APIResponse.error_response(str(e)).to_dict()

@mcp.tool(name="get_active_company", description="Get information about the currently active company.")
async def get_active_company_tool(ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Get the currently active company information."""
    logger.info("Tool 'get_active_company' called")
    
    try:
        api, companies_mgr = get_request_clients(ctx)
        company = await companies_mgr.get_active_company()
        if not company:
            return APIResponse.error_response("No active company set").to_dict()
        
        response = APIResponse.success_response({
            "active_company": {
                "id": company.id,
                "name": company.name,
                "displayName": company.display_name,
                "businessProfileId": company.business_profile_id
            },
            "company_id": company.id
        })
        return response.to_dict()
            
    except Exception as e:
        logger.error(f"Error getting active company: {e}")
        return APIResponse.error_response(str(e)).to_dict()



@mcp.tool(name="list_resources", description="List all available Business Central resources in the current environment.")
async def list_resources_tool(ctx: Optional[Context] = None) -> Dict[str, Any]:
    """List all available Business Central resources using native API discovery."""
    logger.info("Tool 'list_resources' called")
    
    try:
        # Step 1: Resource discovery using global endpoint (no company needed)
        logger.info("Discovering all available resources...")
        api, _ = get_request_clients(ctx)
        result = await api.request("GET", "", company_id=None)  # No company context needed
        
        all_resources = []
        if isinstance(result, dict) and 'value' in result:
            all_resources = [
                {
                    "name": item.get("name"),
                    "kind": item.get("kind"), 
                    "url": item.get("url")
                }
                for item in result.get('value', [])
                if item.get("name")
            ]
        
        # Step 2: Filter EntitySets (the resources users typically want)
        entity_sets = [r for r in all_resources if r.get("kind") == "EntitySet"]
        other_resources = [r for r in all_resources if r.get("kind") != "EntitySet"]
        
        # Step 3: Create comprehensive response
        discovery_data = {
            "discovery_method": "Business Central native API discovery endpoints",
            "summary": {
                "total_resources": len(all_resources),
                "entity_sets": len(entity_sets),
                "other_resources": len(other_resources)
            },
            "entity_sets": entity_sets,
            "other_resources": other_resources,
            "all_resources": all_resources,
            "usage_tips": [
                "All resources listed are available without company context",
                "EntitySets are the main data resources (customers, items, etc.)",
                "Resource names are case-sensitive",
                "Use get_resource_schema to explore fields for any resource",
                "Use get_odata_metadata to retrieve the full OData XML schema"
            ]
        }
        
        response = APIResponse.success_response(discovery_data)
        return response.to_dict()
        
    except APIError as e:
        logger.error(f"API error in list_resources: {e}")
        return APIResponse.error_response(str(e)).to_dict()
    except Exception as e:
        logger.error(f"Unexpected error in list_resources: {e}")
        return APIResponse.error_response(f"Unexpected error: {str(e)}").to_dict()


@mcp.tool(name="get_odata_metadata", description="Search and retrieve specific OData metadata information for Business Central entities, properties, relationships, or enums. Use search terms to get focused, relevant metadata instead of the full schema.")
async def get_odata_metadata_tool(
    search: Annotated[Optional[str], Field(description="Search term to filter metadata (entity name, property, enum, etc.). If not provided, returns summary of all entities") ] = None,
    search_type: Annotated[Optional[str], Field(description="Type of metadata to search: 'entity', 'property', 'relationship', 'enum', 'all'") ] = "all",
    include_properties: Annotated[Optional[bool], Field(description="Include detailed property information for found entities")] = True,
    include_relationships: Annotated[Optional[bool], Field(description="Include navigation properties/relationships for found entities")] = True,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Search and retrieve specific OData metadata information."""
    logger.info(f"Tool 'get_odata_metadata' called with search='{search}', search_type='{search_type}'")
    
    try:
        # Import aiohttp for direct HTTP requests
        import aiohttp
        
        # Resolve per-request API client (header or env fallback)
        api, _ = get_request_clients(ctx)
        
        # Get authentication token and base URL from the resolved client
        token = await api.auth_manager.get_access_token()
        base_url = api.config.base_url
        metadata_url = f"{base_url}/$metadata"
        
        # Make direct HTTP request for XML content
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/xml",
            "Content-Type": "application/xml"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(metadata_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return APIResponse.error_response(f"HTTP {response.status}: {error_text}").to_dict()
                
                xml_content = await response.text()
        
        # Parse XML using metadata utilities
        schema = parse_metadata_xml(xml_content)
        
        result = {
            "search_term": search,
            "search_type": search_type,
            "namespace": schema.get('Namespace', 'Microsoft.NAV')
        }
        
        # If no search term, return summary
        if not search:
            result.update(get_metadata_summary(schema))
        else:
            # Perform targeted search
            search_lower = search.lower()
            
            if search_type in ['entity', 'all']:
                entities = search_entities(schema, search_lower, include_properties, include_relationships)
                if entities:
                    result['entities'] = entities
            
            if search_type in ['enum', 'all']:
                enums = search_enums(schema, search_lower)
                if enums:
                    result['enums'] = enums
            
            if search_type in ['property', 'all']:
                properties = search_properties(schema, search_lower)
                if properties:
                    result['properties_found_in'] = properties
            
            if search_type in ['relationship', 'all']:
                relationships = search_relationships(schema, search_lower)
                if relationships:
                    result['relationships'] = relationships
        
        # Add helpful tips based on what was found
        tips = []
        if 'entities' in result:
            tips.append("Use list_records, get_record_by_id, or find_records_by_field with these entity names")
        if 'enums' in result:
            tips.append("Use enum values in filters (e.g., itemType eq 'Inventory')")
        if 'properties_found_in' in result:
            tips.append("Use these property names in select, filter, or orderby parameters")
        
        if tips:
            result['usage_tips'] = tips
        
        return APIResponse.success_response(result).to_dict()
                    
    except ValueError as e:
        logger.error(f"Metadata parsing error: {e}")
        return APIResponse.error_response(f"Failed to parse metadata: {str(e)}").to_dict()
    except Exception as e:
        logger.error(f"Error fetching OData metadata: {e}")
        return APIResponse.error_response(f"Failed to fetch OData metadata: {str(e)}").to_dict()


@mcp.tool(name="get_resource_schema", description="Get schema information and available fields for a Business Central resource.")
async def get_schema_tool(
    resource: Annotated[str, Field(description="Business Central entity/resource name. Case-sensitive. Common entities: 'customers', 'items', 'salesOrders', 'vendors', 'employees'. Use list_resources to discover all available entities.")],
    company_id: Annotated[Optional[str], Field(description="Optional company ID (UUID format). If not provided, uses the currently active company. Use list_companies to discover available companies.")] = None,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Get schema information for a Business Central resource."""
    logger.info(f"Tool 'get_resource_schema' called for resource={resource}")
    
    try:
        # Validate inputs
        resource = validate_resource_name(resource)
        
        if not company_id:
            _, companies_mgr = get_request_clients(ctx)
            company_id = await companies_mgr.get_active_company_id()
        
        logger.info(f"Getting schema for resource: {resource}")
        
        # Get a sample record to determine schema
        api, _ = get_request_clients(ctx)
        result = await api.request("GET", resource, params={'$top': 1}, company_id=company_id)
        
        fields = []
        sample_item = {}
        
        if result.get('value') and len(result['value']) > 0:
            sample_item = result['value'][0]
            fields = list(sample_item.keys())
            logger.info(f"Found {len(fields)} fields in schema")
        else:
            logger.warning(f"No sample data found for resource {resource}")
        
        schema_info = SchemaInfo(
            resource=resource,
            fields=fields,
            sample_item=sample_item,
            company_id=company_id
        )
        
        response = APIResponse.success_response({
            "resource": schema_info.resource,
            "available_fields": schema_info.fields,
            "field_count": schema_info.field_count,
            "sample_item": schema_info.sample_item,
            "company_id": schema_info.company_id,
            "has_data": schema_info.has_data
        })
        return response.to_dict()
        
    except ValidationError as e:
        logger.error(f"Validation error in get_resource_schema: {e}")
        return APIResponse.error_response(f"Parameter validation error: {str(e)}").to_dict()
    except APIError as e:
        logger.error(f"API error in get_resource_schema: {e}")
        return APIResponse.error_response(str(e)).to_dict()
    except Exception as e:
        logger.error(f"Unexpected error in get_resource_schema: {e}")
        return APIResponse.error_response(f"Unexpected error: {str(e)}").to_dict()

@mcp.tool(name="list_records", description="List records from a Business Central resource with optional filtering, ordering, expansion, selection, and pagination.")
async def list_items_tool(
    resource: Annotated[str, Field(description="Business Central entity/resource name. Case-sensitive. Common entities: 'customers', 'items', 'salesOrders', 'vendors', 'employees'. Use list_resources to discover all available entities.")],
    filter: Annotated[Optional[str], Field(description="OData V4.0 $filter syntax to restrict returned entities. Operators: eq, ne, gt, ge, lt, le, or, and, not. Alert: Business Central's OData API doesn't support the OR operator across different fields in a single filter (make separate queries if needed). Use guid'value' for GUIDs. Examples: \"city eq 'Seattle'\", \"amount gt 1000 and status eq 'Active'\", \"city eq 'Seattle' or city eq 'Portland'\"")] = None,
    top: Annotated[Optional[Union[int, str]], Field(description="Maximum records to return. Default/recommended: 20. Use with skip for pagination. Example: 50")] = None,
    skip: Annotated[Optional[Union[int, str]], Field(description="Number of records to skip before returning results. Use with top for pagination. Example: 100")] = None,
    orderby: Annotated[Optional[str], Field(description="OData V4.0 $orderby syntax (e.g., 'displayName asc', 'createdDate desc', 'property1 desc, property2 asc'). Sorts results by specified properties.")] = None,
    expand: Annotated[Optional[str], Field(description="OData V4.0 $expand to include related entities in response. Comma-separated list (e.g., 'salesOrderLines', 'customer,defaultDimensions'). Use get_resource_schema to discover available navigation properties.")] = None,
    select: Annotated[Optional[str], Field(description="OData V4.0 $select - comma-separated list of properties to include in response (e.g., 'id,displayName,email'). Returns all properties if not specified. Use get_resource_schema to discover available properties.")] = None,
    company_id: Annotated[Optional[str], Field(description="Optional company ID (UUID format). If not provided, uses the currently active company. Use list_companies to discover available companies.")] = None,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """List items from a Business Central resource with full OData query support."""
    logger.info(f"Tool 'list_records' called for resource={resource}, filter={filter}, top={top}, skip={skip}, orderby={orderby}, expand={expand}, select={select}")
    
    try:
        # Validate and normalize inputs
        resource = validate_resource_name(resource)
        
        if not company_id:
            _, companies_mgr = get_request_clients(ctx)
            company_id = await companies_mgr.get_active_company_id()
        
        # Convert string parameters to integers if needed
        top_int = convert_to_int(top, 'top')
        skip_int = convert_to_int(skip, 'skip')
        
        # Build OData parameters dictionary
        params = {}
        if filter is not None:
            params['$filter'] = filter
        if top_int is not None:
            params['$top'] = top_int
        if skip_int is not None:
            params['$skip'] = skip_int
        if orderby is not None:
            params['$orderby'] = orderby
        if expand is not None:
            params['$expand'] = expand
        if select is not None:
            params['$select'] = select
        
        logger.debug(f"Final OData request parameters: {params}")
        
        api, _ = get_request_clients(ctx)
        result = await api.request("GET", resource, params=params, company_id=company_id)
        
        # Add metadata to response
        if isinstance(result, dict) and 'value' in result:
            result['_metadata'] = {
                "company_id": company_id,
                "request_params": {
                    "resource": resource,
                    "filter": filter,
                    "top": top_int,
                    "skip": skip_int,
                    "orderby": orderby,
                    "expand": expand,
                    "select": select
                }
            }
        
        response = APIResponse.success_response(result)
        return response.to_dict()
        
    except ValidationError as e:
        logger.error(f"Validation error in list_records: {e}")
        return APIResponse.error_response(f"Parameter validation error: {str(e)}").to_dict()
    except APIError as e:
        logger.error(f"API error in list_records: {e}")
        return APIResponse.error_response(str(e)).to_dict()
    except Exception as e:
        logger.error(f"Unexpected error in list_records: {e}")
        return APIResponse.error_response(f"Unexpected error: {str(e)}").to_dict()

@mcp.tool(name="find_records_by_field", description="Find records where a specific field matches a given value with optional ordering, expansion, and selection.")
async def get_items_by_field_tool(
    resource: Annotated[str, Field(description="Business Central entity/resource name. Case-sensitive. Common entities: 'customers', 'items', 'salesOrders', 'vendors', 'employees'. Use list_resources to discover all available entities.")],
    field: Annotated[str, Field(description="Property/field name to search by. Case-sensitive. Common fields: 'displayName', 'city', 'email', 'number'. Use get_resource_schema to discover available properties for the entity.")],
    value: Annotated[str, Field(description="Value to search for. Will be automatically quoted for string comparison and formatted appropriately for the field type.")],
    orderby: Annotated[Optional[str], Field(description="OData V4.0 $orderby syntax (e.g., 'displayName asc', 'createdDate desc', 'property1 desc, property2 asc'). Sorts results by specified properties.")] = None,
    expand: Annotated[Optional[str], Field(description="OData V4.0 $expand to include related entities in response. Comma-separated list (e.g., 'salesOrderLines', 'customer,defaultDimensions'). Use get_resource_schema to discover available navigation properties.")] = None,
    select: Annotated[Optional[str], Field(description="OData V4.0 $select - comma-separated list of properties to include in response (e.g., 'id,displayName,email'). Returns all properties if not specified. Use get_resource_schema to discover available properties.")] = None,
    top: Annotated[Optional[Union[int, str]], Field(description="Maximum records to return. Default/recommended: 20. Use with skip for pagination. Example: 50")] = None,
    company_id: Annotated[Optional[str], Field(description="Optional company ID (UUID format). If not provided, uses the currently active company. Use list_companies to discover available companies.")] = None,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Get items from Business Central by field value with full OData query support."""
    logger.info(f"Tool 'find_records_by_field' called for resource={resource}, field={field}, value={value}, orderby={orderby}, expand={expand}, select={select}, top={top}")
    
    try:
        # Validate inputs
        resource = validate_resource_name(resource)
        field = validate_field_name(field)
        
        if value is None:
            raise ValidationError("Value cannot be None")
        
        # Convert pagination parameters
        top_int = convert_to_int(top, 'top')
        
        # Build OData filter using utility function
        filter_expr = build_odata_filter(field, value)
        
        logger.debug(f"Built filter expression: {filter_expr}")
        
        return await list_items_tool(resource, filter=filter_expr, orderby=orderby, 
                                   expand=expand, select=select, top=top_int, company_id=company_id, ctx=ctx)
        
    except ValidationError as e:
        logger.error(f"Validation error in find_records_by_field: {e}")
        return APIResponse.error_response(f"Parameter validation error: {str(e)}").to_dict()
    except Exception as e:
        logger.error(f"Unexpected error in find_records_by_field: {e}")
        return APIResponse.error_response(f"Unexpected error: {str(e)}").to_dict()

@mcp.tool(name="get_record_by_id", description="Get a specific record by its unique identifier with optional expansion and field selection.")
async def get_item_by_id_tool(
    resource: Annotated[str, Field(description="Business Central entity/resource name. Case-sensitive. Common entities: 'customers', 'items', 'salesOrders', 'vendors', 'employees'. Use list_resources to discover all available entities.")],
    item_id: Annotated[str, Field(description="Unique identifier of the record. Usually UUID format (e.g., '12345678-1234-1234-1234-123456789abc') or entity-specific identifier.")],
    expand: Annotated[Optional[str], Field(description="OData V4.0 $expand to include related entities in response. Comma-separated list (e.g., 'salesOrderLines', 'customer,defaultDimensions'). Use get_resource_schema to discover available navigation properties.")] = None,
    select: Annotated[Optional[str], Field(description="OData V4.0 $select - comma-separated list of properties to include in response (e.g., 'id,displayName,email'). Returns all properties if not specified. Use get_resource_schema to discover available properties.")] = None,
    company_id: Annotated[Optional[str], Field(description="Optional company ID (UUID format). If not provided, uses the currently active company. Use list_companies to discover available companies.")] = None,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Get a specific item by ID from Business Central with optional expansion and field selection."""
    logger.info(f"Tool 'get_record_by_id' called for resource={resource}, item_id={item_id}, expand={expand}, select={select}")
    
    try:
        resource = validate_resource_name(resource)
        
        if not company_id:
            _, companies_mgr = get_request_clients(ctx)
            company_id = await companies_mgr.get_active_company_id()
        
        # Build OData parameters
        params = {}
        if expand is not None:
            params['$expand'] = expand
        if select is not None:
            params['$select'] = select
        
        logger.debug(f"OData parameters for get_record_by_id: {params}")
        
        api, _ = get_request_clients(ctx)
        result = await api.request("GET", resource, item_id=item_id, params=params, company_id=company_id)
        
        # Add metadata
        if isinstance(result, dict):
            result['_metadata'] = {
                "company_id": company_id,
                "request_params": {
                    "expand": expand,
                    "select": select
                }
            }
        
        response = APIResponse.success_response(result)
        return response.to_dict()
        
    except ValidationError as e:
        logger.error(f"Validation error in get_record_by_id: {e}")
        return APIResponse.error_response(f"Parameter validation error: {str(e)}").to_dict()
    except APIError as e:
        logger.error(f"API error in get_record_by_id: {e}")
        return APIResponse.error_response(str(e)).to_dict()
    except Exception as e:
        logger.error(f"Unexpected error in get_record_by_id: {e}")
        return APIResponse.error_response(f"Unexpected error: {str(e)}").to_dict()