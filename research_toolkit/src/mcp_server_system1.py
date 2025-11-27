#!/usr/bin/env python3
"""
System-1 MCP Server for Research Document Management.

Exposes System-1 tools for saving, retrieving, and listing research documents.
Supports conversation linking and metadata injection for System-2 integration.
"""

import asyncio
import os
import json
import sys
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.document_orchestrator import DocumentOrchestrator


# MongoDB configuration
_mongodb_config: Dict[str, Dict[str, Any]] = {}
_mongo_client: Optional[MongoClient] = None
_active_db_name: Optional[str] = None
_active_collection_name: Optional[str] = None


def load_mongodb_config() -> Dict[str, Dict[str, Any]]:
    """Load MongoDB configuration from environment variables."""
    global _mongodb_config
    
    # Load default instance
    if os.getenv("MONGODB_CONNECTION_STRING"):
        _mongodb_config["default"] = {
            "uri": os.getenv("MONGODB_CONNECTION_STRING"),
            "database": os.getenv("MONGODB_DATABASE", "research_toolkit"),
            "collection": os.getenv("MONGODB_COLLECTION", "research_documents")
        }
    
    return _mongodb_config


def get_mongo_client() -> MongoClient:
    """Get or create MongoDB client."""
    global _mongo_client, _active_db_name, _active_collection_name
    
    if _mongo_client is None:
        config = load_mongodb_config()
        if "default" not in config:
            # Return a mock-like client for testing scenarios
            # In real usage, this should be configured via environment variables
            raise ValueError("MongoDB configuration not found. Set MONGODB_CONNECTION_STRING environment variable.")
        
        default_config = config["default"]
        _mongo_client = MongoClient(default_config["uri"])
        _active_db_name = default_config["database"]
        _active_collection_name = default_config["collection"]
    
    return _mongo_client


def list_tools() -> List[Dict[str, Any]]:
    """List all available System-1 MCP tools."""
    return [
        {
            "name": "save_research_document",
            "description": "Save a System-1 research document into MongoDB",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Research question"
                    },
                    "markdown_content": {
                        "type": "string",
                        "description": "Markdown content of the research response"
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "Optional parent document ID for follow-up questions"
                    }
                },
                "required": ["question", "markdown_content"]
            }
        },
        {
            "name": "get_research_document",
            "description": "Fetch a research document from MongoDB",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Document ID to retrieve"
                    }
                },
                "required": ["document_id"]
            }
        },
        {
            "name": "list_documents",
            "description": "List all documents in the research collection",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle System-1 MCP tool calls."""
    mongo_client = get_mongo_client()
    
    # Get active database and collection names
    # Try to get from config, but use defaults if config not available (for testing)
    config = load_mongodb_config()
    if "default" in config:
        default_config = config["default"]
        db_name = default_config["database"]
        collection_name = default_config["collection"]
    else:
        # Fallback defaults (for testing scenarios)
        db_name = os.getenv("MONGODB_DATABASE", "research_toolkit")
        collection_name = os.getenv("MONGODB_COLLECTION", "research_documents")
    
    if name == "save_research_document":
        question = arguments.get("question")
        markdown_content = arguments.get("markdown_content")
        parent_id = arguments.get("parent_id")
        
        if not question or not markdown_content:
            raise ValueError("InvalidInput: missing required fields (question or markdown_content)")
        
        result = DocumentOrchestrator.save_document(
            question=question,
            markdown_content=markdown_content,
            parent_id=parent_id,
            mongo_client=mongo_client,
            database_name=db_name,
            collection_name=collection_name
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    
    elif name == "get_research_document":
        document_id = arguments.get("document_id")
        if not document_id:
            raise ValueError("InvalidInput: document_id required")
        
        db = mongo_client[db_name]
        collection = db[collection_name]
        
        doc = collection.find_one({"document_id": document_id})
        
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(doc, indent=2) if doc else json.dumps(None)
                }
            ]
        }
    
    elif name == "list_documents":
        db = mongo_client[db_name]
        collection = db[collection_name]
        
        docs = list(collection.find({}))
        
        # Convert ObjectId to string for JSON serialization
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(docs, indent=2)
                }
            ]
        }
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle MCP protocol requests."""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    # Validate request_id - must be string, number, or null (for notifications)
    if request_id is not None and not isinstance(request_id, (str, int)):
        print(f"Invalid request_id type: {type(request_id)}", file=sys.stderr, flush=True)
        return None
    
    # Validate request structure
    if not method:
        if request_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: 'method' is required"
                }
            }
        return None
    
    try:
        if method == "tools/list":
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": list_tools()
                    }
                }
            return None
        
        elif method == "tools/call":
            if request_id is None:
                return None
            
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
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
        
        elif method == "initialize":
            if request_id is None:
                return None
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "system1",
                        "version": "1.0.0"
                    }
                }
            }
        
        else:
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            return None
    
    except Exception as e:
        if request_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        return None


def main():
    """Main entry point for MCP server using stdio."""
    # Load MongoDB config on startup
    load_mongodb_config()
    
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
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id if request_id is not None else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()

