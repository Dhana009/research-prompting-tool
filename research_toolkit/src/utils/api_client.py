"""
RouteLLM API client for making chat completion requests.

Uses OpenAI SDK format with RouteLLM base URL.
"""

from typing import Dict, Any, List, Optional, Iterator
import os
import sys
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai import APIConnectionError, APIError, APIStatusError, AuthenticationError


class RouteLLMClient:
    """
    Client for interacting with RouteLLM API using OpenAI SDK format.
    
    Handles chat completion requests with error handling and rate limit management.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize RouteLLM API client.
        
        Args:
            api_key: RouteLLM API key. If None, reads from ROUTELLM_API_KEY env var.
            base_url: RouteLLM API base URL. If None, uses default RouteLLM URL.
        """
        if api_key is None:
            api_key = os.getenv("ROUTELLM_API_KEY")
            if not api_key:
                raise ValueError(
                    "RouteLLM API key required. Provide as argument or "
                    "set ROUTELLM_API_KEY environment variable."
                )
        
        if base_url is None:
            # Default to RouteLLM Abacus AI endpoint (as per RouteLLM documentation)
            # This matches the exact format: base_url="https://routellm.abacus.ai/v1"
            env_url = os.getenv("ROUTELLM_API_URL")
            if env_url:
                base_url = env_url
            else:
                base_url = "https://routellm.abacus.ai/v1"
        
        self.api_key = api_key
        self.base_url = base_url
        
        # Initialize OpenAI client with RouteLLM base URL
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1500,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Make a chat completion request to RouteLLM API.
        
        Args:
            model: Model name to use (e.g., "gpt-5", "gemini-2.5-flash")
            messages: List of message dictionaries with "role" and "content" keys
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            stream: Whether to stream the response. Default: False
            
        Returns:
            API response dictionary with:
            - choices: List of response choices
            - usage: Token usage information (if not streaming)
            
            If streaming=True, returns an iterator of chunks.
            
        Raises:
            ValueError: If API returns an error response
            Exception: For other errors (connection, timeout, etc.)
        """
        try:
            # Create chat completion (exact format from RouteLLM docs)
            chat_completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream
            )
            
            if stream:
                # Return iterator for streaming
                return self._handle_stream_response(chat_completion)
            else:
                # Return standard response dict
                # Access content directly: chat_completion.choices[0].message.content
                return self._convert_to_dict(chat_completion)
                
        except APIConnectionError as e:
            # Connection errors (network issues, DNS, etc.)
            error_msg = f"Failed to connect to RouteLLM API at {self.base_url}. "
            error_msg += f"Please check your internet connection and verify the base URL is correct. "
            error_msg += f"Error details: {str(e)}"
            raise ConnectionError(error_msg)
        except AuthenticationError as e:
            # Authentication errors (invalid API key)
            error_msg = "Invalid API key. Please check your ROUTELLM_API_KEY environment variable. "
            error_msg += f"Error details: {str(e)}"
            raise ValueError(error_msg)
        except APIStatusError as e:
            # HTTP status errors (4xx, 5xx)
            status_code = e.status_code if hasattr(e, 'status_code') else "unknown"
            error_message = str(e)
            
            if status_code == 429:
                raise ValueError("Rate limit exceeded. Please wait before retrying.")
            elif status_code == 401:
                raise ValueError("Invalid API key. Check your ROUTELLM_API_KEY.")
            elif status_code == 404:
                raise ValueError(f"Model not found: {model}. Please check the model name.")
            elif status_code == 400:
                raise ValueError(f"Bad request: {error_message}. Please check your parameters.")
            else:
                raise ValueError(f"API error (HTTP {status_code}): {error_message}")
        except APIError as e:
            # General API errors
            error_message = str(e)
            raise Exception(f"RouteLLM API error: {error_message}")
        except Exception as e:
            # Catch-all for any other exceptions
            error_message = str(e)
            error_type = type(e).__name__
            raise Exception(f"Unexpected error ({error_type}): {error_message}")
    
    def _convert_to_dict(self, completion: ChatCompletion) -> Dict[str, Any]:
        """
        Convert OpenAI ChatCompletion object to dictionary format.
        
        Uses exact format: chat_completion.choices[0].message.content
        
        Args:
            completion: ChatCompletion object from OpenAI SDK
            
        Returns:
            Dictionary with choices and usage
        """
        # Access content directly as shown in the example
        choice = completion.choices[0]
        message_content = choice.message.content if choice.message.content else ""
        
        return {
            "choices": [
                {
                    "message": {
                        "role": choice.message.role,
                        "content": message_content
                    },
                    "finish_reason": choice.finish_reason
                }
            ],
            "usage": {
                "prompt_tokens": completion.usage.prompt_tokens if completion.usage else 0,
                "completion_tokens": completion.usage.completion_tokens if completion.usage else 0,
                "total_tokens": completion.usage.total_tokens if completion.usage else 0
            }
        }
    
    def _handle_stream_response(self, stream: Iterator[ChatCompletionChunk]) -> Iterator[Dict[str, Any]]:
        """
        Handle streaming response chunks.
        
        Uses exact format from RouteLLM docs:
        - Check event.choices[0].finish_reason
        - Check event.choices[0].delta.content
        
        Args:
            stream: Iterator of ChatCompletionChunk objects
            
        Yields:
            Dictionary chunks with delta content
        """
        for event in stream:
            if event.choices[0].finish_reason:
                # Finish reason indicates completion
                yield {
                    "choices": [{
                        "finish_reason": event.choices[0].finish_reason
                    }]
                }
            else:
                # Check for delta content
                if event.choices[0].delta:
                    delta_content = event.choices[0].delta.content
                    if delta_content:
                        yield {
                            "choices": [{
                                "delta": {
                                    "content": delta_content
                                }
                            }]
                        }
