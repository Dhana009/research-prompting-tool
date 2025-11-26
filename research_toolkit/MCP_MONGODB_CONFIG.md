# MongoDB Multi-Instance Configuration Guide

The Research & Debugging Toolkit MCP server supports multiple MongoDB instances with runtime switching. You can configure as many MongoDB instances as needed and switch between them at runtime.

## Configuration Format

### Default Instance (Legacy Support)

The default instance uses these environment variables:

```json
{
  "MONGODB_CONNECTION_STRING": "mongodb+srv://...",
  "MONGODB_DATABASE": "research_toolkit",
  "MONGODB_COLLECTION": "research_documents"
}
```

### Additional Instances

For each additional MongoDB instance, use this naming pattern:

```
MONGODB_INSTANCE_<NAME>_URI        - MongoDB connection string
MONGODB_INSTANCE_<NAME>_DB         - Database name (optional, defaults to "research_toolkit")
MONGODB_INSTANCE_<NAME>_COLLECTION - Collection name (optional, defaults to "research_documents")
```

**Example for a "PRIMARY" instance:**

```json
{
  "MONGODB_INSTANCE_PRIMARY_URI": "mongodb+srv://user:pass@cluster0.mongodb.net/",
  "MONGODB_INSTANCE_PRIMARY_DB": "research_toolkit",
  "MONGODB_INSTANCE_PRIMARY_COLLECTION": "research_documents"
}
```

**Example for a "SECONDARY" instance:**

```json
{
  "MONGODB_INSTANCE_SECONDARY_URI": "mongodb+srv://user:pass@cluster1.mongodb.net/",
  "MONGODB_INSTANCE_SECONDARY_DB": "research_toolkit_backup",
  "MONGODB_INSTANCE_SECONDARY_COLLECTION": "research_documents"
}
```

**Example for a "TERTIARY" instance:**

```json
{
  "MONGODB_INSTANCE_TERTIARY_URI": "mongodb+srv://user:pass@cluster2.mongodb.net/",
  "MONGODB_INSTANCE_TERTIARY_DB": "research_toolkit_archive",
  "MONGODB_INSTANCE_TERTIARY_COLLECTION": "research_documents"
}
```

## Complete mcp.json Example

```json
{
  "mcpServers": {
    "research-toolkit": {
      "command": "python",
      "args": [
        "D:\\planning\\research\\research_toolkit\\src\\mcp_server.py"
      ],
      "env": {
        "ROUTELLM_API_KEY": "your-api-key",
        "ROUTELLM_API_URL": "https://routellm.abacus.ai/v1",
        
        "MONGODB_CONNECTION_STRING": "mongodb+srv://user:pass@cluster0.mongodb.net/",
        "MONGODB_DATABASE": "research_toolkit",
        "MONGODB_COLLECTION": "research_documents",
        
        "MONGODB_INSTANCE_PRIMARY_URI": "mongodb+srv://user:pass@cluster0.mongodb.net/",
        "MONGODB_INSTANCE_PRIMARY_DB": "research_toolkit",
        "MONGODB_INSTANCE_PRIMARY_COLLECTION": "research_documents",
        
        "MONGODB_INSTANCE_SECONDARY_URI": "mongodb+srv://user:pass@cluster1.mongodb.net/",
        "MONGODB_INSTANCE_SECONDARY_DB": "research_toolkit_backup",
        "MONGODB_INSTANCE_SECONDARY_COLLECTION": "research_documents",
        
        "MONGODB_INSTANCE_ARCHIVE_URI": "mongodb+srv://user:pass@cluster2.mongodb.net/",
        "MONGODB_INSTANCE_ARCHIVE_DB": "research_toolkit_archive",
        "MONGODB_INSTANCE_ARCHIVE_COLLECTION": "research_documents"
      }
    }
  }
}
```

## MCP Tools for MongoDB Management

### 1. `list_mongodb_instances`

Lists all configured MongoDB instances and shows which one is currently active.

**Usage:**
- No parameters required
- Returns a list of all instances with their URIs, databases, collections, and active status

**Example Response:**
```
Available MongoDB Instances:

default
  URI: mongodb+srv://...
  Database: research_toolkit
  Collection: research_documents

primary ✓ ACTIVE
  URI: mongodb+srv://...
  Database: research_toolkit
  Collection: research_documents

secondary
  URI: mongodb+srv://...
  Database: research_toolkit_backup
  Collection: research_documents
```

### 2. `get_active_mongodb_instance`

Shows the currently active MongoDB instance details.

**Usage:**
- No parameters required
- Returns the active instance name, URI, database, and collection

**Example Response:**
```
Currently Active MongoDB Instance: primary

URI: mongodb+srv://user:pass@cluster0.mongodb.net/
Database: research_toolkit
Collection: research_documents
```

### 3. `switch_mongodb_instance`

Switches to a different MongoDB instance. All future operations will use this instance.

**Parameters:**
- `instance_name` (required): Name of the MongoDB instance to switch to

**Usage:**
```json
{
  "instance_name": "secondary"
}
```

**Example Response:**
```
✓ Switched to MongoDB instance: secondary

URI: mongodb+srv://user:pass@cluster1.mongodb.net/
Database: research_toolkit_backup
Collection: research_documents
```

## Usage Workflow

1. **List Available Instances:**
   - Use `list_mongodb_instances` to see all configured MongoDB instances

2. **Check Active Instance:**
   - Use `get_active_mongodb_instance` to see which instance is currently being used

3. **Switch Instance:**
   - Use `switch_mongodb_instance` with the desired instance name
   - All future research tool operations will write to the new instance

4. **Verify Switch:**
   - Use `get_active_mongodb_instance` again to confirm the switch

## Important Notes

- **Instance Names are Case-Insensitive**: The system converts all instance names to lowercase
- **Default Instance**: If you only configure `MONGODB_CONNECTION_STRING`, it will be available as the "default" instance
- **Automatic Selection**: The first configured instance becomes the default active instance on startup
- **Persistence**: The active instance persists for the lifetime of the MCP server process
- **Collection/Database Flexibility**: Each instance can use different database and collection names
- **No Limit**: You can configure as many instances as needed (10, 20, 100+)

## Use Cases

1. **Storage Full**: When one MongoDB cluster is full, switch to another
2. **Environment Separation**: Use different instances for dev/staging/prod
3. **Backup Strategy**: Write to multiple instances for redundancy
4. **Organization**: Separate instances by project, team, or purpose
5. **Cost Optimization**: Use cheaper instances for archival data

## Troubleshooting

**Instance Not Found:**
- Check that environment variable names match the pattern exactly
- Ensure instance name in `switch_mongodb_instance` matches the configured name (case-insensitive)
- Use `list_mongodb_instances` to see all available instances

**Connection Errors:**
- Verify MongoDB connection strings are correct
- Check network connectivity
- Ensure MongoDB credentials are valid

**Database/Collection Not Found:**
- MongoDB will create databases and collections automatically on first write
- Verify you have write permissions

