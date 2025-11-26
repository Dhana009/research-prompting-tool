"""
Output handler for markdown responses.

Handles truncation detection, auto-refetch, and response concatenation.
"""

from typing import Dict, Any, Optional, List
import re


def detect_truncation(api_response: Dict[str, Any]) -> bool:
    """
    Detect if API response was truncated.
    
    Args:
        api_response: API response dictionary from RouteLLM
        
    Returns:
        True if response was truncated, False otherwise
    """
    if "choices" not in api_response or len(api_response["choices"]) == 0:
        return False
    
    choice = api_response["choices"][0]
    
    # Check finish_reason field
    finish_reason = choice.get("finish_reason")
    if finish_reason == "length":
        return True
    
    # Also check if content seems incomplete (ends abruptly)
    message = choice.get("message", {})
    content = message.get("content", "")
    
    # Heuristic: if content ends with incomplete markdown or code block
    if content:
        # Check for incomplete code blocks
        code_blocks = re.findall(r'```', content)
        if len(code_blocks) % 2 != 0:  # Odd number means unclosed block
            return True
        
        # Check for incomplete markdown lists or headers
        if content.rstrip().endswith(('*', '-', '#', '`')) and not content.rstrip().endswith('```'):
            return True
    
    return False


def extract_content(api_response: Dict[str, Any]) -> str:
    """
    Extract markdown content from API response.
    
    Args:
        api_response: API response dictionary from RouteLLM
        
    Returns:
        Markdown content string
        
    Raises:
        ValueError: If response structure is invalid
    """
    if "choices" not in api_response or len(api_response["choices"]) == 0:
        raise ValueError("Invalid API response: no choices found")
    
    choice = api_response["choices"][0]
    message = choice.get("message", {})
    content = message.get("content", "")
    
    if not content:
        raise ValueError("Invalid API response: no content in message")
    
    return content


def concatenate_responses(responses: List[str]) -> str:
    """
    Concatenate multiple response strings into a single markdown document.
    
    Args:
        responses: List of markdown response strings
        
    Returns:
        Concatenated markdown string
    """
    if not responses:
        return ""
    
    if len(responses) == 1:
        return responses[0]
    
    # Join responses with a separator
    # Add a horizontal rule between continuation parts
    separator = "\n\n---\n\n*[Continued from previous response]*\n\n"
    
    return separator.join(responses)


def refetch_incomplete(
    api_client: Any,
    model: str,
    messages: List[Dict[str, str]],
    previous_content: str,
    max_tokens: int,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Refetch incomplete response by continuing from where it left off.
    
    Args:
        api_client: RouteLLM API client instance
        model: Model name
        messages: Original message list
        previous_content: Content from previous (truncated) response
        max_tokens: Maximum tokens for continuation
        temperature: Temperature setting
        
    Returns:
        Complete API response dictionary
    """
    # Create continuation message
    continuation_messages = messages.copy()
    continuation_messages.append({
        "role": "assistant",
        "content": previous_content
    })
    continuation_messages.append({
        "role": "user",
        "content": "Please continue from where you left off."
    })
    
    # Make continuation request
    continuation_response = api_client.chat_completion(
        model=model,
        messages=continuation_messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    return continuation_response


def get_complete_response(
    api_client: Any,
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float = 0.7,
    max_iterations: int = 3
) -> str:
    """
    Get complete response, automatically refetching if truncated.
    
    This function handles the full cycle:
    1. Make initial request
    2. Check for truncation
    3. Refetch if needed (up to max_iterations)
    4. Concatenate all parts
    
    Args:
        api_client: RouteLLM API client instance
        model: Model name
        messages: Message list for the request
        max_tokens: Maximum tokens per request
        temperature: Temperature setting
        max_iterations: Maximum number of refetch attempts
        
    Returns:
        Complete markdown content string
    """
    all_responses = []
    current_messages = messages
    iteration = 0
    
    while iteration < max_iterations:
        # Make API request
        response = api_client.chat_completion(
            model=model,
            messages=current_messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract content
        content = extract_content(response)
        all_responses.append(content)
        
        # Check if truncated
        if not detect_truncation(response):
            # Complete response received
            break
        
        # Prepare for continuation
        current_messages = messages.copy()
        current_messages.append({
            "role": "assistant",
            "content": content
        })
        current_messages.append({
            "role": "user",
            "content": "Please continue from where you left off."
        })
        
        iteration += 1
    
    # Concatenate all response parts
    complete_content = concatenate_responses(all_responses)
    
    return complete_content

