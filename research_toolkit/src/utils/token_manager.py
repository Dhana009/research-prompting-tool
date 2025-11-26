"""
Token management for dynamic allocation based on expected output length.

Determines max_tokens parameter based on expected response size.
"""

from typing import Literal


def get_max_tokens(expected_output_length: Literal["small", "medium", "large"]) -> int:
    """
    Get max_tokens value based on expected output length.
    
    Args:
        expected_output_length: Expected output size category
            - "small": Expected 200-1000 tokens, limit 1500
            - "medium": Expected 2000-4000 tokens, limit 5000
            - "large": Expected 5000-8000 tokens, limit 10000
    
    Returns:
        Maximum tokens to allocate for the response
        
    Raises:
        ValueError: If invalid expected_output_length provided
    """
    token_limits = {
        "small": 1500,   # Expected: 200-1000 tokens
        "medium": 5000,  # Expected: 2000-4000 tokens
        "large": 10000  # Expected: 5000-8000 tokens
    }
    
    if expected_output_length not in token_limits:
        raise ValueError(
            f"Invalid expected_output_length: {expected_output_length}. "
            f"Must be one of: {list(token_limits.keys())}"
        )
    
    return token_limits[expected_output_length]


def estimate_output_length(question: str, complexity: str = "simple") -> Literal["small", "medium", "large"]:
    """
    Estimate expected output length based on question and complexity.
    
    This is a simple heuristic. More sophisticated estimation can be added later.
    
    Args:
        question: User's question text
        complexity: Complexity level (simple, moderate, large, deep)
        
    Returns:
        Estimated output length category
    """
    # Simple heuristic: longer questions or higher complexity = larger output
    question_length = len(question)
    
    # Complexity-based estimation
    if complexity in ["large", "deep"]:
        return "large"
    elif complexity == "moderate":
        return "medium"
    elif question_length > 500:  # Long questions might need medium response
        return "medium"
    else:
        return "small"

