#!/usr/bin/env python3
"""
Test script for the Research Toolkit MCP Server.
Tests all tools to verify they work correctly.
"""

import json
import subprocess
import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent
server_path = project_root / "src" / "mcp_server.py"

# Check if API key is set
if not os.getenv("ROUTELLM_API_KEY"):
    print("[ERROR] ROUTELLM_API_KEY environment variable is not set!")
    print("\nPlease set it first:")
    print("  Windows PowerShell: $env:ROUTELLM_API_KEY='your_key_here'")
    print("  Windows CMD: set ROUTELLM_API_KEY=your_key_here")
    print("  macOS/Linux: export ROUTELLM_API_KEY='your_key_here'")
    sys.exit(1)

def send_request(method, params=None, request_id=1):
    """Send a JSON-RPC request to the server"""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {}
    }
    return json.dumps(request) + "\n"

def test_initialize():
    """Test 1: Initialize"""
    print("\n[TEST 1] Initialize...")
    request = send_request("initialize", {})
    result = subprocess.run(
        ["python", str(server_path)],
        input=request,
        text=True,
        capture_output=True,
        cwd=str(project_root)
    )
    if result.returncode == 0:
        try:
            response = json.loads(result.stdout.strip())
            if "result" in response and "serverInfo" in response["result"]:
                print(f"[OK] Initialize successful: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}")
                return True
        except json.JSONDecodeError:
            pass
    print(f"[FAIL] Initialize failed")
    if result.stderr:
        print(f"  stderr: {result.stderr[:200]}")
    if result.stdout:
        print(f"  stdout: {result.stdout[:200]}")
    return False

def test_tools_list():
    """Test 2: List all tools"""
    print("\n[TEST 2] List Tools...")
    request = send_request("tools/list", {})
    result = subprocess.run(
        ["python", str(server_path)],
        input=request,
        text=True,
        capture_output=True,
        cwd=str(project_root)
    )
    if result.returncode == 0:
        try:
            response = json.loads(result.stdout.strip())
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"[OK] Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}")
                return True
        except json.JSONDecodeError:
            pass
    print(f"[FAIL] Tools list failed")
    if result.stderr:
        print(f"  stderr: {result.stderr[:200]}")
    if result.stdout:
        print(f"  stdout: {result.stdout[:200]}")
    return False

def test_tool_call(tool_name, arguments, description):
    """Test a specific tool call"""
    print(f"\n[TEST] {description} ({tool_name})...")
    request = send_request("tools/call", {
        "name": tool_name,
        "arguments": arguments
    })
    result = subprocess.run(
        ["python", str(server_path)],
        input=request,
        text=True,
        capture_output=True,
        timeout=60,
        cwd=str(project_root)
    )
    if result.returncode == 0:
        try:
            response = json.loads(result.stdout.strip())
            if "result" in response:
                if "content" in response["result"] and len(response["result"]["content"]) > 0:
                    content = response["result"]["content"][0].get("text", "")
                    print(f"[OK] Success! Response length: {len(content)} characters")
                    print(f"   Preview: {content[:100]}...")
                    return True
                else:
                    print(f"[OK] Success! (no content preview available)")
                    return True
            elif "error" in response:
                print(f"[FAIL] Error: {response['error'].get('message', 'Unknown error')}")
                return False
        except json.JSONDecodeError as e:
            print(f"[FAIL] Invalid JSON response: {result.stdout[:200]}")
            print(f"   JSON Error: {e}")
            return False
    print(f"[FAIL] Failed")
    if result.stderr:
        print(f"  stderr: {result.stderr[:200]}")
    if result.stdout:
        print(f"  stdout: {result.stdout[:200]}")
    return False

def main():
    print("=" * 60)
    print("Research Toolkit MCP Server - Test Suite")
    print("=" * 60)
    
    # Test 1: Initialize
    if not test_initialize():
        print("\n[FAIL] Server initialization failed. Cannot continue.")
        sys.exit(1)
    
    # Test 2: List tools
    if not test_tools_list():
        print("\n[FAIL] Tools list failed. Cannot continue.")
        sys.exit(1)
    
    # Test 3: Research Tools
    print("\n" + "=" * 60)
    print("Testing Research Tools")
    print("=" * 60)
    
    test_tool_call(
        "topic_research",
        {"question": "What is Python? Answer in one sentence.", "complexity": "simple"},
        "Topic Research (Simple)"
    )
    
    test_tool_call(
        "coding_research",
        {"question": "What are Python decorators? Answer in one sentence.", "complexity": "simple"},
        "Coding Research (Simple)"
    )
    
    # Test 4: MongoDB Tools
    print("\n" + "=" * 60)
    print("Testing MongoDB Management Tools")
    print("=" * 60)
    
    test_tool_call(
        "list_mongodb_instances",
        {},
        "List MongoDB Instances"
    )
    
    test_tool_call(
        "get_active_mongodb_instance",
        {},
        "Get Active MongoDB Instance"
    )
    
    print("\n" + "=" * 60)
    print("[OK] All tests completed!")
    print("=" * 60)
    print("\nIf all tests passed, your MCP server is ready to use!")
    print("Next step: Configure it in Cursor MCP settings")

if __name__ == "__main__":
    main()



