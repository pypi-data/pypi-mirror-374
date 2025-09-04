# MCP Business Central

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A professional MCP Server for Microsoft Dynamics 365 Business Central with OAuth2 authentication and API v2.0 endpoints. Developed by [Dmitry Katson](https://github.com/DmitryKatson), Microsoft AI & Business Central MVP.

## Features

- 🔐 **OAuth2 Authentication** - Secure Azure AD integration
- 🏢 **Auto Company Discovery** - Automatic company detection and switching
- 📊 **Full CRUD Operations** - Complete entity management
- 🔍 **Schema Discovery** - Dynamic field exploration
- ⚡ **API v2.0** - Latest Business Central endpoints
- 🧩 **Clean Architecture** - Professional, scalable design

## Installation

```bash
pip install mcp-business-central
```

## Quick Start

### 1. Azure AD Setup

1. Create Azure AD app registration
2. Add Business Central API permissions (`Financials.ReadWrite.All`)
3. Create client secret
4. Grant admin consent

### 2. Environment Variables

```bash
BC_TENANT_ID=your-tenant-id
BC_CLIENT_ID=your-client-id
BC_CLIENT_SECRET=your-client-secret
BC_ENVIRONMENT=production
```

### 3. Claude Desktop Integration

```json
{
  "mcpServers": {
    "businesscentral": {
      "command": "mcp-business-central",
      "env": {
        "BC_TENANT_ID": "your-tenant-id",
        "BC_CLIENT_ID": "your-client-id",
        "BC_CLIENT_SECRET": "your-client-secret",
        "BC_ENVIRONMENT": "production"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `list_companies` | Discover available companies |
| `set_active_company` | Set active company |
| `get_active_company` | Get current company info |
| `list_resources` | List all available Business Central resources |
| `get_odata_metadata` | Smart metadata search - find entities, properties, relationships by search term |
| `get_resource_schema` | Get entity schema and fields |
| `list_records` | List entities with filtering/pagination |
| `find_records_by_field` | Search by field value |
| `get_record_by_id` | Get specific record |

## Usage Examples

### Company Management
```json
{
  "tool": "list_companies",
  "parameters": {}
}
```

### Entity Operations
```json
{
  "tool": "list_records",
  "parameters": {
    "resource": "customers",
    "top": "10",
    "filter": "city eq 'Seattle'"
  }
}
```

### Resource Discovery
```json
{
  "tool": "list_resources",
  "parameters": {}
}
```

### Metadata Discovery
```json
{
  "tool": "get_odata_metadata",
  "parameters": {
    "search": "customer",
    "search_type": "entity",
    "include_properties": true,
    "include_relationships": true
  }
}
```

**Smart Metadata Search**: Now returns focused, relevant metadata instead of the full XML. Search by entity names, properties, relationships, or enums. For complete schema overview, omit the `search` parameter.

### Schema Discovery
```json
{
  "tool": "get_resource_schema",
  "parameters": {
    "resource": "customers"
  }
}
```

## Common Entities

- `customers` - Customer records
- `vendors` - Vendor records
- `items` - Item catalog
- `employees` - Employee records
- `salesOrders` - Sales orders
- `purchaseOrders` - Purchase orders
- `accounts` - Chart of accounts
- `companyInformation` - Company details

## Development

```bash
# Clone and setup
git clone https://github.com/DmitryKatson/mcp-business-central
cd mcp-business-central
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .

# Run with debugging
npx @modelcontextprotocol/inspector -- python -m mcp_business_central
```

## Documentation

- 📁 [Project Structure](.aidocs/PROJECT_STRUCTURE.md) - Code organization and modules
- 🏗️ [Architecture](.aidocs/ARCHITECTURE.md) - Design principles and components
- 📋 [Tools](.aidocs/TOOLS.md) - Detailed tool documentation

## Troubleshooting

### Authentication Issues
- Verify Azure AD app permissions
- Check tenant/client ID and secret
- Ensure admin consent is granted

### API Access Issues
- Confirm Business Central environment access
- Verify correct entity names (case-sensitive)
- Use `get_resource_schema` to check available fields

## Author

**Dmitry Katson** - [GitHub](https://github.com/DmitryKatson) | [Website](https://katson.com)

💻 Microsoft AI & Business Central MVP  
🏆 Contribution Hero 2024  
🌐 Creator of [CentralQ.ai](https://centralq.ai) - AI search for Business Central community

## License

MIT License - Copyright (c) 2025 Dmitry Katson