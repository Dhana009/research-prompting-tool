"""
Test fixtures and sample data for testing without calling real AI models.

All tests should use these fixtures to avoid wasting tokens during development.
Real model calls will only happen during end-to-end testing once the system is ready.
"""

# Sample AI model responses (markdown format)
SAMPLE_TOPIC_RESEARCH_RESPONSE = """# Topic Research Response

This is a sample markdown response for topic research.

## Key Points

1. First point
2. Second point
3. Third point

## Summary

This is a sample response that would come from the AI model.
"""

SAMPLE_CODING_RESEARCH_RESPONSE = """# Coding Research Response

Here's a sample coding research response with code examples.

## Best Practices

```python
def example_function():
    # Sample code
    return "Hello, World!"
```

## Edge Cases

- Handle None values
- Validate input types
- Error handling
"""

SAMPLE_DEBUGGING_RESPONSE_TIER1 = """# Debugging Analysis - Tier 1

## Root Cause Analysis

The issue appears to be related to:
1. Type mismatch
2. Missing validation
3. Incorrect data flow

## Recommended Fix

Review the data types and add proper validation.
"""

SAMPLE_DEBUGGING_RESPONSE_TIER2 = """# Debugging Analysis - Tier 2

## Deep Analysis

After reviewing the code more carefully:

1. **Type Issue**: The function expects a string but receives an integer
2. **Validation Gap**: No input validation before processing
3. **Flow Problem**: Data transformation happens in wrong order

## Detailed Solution

The root cause is a type conversion issue. Add explicit type checking.
"""

SAMPLE_ARCHITECTURE_RESPONSE = """# Architecture Design

## System Layout

```
[Component A] -> [Component B] -> [Component C]
```

## Critical Hotspots

1. Database connection pooling
2. API rate limiting
3. Error handling middleware
"""

SAMPLE_GENERAL_PURPOSE_RESPONSE = """# General Purpose Response

This is a sample response for general purpose queries.

## Answer

The answer to your question is: [sample response]
"""

# Sample question IDs
SAMPLE_QUESTION_ID_TR = "TR-20251126-105433IST-WED-QX18"
SAMPLE_QUESTION_ID_CR = "CR-20251126-183212IST-WED-AX39"
SAMPLE_QUESTION_ID_DB = "DB-20251126-120000IST-WED-BY45"
SAMPLE_QUESTION_ID_AR = "AR-20251126-140000IST-WED-CZ56"
SAMPLE_QUESTION_ID_GP = "GP-20251126-160000IST-WED-DE67"

# Sample MongoDB documents
SAMPLE_DOCUMENT_TOPIC_RESEARCH = {
    "question": "What is test-driven development?",
    "markdown_content": SAMPLE_TOPIC_RESEARCH_RESPONSE,
    "category": "topic_research",
    "sub_category": None,
    "question_id": SAMPLE_QUESTION_ID_TR,
    "timestamp_ist": "2025-11-26 10:54:33 IST (Wednesday)",
    "model_used": "gemini-2.5-flash",
    "complexity_score": 3,
    "contains_code": False,
    "estimated_segments": 1,
    "language_tags": [],
    "segments": [],
    "vectors": [],
    "graph_nodes": [],
    "graph_edges": []
}

SAMPLE_DOCUMENT_CODING_RESEARCH = {
    "question": "How to implement error handling in Python?",
    "markdown_content": SAMPLE_CODING_RESEARCH_RESPONSE,
    "category": "coding_research",
    "sub_category": None,
    "question_id": SAMPLE_QUESTION_ID_CR,
    "timestamp_ist": "2025-11-26 18:32:12 IST (Wednesday)",
    "model_used": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "complexity_score": 5,
    "contains_code": True,
    "estimated_segments": 2,
    "language_tags": ["python"],
    "segments": [],
    "vectors": [],
    "graph_nodes": [],
    "graph_edges": []
}

# Mock API responses (for RouteLLM API simulation)
MOCK_API_RESPONSE_SUCCESS = {
    "choices": [{
        "message": {
            "content": SAMPLE_TOPIC_RESEARCH_RESPONSE
        }
    }],
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 200,
        "total_tokens": 300
    }
}

MOCK_API_RESPONSE_TRUNCATED = {
    "choices": [{
        "message": {
            "content": SAMPLE_TOPIC_RESEARCH_RESPONSE[:100] + "..."
        },
        "finish_reason": "length"
    }],
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150
    }
}

MOCK_API_RESPONSE_ERROR = {
    "error": {
        "message": "API rate limit exceeded",
        "type": "rate_limit_error",
        "code": 429
    }
}

