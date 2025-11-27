#!/usr/bin/env python3
"""
Test script for the Research Toolkit MCP Server - Protocol Tests Only.
Tests JSON-RPC protocol compliance without requiring API keys.
"""

import json
import subprocess
import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent
server_path = project_root / "src" / "mcp_server.py"

def send_request(method, params=None, request_id=1):
    """Send a JSON-RPC request to the server"""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {}
    }
    return json.dumps(request) + "\n"

def test_response_format(response_text, test_name):
    """Validate JSON-RPC 2.0 response format"""
    try:
        response = json.loads(response_text.strip())
        
        # Check required fields
        if "jsonrpc" not in response:
            print(f"[FAIL] {test_name}: Missing 'jsonrpc' field")
            return False
        
        if response["jsonrpc"] != "2.0":
            print(f"[FAIL] {test_name}: Invalid jsonrpc version: {response['jsonrpc']}")
            return False
        
        # Check id field (must be string, number, or null for parse errors)
        if "id" not in response:
            print(f"[FAIL] {test_name}: Missing 'id' field")
            return False
        
        if response["id"] is not None:
            if not isinstance(response["id"], (str, int)):
                print(f"[FAIL] {test_name}: Invalid 'id' type: {type(response['id'])}")
                return False
        
        # Check for result or error (but not both)
        has_result = "result" in response
        has_error = "error" in response
        
        if has_result and has_error:
            print(f"[FAIL] {test_name}: Response has both 'result' and 'error'")
            return False
        
        if not has_result and not has_error:
            print(f"[FAIL] {test_name}: Response has neither 'result' nor 'error'")
            return False
        
        # Validate error structure if present
        if has_error:
            error = response["error"]
            if "code" not in error or "message" not in error:
                print(f"[FAIL] {test_name}: Error object missing 'code' or 'message'")
                return False
        
        print(f"[OK] {test_name}: Valid JSON-RPC 2.0 response")
        return True
        
    except json.JSONDecodeError as e:
        print(f"[FAIL] {test_name}: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"[FAIL] {test_name}: Unexpected error - {e}")
        return False

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
    
    if result.returncode != 0:
        print(f"[FAIL] Process exited with code {result.returncode}")
        if result.stderr:
            print(f"  stderr: {result.stderr[:200]}")
        return False
    
    if not test_response_format(result.stdout, "Initialize"):
        print(f"  Response: {result.stdout[:200]}")
        return False
    
    try:
        response = json.loads(result.stdout.strip())
        if "result" in response and "serverInfo" in response["result"]:
            print(f"  Server: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}")
    except:
        pass
    
    return True

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
    
    if result.returncode != 0:
        print(f"[FAIL] Process exited with code {result.returncode}")
        if result.stderr:
            print(f"  stderr: {result.stderr[:200]}")
        return False
    
    if not test_response_format(result.stdout, "List Tools"):
        print(f"  Response: {result.stdout[:200]}")
        return False
    
    try:
        response = json.loads(result.stdout.strip())
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"  Found {len(tools)} tools")
    except:
        pass
    
    return True

def test_invalid_method():
    """Test 3: Invalid method"""
    print("\n[TEST 3] Invalid Method...")
    request = send_request("invalid/method", {})
    result = subprocess.run(
        ["python", str(server_path)],
        input=request,
        text=True,
        capture_output=True,
        cwd=str(project_root)
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Process exited with code {result.returncode}")
        return False
    
    if not test_response_format(result.stdout, "Invalid Method"):
        print(f"  Response: {result.stdout[:200]}")
        return False
    
    try:
        response = json.loads(result.stdout.strip())
        if "error" in response:
            print(f"  Error code: {response['error']['code']}")
            print(f"  Error message: {response['error']['message']}")
    except:
        pass
    
    return True

def test_invalid_json():
    """Test 4: Invalid JSON"""
    print("\n[TEST 4] Invalid JSON...")
    invalid_request = "not valid json\n"
    result = subprocess.run(
        ["python", str(server_path)],
        input=invalid_request,
        text=True,
        capture_output=True,
        cwd=str(project_root)
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Process exited with code {result.returncode}")
        return False
    
    if not test_response_format(result.stdout, "Invalid JSON"):
        print(f"  Response: {result.stdout[:200]}")
        return False
    
    try:
        response = json.loads(result.stdout.strip())
        if "error" in response:
            print(f"  Error code: {response['error']['code']}")
            print(f"  Error message: {response['error']['message']}")
            # For parse errors, id should be null
            if response["error"]["code"] == -32700:
                if response["id"] is None:
                    print("  [OK] Parse error correctly has null id")
                else:
                    print(f"  [WARN] Parse error has non-null id: {response['id']}")
    except:
        pass
    
    return True

def test_missing_method():
    """Test 5: Missing method"""
    print("\n[TEST 5] Missing Method...")
    request = {
        "jsonrpc": "2.0",
        "id": 1
        # Missing "method" field
    }
    request_text = json.dumps(request) + "\n"
    
    result = subprocess.run(
        ["python", str(server_path)],
        input=request_text,
        text=True,
        capture_output=True,
        cwd=str(project_root)
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Process exited with code {result.returncode}")
        return False
    
    if not test_response_format(result.stdout, "Missing Method"):
        print(f"  Response: {result.stdout[:200]}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("Research Toolkit MCP Server - Protocol Compliance Tests")
    print("=" * 60)
    print("\nThese tests verify JSON-RPC 2.0 protocol compliance")
    print("without requiring API keys or external services.\n")
    
    results = []
    
    results.append(("Initialize", test_initialize()))
    results.append(("List Tools", test_tools_list()))
    results.append(("Invalid Method", test_invalid_method()))
    results.append(("Invalid JSON", test_invalid_json()))
    results.append(("Missing Method", test_missing_method()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[OK] All protocol tests passed! MCP server is JSON-RPC 2.0 compliant.")
        return 0
    else:
        print("\n[FAIL] Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())












