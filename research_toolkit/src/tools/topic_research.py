"""
Topic Research Tool.

Provides high-level topic understanding, definitions, fundamentals, and terminology.
"""

from typing import Optional
from src.tools.base_tool import BaseTool
from src.models.document import Category
from src.router.model_router import get_model_for_tool
from src.utils.token_manager import get_max_tokens, estimate_output_length
from src.utils.output_handler import get_complete_response
from src.storage.mongodb import MongoDBClient
from src.utils.api_client import RouteLLMClient


class TopicResearchTool(BaseTool):
    """
    Tool for researching topics and understanding concepts.
    
    Model routing:
    - Primary: gemini-2.5-flash
    - Backup: gpt-4o-mini
    - Large topics: gpt-5
    """
    
    def __init__(
        self,
        api_client: RouteLLMClient,
        db_client: MongoDBClient
    ):
        """Initialize Topic Research Tool."""
        super().__init__(api_client, db_client, Category.TOPIC_RESEARCH)
    
    def execute(
        self,
        question: str,
        complexity: str = "simple",
        use_backup: bool = False,
        save_to_db: bool = True,
        **kwargs
    ) -> str:
        """
        Execute topic research query.
        
        Args:
            question: Research question about a topic
            complexity: Complexity level (simple, large). Default: simple
            use_backup: Whether to use backup model. Default: False
            save_to_db: Whether to save response to MongoDB. Default: True
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Markdown response with topic research
        """
        # Determine model based on complexity
        if complexity == "large":
            model = get_model_for_tool("topic_research", complexity="large")
        elif use_backup:
            model = get_model_for_tool("topic_research", complexity="simple", use_backup=True)
        else:
            model = get_model_for_tool("topic_research", complexity="simple")
        
        # Estimate output length and get max tokens
        expected_length = estimate_output_length(question, complexity)
        max_tokens = get_max_tokens(expected_length)
        
        # Create system prompt for topic research
        system_prompt = """You are a research assistant specializing in providing clear, comprehensive explanations of topics, concepts, and terminology.

Your responses should:
- Provide clear definitions and fundamentals
- Explain key terminology
- Give high-level understanding
- Use markdown formatting
- Be well-structured and easy to read

Focus on understanding and explanation, not implementation details."""
        
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
        complexity_score = 7 if complexity == "large" else 3
        
        # Save to MongoDB if requested
        if save_to_db:
            self.save_to_mongodb(
                question=question,
                markdown_content=markdown_content,
                model_used=model,
                complexity_score=complexity_score
            )
        
        return markdown_content

