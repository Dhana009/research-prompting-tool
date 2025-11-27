"""
Architecture & Design Tool.

Helps design flows, frameworks, and system layouts. Identifies critical hotspots.
"""

from typing import Optional
from src.tools.base_tool import BaseTool
from src.models.document import Category
from src.router.model_router import get_model_for_tool
from src.utils.token_manager import get_max_tokens, estimate_output_length
from src.utils.output_handler import get_complete_response
from src.storage.mongodb import MongoDBClient
from src.utils.api_client import RouteLLMClient


class ArchitectureTool(BaseTool):
    """
    Tool for architecture and system design.
    
    Model routing:
    - Primary: claude-sonnet-4-20250514
    - Backup: gpt-5
    """
    
    def __init__(
        self,
        api_client: RouteLLMClient,
        db_client: MongoDBClient
    ):
        """Initialize Architecture Tool."""
        super().__init__(api_client, db_client, Category.ARCHITECTURE)
    
    def execute(
        self,
        question: str,
        use_backup: bool = False,
        save_to_db: bool = True,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Execute architecture design query.
        
        Args:
            question: Question about system design, architecture, flows, etc.
            use_backup: Whether to use backup model. Default: False
            save_to_db: Whether to save response to MongoDB. Default: True
            parent_id: Optional parent document ID for follow-up questions
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Markdown response with architecture design
        """
        # Get model (primary or backup)
        model = get_model_for_tool("architecture", complexity="simple", use_backup=use_backup)
        
        # Estimate output length and get max tokens
        # Architecture questions typically need medium to large responses
        expected_length = estimate_output_length(question, "moderate")
        max_tokens = get_max_tokens(expected_length)
        
        # Create system prompt for architecture
        system_prompt = """You are an architecture and design expert specializing in system design, flows, and frameworks.

Your responses should:
- Help design system flows and frameworks
- Identify critical hotspots and bottlenecks
- Provide clear system layouts and diagrams (in text/ASCII)
- Explain architectural decisions and trade-offs
- Consider scalability, maintainability, and performance
- Use markdown formatting
- Be structured and comprehensive

Focus on high-level design, patterns, and architectural principles."""
        
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
        
        # Architecture questions are typically complex
        complexity_score = 7
        
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

