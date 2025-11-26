"""
Mock models and API clients for testing without real API calls.

These mocks simulate the RouteLLM API responses to avoid wasting tokens.
"""

from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock


class MockRouteLLMClient:
    """Mock client for RouteLLM API that returns sample responses."""
    
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.call_count = 0
        self.last_model = None
        self.last_prompt = None
    
    def chat_completion(
        self,
        model: str,
        messages: list,
        max_tokens: int = 1500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Mock chat completion that returns sample responses based on model.
        
        Args:
            model: Model name (used to determine response type)
            messages: List of message dicts
            max_tokens: Maximum tokens (for testing truncation)
            temperature: Temperature setting (not used in mock)
        
        Returns:
            Mock API response dict
        """
        self.call_count += 1
        self.last_model = model
        self.last_prompt = messages[-1]["content"] if messages else ""
        
        # Import sample responses
        from tests.fixtures.test_data import (
            SAMPLE_TOPIC_RESEARCH_RESPONSE,
            SAMPLE_CODING_RESEARCH_RESPONSE,
            SAMPLE_DEBUGGING_RESPONSE_TIER1,
            SAMPLE_ARCHITECTURE_RESPONSE,
            SAMPLE_GENERAL_PURPOSE_RESPONSE,
            MOCK_API_RESPONSE_SUCCESS,
            MOCK_API_RESPONSE_TRUNCATED
        )
        
        # Determine response based on model or prompt content
        if "debugging" in self.last_prompt.lower() or "deepseek" in model.lower():
            content = SAMPLE_DEBUGGING_RESPONSE_TIER1
        elif "coding" in self.last_prompt.lower() or "llama" in model.lower():
            content = SAMPLE_CODING_RESEARCH_RESPONSE
        elif "architecture" in self.last_prompt.lower() or "claude" in model.lower():
            content = SAMPLE_ARCHITECTURE_RESPONSE
        elif "topic" in self.last_prompt.lower() or "gemini" in model.lower():
            content = SAMPLE_TOPIC_RESEARCH_RESPONSE
        else:
            content = SAMPLE_GENERAL_PURPOSE_RESPONSE
        
        # Simulate truncation if max_tokens is very low
        if max_tokens < 100:
            response = MOCK_API_RESPONSE_TRUNCATED.copy()
            response["choices"][0]["message"]["content"] = content[:50] + "..."
            return response
        
        # Return full response
        response = MOCK_API_RESPONSE_SUCCESS.copy()
        response["choices"][0]["message"]["content"] = content
        return response
    
    def reset(self):
        """Reset mock state."""
        self.call_count = 0
        self.last_model = None
        self.last_prompt = None


class MockMongoDBClient:
    """Mock MongoDB client for testing without real database."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.documents = []
        self.insert_count = 0
        self.find_count = 0
    
    def insert_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Mock insert operation."""
        self.documents.append(document.copy())
        self.insert_count += 1
        return {"inserted_id": f"mock_id_{self.insert_count}"}
    
    def find_one(self, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mock find one operation."""
        self.find_count += 1
        for doc in self.documents:
            if all(doc.get(k) == v for k, v in filter.items()):
                return doc.copy()
        return None
    
    def find(self, filter: Dict[str, Any] = None) -> list:
        """Mock find operation."""
        self.find_count += 1
        if filter is None:
            return [doc.copy() for doc in self.documents]
        results = []
        for doc in self.documents:
            if all(doc.get(k) == v for k, v in filter.items()):
                results.append(doc.copy())
        return results
    
    def reset(self):
        """Reset mock state."""
        self.documents = []
        self.insert_count = 0
        self.find_count = 0

