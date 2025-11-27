"""
Coding Research Tool.

Provides best coding patterns, implementation guides, edge cases, and pitfalls.
"""

from typing import Optional
from src.tools.base_tool import BaseTool
from src.models.document import Category
from src.router.model_router import get_model_for_tool
from src.utils.token_manager import get_max_tokens, estimate_output_length
from src.utils.output_handler import get_complete_response
from src.storage.mongodb import MongoDBClient
from src.utils.api_client import RouteLLMClient


class CodingResearchTool(BaseTool):
    """
    Tool for researching coding patterns and best practices.
    
    Model routing:
    - Simple: meta-llama/Meta-Llama-3.1-8B-Instruct
    - Moderate: deepseek/deepseek-v3.1
    - Deep: meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8
    """
    
    def __init__(
        self,
        api_client: RouteLLMClient,
        db_client: MongoDBClient
    ):
        """Initialize Coding Research Tool."""
        super().__init__(api_client, db_client, Category.CODING_RESEARCH)
    
    def execute(
        self,
        question: str,
        complexity: str = "simple",
        save_to_db: bool = True,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Execute coding research query.
        
        Args:
            question: Research question about coding patterns, best practices, etc.
            complexity: Complexity level (simple, moderate, deep). Default: simple
            save_to_db: Whether to save response to MongoDB. Default: True
            parent_id: Optional parent document ID for follow-up questions
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Markdown response with coding research
        """
        # Map complexity to router complexity
        router_complexity = complexity if complexity in ["simple", "moderate", "deep"] else "simple"
        
        # Get model based on complexity
        model = get_model_for_tool("coding_research", complexity=router_complexity)
        
        # Estimate output length and get max tokens
        expected_length = estimate_output_length(question, complexity)
        max_tokens = get_max_tokens(expected_length)
        
        # Create system prompt for coding research
        system_prompt = """You are a coding research assistant specializing in best practices, patterns, and implementation guides.

Your responses should:
- Provide best coding patterns and practices
- Include implementation guides with code examples
- Highlight edge cases and potential pitfalls
- Show common mistakes and how to avoid them
- Use markdown formatting with proper code blocks
- Be practical and actionable

Focus on code quality, maintainability, and best practices."""
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        # Get complete response (handles truncation automatically)
        markdown_content = get_complete_response(
            api_client=self.api_client,
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        # Determine complexity score (1-10)
        complexity_map = {
            "simple": 4,
            "moderate": 6,
            "deep": 8
        }
        complexity_score = complexity_map.get(complexity, 5)
        
        # Save to MongoDB if requested
        if save_to_db:
            self.save_to_mongodb(
                question=question,
                markdown_content=markdown_content,
                model_used=model,
                complexity_score=complexity_score,
                parent_id=parent_id
            )
        
        return markdown_content

