"""
Debugging Tool.

Analyzes failing code and provides root cause analysis with tier-based escalation.
Does NOT generate code - only deep reasoning.
"""

from typing import Optional, List, Dict, Any
from src.tools.base_tool import BaseTool
from src.models.document import Category
from src.router.model_router import get_model_for_tool
from src.utils.token_manager import get_max_tokens
from src.utils.output_handler import get_complete_response
from src.storage.mongodb import MongoDBClient
from src.utils.api_client import RouteLLMClient


class DebuggingTool(BaseTool):
    """
    Tool for debugging analysis with tier-based escalation.
    
    Model routing:
    - Tier-1: deepseek-ai/DeepSeek-V3.1-Terminus
    - Tier-2: deepseek/deepseek-v3.1
    - Tier-3: gpt-5 or claude-sonnet-4-20250514
    
    Escalation is user-driven - system waits for user trigger.
    """
    
    # Escalation trigger phrases (case-insensitive)
    ESCALATION_TRIGGERS = [
        "not working",
        "didn't work",
        "failed",
        "escalate",
        "tier 2",
        "tier2",
        "tier 3",
        "tier3"
    ]
    
    def __init__(
        self,
        api_client: RouteLLMClient,
        db_client: MongoDBClient
    ):
        """Initialize Debugging Tool."""
        super().__init__(api_client, db_client, Category.DEBUGGING)
        self._tier_history: List[Dict[str, Any]] = []
        self._original_question: Optional[str] = None
    
    def _check_escalation_trigger(self, user_feedback: str) -> bool:
        """
        Check if user feedback contains escalation trigger.
        
        Args:
            user_feedback: User's feedback text
            
        Returns:
            True if escalation trigger detected, False otherwise
        """
        feedback_lower = user_feedback.lower()
        return any(trigger in feedback_lower for trigger in self.ESCALATION_TRIGGERS)
    
    def _get_next_tier(self, current_tier: int) -> int:
        """
        Get next tier level.
        
        Args:
            current_tier: Current tier (1, 2, or 3)
            
        Returns:
            Next tier level, or current tier if already at max
        """
        if current_tier < 3:
            return current_tier + 1
        return current_tier
    
    def _build_escalation_context(
        self,
        original_question: str,
        tier_history: List[Dict[str, Any]],
        user_feedback: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build message context for escalation with full history.
        
        Args:
            original_question: Original debugging question
            tier_history: List of previous tier responses
            user_feedback: Optional user feedback
            
        Returns:
            List of messages for API call
        """
        messages = [
            {
                "role": "system",
                "content": """You are a debugging expert specializing in root cause analysis.

Your responses should:
- Analyze failing code and identify root causes
- Provide deep reasoning about why code fails
- Explain the underlying issues
- Do NOT generate code - only analyze and explain
- Use markdown formatting
- Be thorough and detailed

Focus on understanding the problem, not fixing it."""
            },
            {
                "role": "user",
                "content": original_question
            }
        ]
        
        # Add all previous tier responses
        for tier_response in tier_history:
            messages.append({
                "role": "assistant",
                "content": tier_response["response"]
            })
            
            # Add user feedback if provided for that tier
            if tier_response.get("user_feedback"):
                messages.append({
                    "role": "user",
                    "content": tier_response["user_feedback"]
                })
        
        # Add current user feedback if provided
        if user_feedback:
            messages.append({
                "role": "user",
                "content": user_feedback
            })
        
        return messages
    
    def execute(
        self,
        question: str,
        tier: int = 1,
        user_feedback: Optional[str] = None,
        save_to_db: bool = True,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Execute debugging analysis at specified tier.
        
        Args:
            question: Debugging question (failing code + explanation)
            tier: Tier level (1, 2, or 3). Default: 1
            user_feedback: Optional user feedback for escalation. Default: None
            save_to_db: Whether to save response to MongoDB. Default: True
            parent_id: Optional parent document ID for follow-up questions
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Markdown response with debugging analysis
        """
        # Validate tier
        if tier not in [1, 2, 3]:
            raise ValueError(f"Invalid tier: {tier}. Must be 1, 2, or 3.")
        
        # Get model for tier
        model = get_model_for_tool("debugging", tier=tier)
        
        # Debugging typically needs large responses
        max_tokens = get_max_tokens("large")
        
        # Build context with full history
        messages = self._build_escalation_context(
            original_question=question,
            tier_history=self._tier_history,
            user_feedback=user_feedback
        )
        
        # Get complete response (handles truncation automatically)
        markdown_content = get_complete_response(
            api_client=self.api_client,
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        # Store original question on first tier
        if tier == 1:
            self._original_question = question
        
        # Store tier response in history
        tier_response = {
            "tier": tier,
            "model": model,
            "response": markdown_content,
            "user_feedback": user_feedback,
            "original_question": self._original_question or question
        }
        self._tier_history.append(tier_response)
        
        # Determine complexity score (1-10)
        # Higher tier = higher complexity
        complexity_score = 5 + tier  # 6, 7, or 8
        
        # Save to MongoDB if requested
        # Each tier is stored separately
        if save_to_db:
            # Create a question that includes tier info for uniqueness
            tier_question = f"[Tier {tier}] {question}"
            if user_feedback:
                tier_question += f"\n\nUser Feedback: {user_feedback}"
            
            self.save_to_mongodb(
                question=tier_question,
                markdown_content=markdown_content,
                model_used=model,
                complexity_score=complexity_score,
                parent_id=parent_id
            )
        
        return markdown_content
    
    def escalate(
        self,
        user_feedback: str,
        save_to_db: bool = True
    ) -> str:
        """
        Escalate to next tier based on user feedback.
        
        This method should be called when user indicates escalation is needed.
        
        Args:
            user_feedback: User's feedback indicating escalation needed
            save_to_db: Whether to save response to MongoDB. Default: True
            
        Returns:
            Markdown response from escalated tier
        """
        # Determine current tier and next tier
        if not self._tier_history:
            raise ValueError("No previous tier responses. Call execute() first.")
        
        current_tier = self._tier_history[-1]["tier"]
        next_tier = self._get_next_tier(current_tier)
        
        if next_tier == current_tier:
            raise ValueError(f"Already at maximum tier ({current_tier}). Cannot escalate further.")
        
        # Get original question
        original_question = self._original_question
        if not original_question and self._tier_history:
            original_question = self._tier_history[0].get("original_question", "")
        if not original_question:
            raise ValueError("Original question not found. Cannot escalate without original question.")
        
        # Execute at next tier
        return self.execute(
            question=original_question,
            tier=next_tier,
            user_feedback=user_feedback,
            save_to_db=save_to_db
        )
    
    def reset(self):
        """Reset tier history (for new debugging session)."""
        self._tier_history = []
        self._original_question = None

