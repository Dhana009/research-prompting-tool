# MCP Server Setup for Research & Debugging Toolkit

The Research & Debugging Toolkit is now available as an MCP (Model Context Protocol) server, allowing you to use all 5 research tools directly from Cursor.

## Features

- **5 Research Tools**: Topic Research, Coding Research, Debugging, Architecture, General Purpose
- **Multiple MongoDB Instances**: Configure and switch between multiple MongoDB instances at runtime
- **Flexible Configuration**: Each MongoDB instance can have its own database and collection names
- **Runtime Switching**: Switch between MongoDB instances without restarting the server
- **Visibility**: Always know which MongoDB instance is currently active

## Configuration

The MCP server has been added to your `mcp.json` file. See [MCP_MONGODB_CONFIG.md](./MCP_MONGODB_CONFIG.md) for detailed MongoDB configuration options.

### Basic Configuration

```json
"research-toolkit": {
  "command": "python",
  "args": [
    "D:\\planning\\research\\research_toolkit\\src\\mcp_server.py"
  ],
  "env": {
    "ROUTELLM_API_KEY": "your-api-key",
    "ROUTELLM_API_URL": "https://routellm.abacus.ai/v1",
    "MONGODB_CONNECTION_STRING": "mongodb+srv://...",
    "MONGODB_DATABASE": "research_toolkit",
    "MONGODB_COLLECTION": "research_documents"
  }
}
```

### Multiple MongoDB Instances

For multiple MongoDB instances, see [MCP_MONGODB_CONFIG.md](./MCP_MONGODB_CONFIG.md) for the complete configuration guide.

## Available MCP Tools

The server exposes 8 tools (5 research tools + 3 MongoDB management tools):

### 1. `topic_research`
Research topics and concepts. Provides high-level understanding, definitions, fundamentals, and terminology.

**Parameters:**
- `question` (required): Research question about a topic
- `complexity` (optional): "simple" or "large" (default: "simple")
- `use_backup` (optional): Use backup model instead of primary (default: false)
- `save_to_db` (optional): Save response to MongoDB (default: true)

### 2. `coding_research`
Research coding patterns, best practices, implementation guides, edge cases, and pitfalls.

**Parameters:**
- `question` (required): Coding research question
- `complexity` (optional): "simple", "moderate", or "deep" (default: "simple")
- `save_to_db` (optional): Save response to MongoDB (default: true)

### 3. `debugging`
Analyze failing code and provide root cause analysis. Does NOT generate code - only deep reasoning. Supports tier-based escalation.

**Parameters:**
- `code` (required): The failing code
- `explanation` (required): Error explanation or context
- `tier` (optional): 1, 2, or 3 (default: 1)
- `user_feedback` (optional): User feedback for escalation
- `save_to_db` (optional): Save response to MongoDB (default: true)

### 4. `architecture`
Design system architecture, flows, frameworks, and system layouts. Identifies critical hotspots.

**Parameters:**
- `question` (required): Architecture or system design question
- `use_backup` (optional): Use backup model instead of primary (default: false)
- `save_to_db` (optional): Save response to MongoDB (default: true)

### 5. `general_purpose`
General purpose queries that don't fit into other categories. Auto-upgrades model based on complexity.

**Parameters:**
- `question` (required): General question
- `complexity` (optional): "simple" or "medium" (default: "simple")
- `save_to_db` (optional): Save response to MongoDB (default: true)

### 6. `list_mongodb_instances`
List all configured MongoDB instances and show which one is currently active.

**Parameters:** None

**Returns:** List of all MongoDB instances with their URIs, databases, collections, and active status

### 7. `get_active_mongodb_instance`
Get the currently active MongoDB instance details.

**Parameters:** None

**Returns:** Active instance name, URI, database, and collection

### 8. `switch_mongodb_instance`
Switch to a different MongoDB instance. All future operations will use this instance.

**Parameters:**
- `instance_name` (required): Name of the MongoDB instance to switch to

**Returns:** Confirmation with new instance details

## Usage in Cursor

After restarting Cursor, the tools will be available in the MCP tools list. You can use them by:

1. Opening the MCP tools panel in Cursor
2. Selecting one of the research-toolkit tools
3. Providing the required parameters
4. The tool will execute and return the research results

## Testing

To test the MCP server manually:

```bash
cd research_toolkit
python src/mcp_server.py
```

Then send JSON-RPC 2.0 requests via stdin, for example:

```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
```

## Troubleshooting

1. **Server not starting**: Check that Python can find the `src` directory and all dependencies are installed
2. **Import errors**: Ensure you're running from the correct directory or adjust the `sys.path` in `mcp_server.py`
3. **Connection errors**: Verify environment variables are set correctly in `mcp.json`
4. **MongoDB errors**: Ensure MongoDB connection string is valid and accessible

## Notes

- The MCP server uses stdio for communication (standard input/output)
- All responses are saved to MongoDB by default (unless `save_to_db: false`)
- The server follows the MCP protocol version 2024-11-05
- Error handling is built-in and returns proper JSON-RPC error responses

