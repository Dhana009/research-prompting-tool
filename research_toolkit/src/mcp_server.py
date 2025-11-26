#!/usr/bin/env python3
"""
MCP Server for Research & Debugging Toolkit.

Exposes the 5 research tools as MCP tools for use in Cursor.
Supports multiple MongoDB instances with runtime switching.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, Optional, List, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.api_client import RouteLLMClient
from src.storage.mongodb import MongoDBClient
from src.tools.topic_research import TopicResearchTool
from src.tools.coding_research import CodingResearchTool
from src.tools.debugging import DebuggingTool
from src.tools.architecture import ArchitectureTool
from src.tools.general_purpose import GeneralPurposeTool


# MongoDB instance management
_mongodb_instances: Dict[str, Dict[str, Any]] = {}
_active_mongodb_instance: Optional[str] = None

# Initialize clients (will be created on first use)
_api_client: Optional[RouteLLMClient] = None
_db_client: Optional[MongoDBClient] = None


def load_mongodb_instances():
    """Load MongoDB instances from environment variables."""
    global _mongodb_instances, _active_mongodb_instance
    
    # Load from environment variables
    # Format: MONGODB_INSTANCE_<NAME>_URI, MONGODB_INSTANCE_<NAME>_DB, MONGODB_INSTANCE_<NAME>_COLLECTION
    # Example: MONGODB_INSTANCE_PRIMARY_URI, MONGODB_INSTANCE_PRIMARY_DB, MONGODB_INSTANCE_PRIMARY_COLLECTION
    
    instance_names = set()
    for key in os.environ.keys():
        if key.startswith("MONGODB_INSTANCE_") and key.endswith("_URI"):
            # Extract instance name (e.g., "PRIMARY" from "MONGODB_INSTANCE_PRIMARY_URI")
            instance_name = key.replace("MONGODB_INSTANCE_", "").replace("_URI", "").lower()
            instance_names.add(instance_name)
    
    # Also check for default instance
    if os.getenv("MONGODB_CONNECTION_STRING"):
        instance_names.add("default")
    
    # Load each instance
    for instance_name in instance_names:
        if instance_name == "default":
            uri = os.getenv("MONGODB_CONNECTION_STRING")
            db = os.getenv("MONGODB_DATABASE", "research_toolkit")
            collection = os.getenv("MONGODB_COLLECTION", "research_documents")
        else:
            uri_key = f"MONGODB_INSTANCE_{instance_name.upper()}_URI"
            db_key = f"MONGODB_INSTANCE_{instance_name.upper()}_DB"
            collection_key = f"MONGODB_INSTANCE_{instance_name.upper()}_COLLECTION"
            
            uri = os.getenv(uri_key)
            db = os.getenv(db_key, "research_toolkit")
            collection = os.getenv(collection_key, "research_documents")
        
        if uri:
            _mongodb_instances[instance_name] = {
                "uri": uri,
                "database": db,
                "collection": collection,
                "name": instance_name
            }
    
    # Set default active instance
    if not _active_mongodb_instance and _mongodb_instances:
        _active_mongodb_instance = list(_mongodb_instances.keys())[0]


def get_clients():
    """Get or create API and database clients."""
    global _api_client, _db_client, _active_mongodb_instance
    
    if _api_client is None:
        _api_client = RouteLLMClient()
    
    # Load instances if not loaded
    if not _mongodb_instances:
        load_mongodb_instances()
    
    # Get active instance
    if not _active_mongodb_instance and _mongodb_instances:
        _active_mongodb_instance = list(_mongodb_instances.keys())[0]
    
    if _db_client is None and _active_mongodb_instance:
        instance = _mongodb_instances[_active_mongodb_instance]
        _db_client = MongoDBClient(connection_string=instance["uri"])
        if not _db_client._connected:
            _db_client.connect(
                database_name=instance["database"],
                collection_name=instance["collection"]
            )
    
    return _api_client, _db_client


def switch_mongodb_instance(instance_name: str) -> Dict[str, Any]:
    """Switch to a different MongoDB instance."""
    global _db_client, _active_mongodb_instance, _mongodb_instances
    
    if instance_name not in _mongodb_instances:
        raise ValueError(f"MongoDB instance '{instance_name}' not found. Available instances: {list(_mongodb_instances.keys())}")
    
    instance = _mongodb_instances[instance_name]
    
    # Close existing connection
    if _db_client:
        _db_client.close()
    
    # Create new connection
    _db_client = MongoDBClient(connection_string=instance["uri"])
    _db_client.connect(
        database_name=instance["database"],
        collection_name=instance["collection"]
    )
    
    _active_mongodb_instance = instance_name
    
    return {
        "active_instance": instance_name,
        "uri": instance["uri"],
        "database": instance["database"],
        "collection": instance["collection"],
        "message": f"Switched to MongoDB instance: {instance_name}"
    }


def list_tools() -> List[Dict[str, Any]]:
    """List all available tools."""
    return [
        {
            "name": "topic_research",
            "description": "Research topics and concepts. Provides high-level understanding, definitions, fundamentals, and terminology.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Research question about a topic"
                    },
                    "complexity": {
                        "type": "string",
                        "enum": ["simple", "large"],
                        "default": "simple",
                        "description": "Complexity level: 'simple' for normal topics, 'large' for complex conceptual topics"
                    },
                    "use_backup": {
                        "type": "boolean",
                        "default": False,
                        "description": "Use backup model instead of primary"
                    },
                    "save_to_db": {
                        "type": "boolean",
                        "default": True,
                        "description": "Save response to MongoDB"
                    }
                },
                "required": ["question"]
            }
        },
        {
            "name": "coding_research",
            "description": "Research coding patterns, best practices, implementation guides, edge cases, and pitfalls.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Coding research question about patterns, best practices, etc."
                    },
                    "complexity": {
                        "type": "string",
                        "enum": ["simple", "moderate", "deep"],
                        "default": "simple",
                        "description": "Complexity level: 'simple' for basic patterns, 'moderate' for advanced patterns, 'deep' for complex implementations"
                    },
                    "save_to_db": {
                        "type": "boolean",
                        "default": True,
                        "description": "Save response to MongoDB"
                    }
                },
                "required": ["question"]
            }
        },
        {
            "name": "debugging",
            "description": "Analyze failing code and provide root cause analysis. Does NOT generate code - only deep reasoning. Supports tier-based escalation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The failing code"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Error explanation or context about what's wrong"
                    },
                    "tier": {
                        "type": "integer",
                        "enum": [1, 2, 3],
                        "default": 1,
                        "description": "Debugging tier: 1 (initial), 2 (escalated), 3 (maximum escalation)"
                    },
                    "user_feedback": {
                        "type": "string",
                        "description": "Optional user feedback for escalation (e.g., 'didn't work', 'escalate')"
                    },
                    "save_to_db": {
                        "type": "boolean",
                        "default": True,
                        "description": "Save response to MongoDB"
                    }
                },
                "required": ["code", "explanation"]
            }
        },
        {
            "name": "architecture",
            "description": "Design system architecture, flows, frameworks, and system layouts. Identifies critical hotspots.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Architecture or system design question"
                    },
                    "use_backup": {
                        "type": "boolean",
                        "default": False,
                        "description": "Use backup model instead of primary"
                    },
                    "save_to_db": {
                        "type": "boolean",
                        "default": True,
                        "description": "Save response to MongoDB"
                    }
                },
                "required": ["question"]
            }
        },
        {
            "name": "general_purpose",
            "description": "General purpose queries that don't fit into other categories. Auto-upgrades model based on complexity.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "General question"
                    },
                    "complexity": {
                        "type": "string",
                        "enum": ["simple", "medium"],
                        "default": "simple",
                        "description": "Complexity level: 'simple' for basic queries, 'medium' for complex queries (auto-upgrades model)"
                    },
                    "save_to_db": {
                        "type": "boolean",
                        "default": True,
                        "description": "Save response to MongoDB"
                    }
                },
                "required": ["question"]
            }
        },
        {
            "name": "list_mongodb_instances",
            "description": "List all available MongoDB instances configured in the system.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_active_mongodb_instance",
            "description": "Get the currently active MongoDB instance details.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "switch_mongodb_instance",
            "description": "Switch to a different MongoDB instance. All future operations will use this instance.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "instance_name": {
                        "type": "string",
                        "description": "Name of the MongoDB instance to switch to (use list_mongodb_instances to see available instances)"
                    }
                },
                "required": ["instance_name"]
            }
        }
    ]


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tool calls."""
    try:
        if name == "list_mongodb_instances":
            load_mongodb_instances()
            instances_list = []
            for inst_name, inst_data in _mongodb_instances.items():
                is_active = inst_name == _active_mongodb_instance
                instances_list.append({
                    "name": inst_name,
                    "uri": inst_data["uri"],
                    "database": inst_data["database"],
                    "collection": inst_data["collection"],
                    "active": is_active
                })
            
            result_text = "Available MongoDB Instances:\n\n"
            for inst in instances_list:
                status = "✓ ACTIVE" if inst["active"] else ""
                result_text += f"{inst['name']} {status}\n"
                result_text += f"  URI: {inst['uri']}\n"
                result_text += f"  Database: {inst['database']}\n"
                result_text += f"  Collection: {inst['collection']}\n\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
        
        elif name == "get_active_mongodb_instance":
            load_mongodb_instances()
            if not _active_mongodb_instance:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No active MongoDB instance. Please configure MongoDB instances in environment variables."
                        }
                    ]
                }
            
            instance = _mongodb_instances[_active_mongodb_instance]
            result_text = f"Currently Active MongoDB Instance: {_active_mongodb_instance}\n\n"
            result_text += f"URI: {instance['uri']}\n"
            result_text += f"Database: {instance['database']}\n"
            result_text += f"Collection: {instance['collection']}\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
        
        elif name == "switch_mongodb_instance":
            instance_name = arguments.get("instance_name")
            if not instance_name:
                raise ValueError("instance_name is required")
            
            result = switch_mongodb_instance(instance_name)
            result_text = f"✓ {result['message']}\n\n"
            result_text += f"URI: {result['uri']}\n"
            result_text += f"Database: {result['database']}\n"
            result_text += f"Collection: {result['collection']}\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
        
        # Research tools
        api_client, db_client = get_clients()
        
        if name == "topic_research":
            tool = TopicResearchTool(api_client, db_client)
            result = tool.execute(
                question=arguments["question"],
                complexity=arguments.get("complexity", "simple"),
                use_backup=arguments.get("use_backup", False),
                save_to_db=arguments.get("save_to_db", True)
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        
        elif name == "coding_research":
            tool = CodingResearchTool(api_client, db_client)
            result = tool.execute(
                question=arguments["question"],
                complexity=arguments.get("complexity", "simple"),
                save_to_db=arguments.get("save_to_db", True)
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        
        elif name == "debugging":
            tool = DebuggingTool(api_client, db_client)
            # Combine code and explanation
            question = f"Code:\n{arguments['code']}\n\nExplanation:\n{arguments['explanation']}"
            result = tool.execute(
                question=question,
                tier=arguments.get("tier", 1),
                user_feedback=arguments.get("user_feedback"),
                save_to_db=arguments.get("save_to_db", True)
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        
        elif name == "architecture":
            tool = ArchitectureTool(api_client, db_client)
            result = tool.execute(
                question=arguments["question"],
                use_backup=arguments.get("use_backup", False),
                save_to_db=arguments.get("save_to_db", True)
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        
        elif name == "general_purpose":
            tool = GeneralPurposeTool(api_client, db_client)
            result = tool.execute(
                question=arguments["question"],
                complexity=arguments.get("complexity", "simple"),
                save_to_db=arguments.get("save_to_db", True)
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        # Re-raise the exception so it can be handled as a proper JSON-RPC error
        raise Exception(f"Error executing {name}: {str(e)}") from e


async def handle_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle MCP protocol requests."""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    # Validate request_id - must be string, number, or null (for notifications)
    # For error responses, we need a valid id (string or number)
    if request_id is not None and not isinstance(request_id, (str, int)):
        # Invalid id type - can't send proper response, log and skip
        print(f"Invalid request_id type: {type(request_id)}", file=sys.stderr, flush=True)
        return None  # Skip this request
    
    # Validate request structure
    if not method:
        # Only send error if we have a valid request_id (not a notification)
        if request_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: 'method' is required"
                }
            }
        return None  # Skip notifications with errors
    
    try:
        if method == "tools/list":
            # Only respond if we have a valid request_id (not a notification)
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": list_tools()
                    }
                }
            return None  # Skip notifications
        
        elif method == "tools/call":
            # Only respond if we have a valid request_id (not a notification)
            if request_id is None:
                return None  # Skip notifications
            
            tool_name = params.get("name")
            if not tool_name:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params: 'name' is required"
                    }
                }
            
            tool_args = params.get("arguments", {})
            try:
                result = call_tool(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            except Exception as e:
                # Convert tool execution errors to proper JSON-RPC error responses
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
        
        elif method == "initialize":
            # Initialize must have a valid request_id
            if request_id is None:
                return None  # Skip notifications
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "research-toolkit",
                        "version": "1.0.0"
                    }
                }
            }
        
        else:
            # Only send error if we have a valid request_id (not a notification)
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            return None  # Skip notifications
    
    except Exception as e:
        # Only send error if we have a valid request_id (not a notification)
        if request_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        return None  # Skip notifications with errors


def main():
    """Main entry point for MCP server using stdio."""
    # Load MongoDB instances on startup
    load_mongodb_instances()
    
    # Read from stdin, write to stdout
    while True:
        request = None
        request_id = None
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            request = json.loads(line)
            request_id = request.get("id")
            
            # Run async handler in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(handle_request(request))
            loop.close()
            
            # Only print response if we have one (skip notifications)
            if response is not None:
                print(json.dumps(response), flush=True)
        
        except json.JSONDecodeError as e:
            # For parse errors, id must be null per JSON-RPC 2.0 spec
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)
        
        except Exception as e:
            # For other errors, try to preserve the request id if available
            # If request_id is None, we can't send a proper response, so log and continue
            if request_id is not None:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            else:
                # If we don't have a request_id, we can't send a proper JSON-RPC response
                # Log to stderr instead
                print(f"Internal error (no request_id): {str(e)}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
