"""
General Purpose Tool.

For queries that don't fall under any specific category.
"""

from typing import Optional
from src.tools.base_tool import BaseTool
from src.models.document import Category
from src.router.model_router import get_model_for_tool
from src.utils.token_manager import get_max_tokens, estimate_output_length
from src.utils.output_handler import get_complete_response
from src.storage.mongodb import MongoDBClient
from src.utils.api_client import RouteLLMClient


class GeneralPurposeTool(BaseTool):
    """
    General purpose tool for miscellaneous queries.
    
    Model routing:
    - Default: gpt-5-nano
    - Auto-upgrade: gpt-4o-mini or gemini-2.5-flash (on complexity)
    """
    
    def __init__(
        self,
        api_client: RouteLLMClient,
        db_client: MongoDBClient
    ):
        """Initialize General Purpose Tool."""
        super().__init__(api_client, db_client, Category.GENERAL)
    
    def execute(
        self,
        question: str,
        complexity: str = "simple",
        save_to_db: bool = True,
        **kwargs
    ) -> str:
        """
        Execute general purpose query.
        
        Args:
            question: General question that doesn't fit other categories
            complexity: Complexity level (simple, medium). Default: simple
            save_to_db: Whether to save response to MongoDB. Default: True
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Markdown response
        """
        # Get model based on complexity
        # If medium complexity, auto-upgrade to better model
        router_complexity = complexity if complexity == "medium" else "simple"
        model = get_model_for_tool("general", complexity=router_complexity)
        
        # Estimate output length and get max tokens
        expected_length = estimate_output_length(question, complexity)
        max_tokens = get_max_tokens(expected_length)
        
        # Create system prompt for general purpose
        system_prompt = """You are a helpful AI assistant that provides clear, accurate, and well-formatted responses.

Your responses should:
- Be clear and concise
- Use markdown formatting when appropriate
- Provide accurate information
- Be well-structured and easy to read

Adapt your response style to the type of question asked."""
        
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
        complexity_score = 5 if complexity == "medium" else 2
        
        # Save to MongoDB if requested
        if save_to_db:
            self.save_to_mongodb(
                question=question,
                markdown_content=markdown_content,
                model_used=model,
                complexity_score=complexity_score
            )
        
        return markdown_content

