#!/usr/bin/env python3
"""
System-1 Full Verification Script
Verifies MCP server, modules, MongoDB, and tool registration.
"""

import sys
import os
import inspect
from pathlib import Path

print("=" * 60)
print("SYSTEM-1 FULL VERIFICATION SCRIPT")
print("=" * 60)

# STEP 1 - Show the full path of the running MCP server
print("\n[STEP 1] MCP Server File Path:")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path[:3]}")  # First 3 entries
print(f"Current working directory: {os.getcwd()}")

# STEP 2 - Verify System-1 MCP tools are registered
print("\n[STEP 2] System-1 MCP Tools Registration:")
try:
    from src.mcp_server_system1 import list_tools
    tools = list_tools()
    tool_names = [tool["name"] for tool in tools]
    print(f"Tools loaded: {tool_names}")
    
    expected_tools = ["save_research_document", "get_research_document", "list_documents"]
    missing_tools = [t for t in expected_tools if t not in tool_names]
    
    if missing_tools:
        print(f"❌ MISSING TOOLS: {missing_tools}")
    else:
        print("✅ All expected tools are registered")
        
except Exception as e:
    print(f"❌ ERROR loading tools: {e}")

# STEP 3 - Verify all System-1 modules are imported correctly
print("\n[STEP 3] System-1 Core Modules Import:")
modules_to_test = [
    "src.utils.metadata_builder",
    "src.utils.document_assembler",
    "src.utils.mongo_writer",
    "src.utils.document_orchestrator"
]

all_imported = True
for module_name in modules_to_test:
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
    except Exception as e:
        print(f"❌ {module_name}: {e}")
        all_imported = False

if all_imported:
    print("✅ All System-1 core modules successfully imported.")

# STEP 4 - Verify MongoDB configuration
print("\n[STEP 4] MongoDB Configuration:")
mongodb_conn = os.getenv("MONGODB_CONNECTION_STRING")
mongodb_db = os.getenv("MONGODB_DATABASE", "research_toolkit")
mongodb_coll = os.getenv("MONGODB_COLLECTION", "research_documents")

print(f"MONGODB_CONNECTION_STRING = {'***SET***' if mongodb_conn else '❌ NOT SET'}")
print(f"MONGODB_DATABASE = {mongodb_db}")
print(f"MONGODB_COLLECTION = {mongodb_coll}")

# STEP 5 - Ping MongoDB
print("\n[STEP 5] MongoDB Connection Test:")
if mongodb_conn:
    try:
        from pymongo import MongoClient
        client = MongoClient(mongodb_conn, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        databases = client.list_database_names()
        print(f"✅ MongoDB connection successful")
        print(f"Available databases: {databases[:5]}...")  # First 5
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        client = None
else:
    print("⚠️  Skipping MongoDB connection test (no connection string)")
    client = None

# STEP 6 - List documents in the collection
print("\n[STEP 6] Document Count in Collection:")
if client and mongodb_db and mongodb_coll:
    try:
        db = client[mongodb_db]
        coll = db[mongodb_coll]
        doc_count = coll.count_documents({})
        print(f"✅ Documents found: {doc_count}")
        
        # Show sample document IDs if any exist
        if doc_count > 0:
            sample_docs = list(coll.find({}, {"document_id": 1, "conversation_id": 1}).limit(3))
            print(f"Sample documents:")
            for doc in sample_docs:
                print(f"  - {doc.get('document_id', 'N/A')} (CV: {doc.get('conversation_id', 'N/A')})")
    except Exception as e:
        print(f"❌ Error counting documents: {e}")
else:
    print("⚠️  Skipping document count (MongoDB not connected)")

# STEP 7 - Verify the MCP server entrypoint
print("\n[STEP 7] MCP Server File Path:")
try:
    import src.mcp_server_system1
    server_file = inspect.getfile(src.mcp_server_system1)
    print(f"✅ System-1 MCP server loaded from: {server_file}")
    
    # Verify it's the correct file
    expected_file = Path("research_toolkit/src/mcp_server_system1.py").resolve()
    actual_file = Path(server_file).resolve()
    
    if expected_file == actual_file or actual_file.name == "mcp_server_system1.py":
        print("✅ Correct MCP server file is being used")
    else:
        print(f"⚠️  File path differs from expected: {expected_file}")
        
except Exception as e:
    print(f"❌ ERROR loading MCP server: {e}")

# Final Summary
print("\n" + "=" * 60)
print("FULL VERIFICATION REPORT:")
print("=" * 60)

# Compile results
results = {
    "MCP Server File": server_file if 'server_file' in locals() else "❌ NOT FOUND",
    "Tools Loaded": tool_names if 'tool_names' in locals() else "❌ NOT LOADED",
    "Modules Imported": "✅ OK" if all_imported else "❌ FAILED",
    "MongoDB Settings": "✅ OK" if mongodb_conn else "❌ NOT SET",
    "MongoDB Connection": "✅ OK" if client else "❌ FAILED",
    "Document Count": doc_count if 'doc_count' in locals() else "N/A",
    "MCP Server Path": server_file if 'server_file' in locals() else "❌ NOT FOUND"
}

for key, value in results.items():
    print(f"- {key}: {value}")

print("=" * 60)


