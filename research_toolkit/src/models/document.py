"""
MongoDB document schema for research responses.

Defines the Pydantic model that matches the exact structure from requirements.
"""

from typing import Optional, List, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class Category(str, Enum):
    """Valid categories for research documents."""
    TOPIC_RESEARCH = "topic_research"
    CODING_RESEARCH = "coding_research"
    DEBUGGING = "debugging"
    ARCHITECTURE = "architecture"
    GENERAL = "general"


class ResearchDocument(BaseModel):
    """
    MongoDB document schema for storing AI research responses.
    
    Matches the exact structure from requirements/final_draft_requirements.md
    """
    
    # Required fields
    question: str = Field(..., description="Raw user question")
    markdown_content: str = Field(..., description="Exact markdown response from AI")
    category: Category = Field(..., description="Tool category")
    question_id: str = Field(..., description="Unique question identifier")
    timestamp_ist: str = Field(..., description="Timestamp in IST format")
    model_used: str = Field(..., description="Model name used for this response")
    complexity_score: int = Field(..., description="Complexity score 1-10")
    contains_code: bool = Field(..., description="Whether response contains code")
    estimated_segments: int = Field(..., description="Estimated number of segments")
    language_tags: List[str] = Field(default_factory=list, description="Programming languages detected")
    
    # Optional fields
    sub_category: Optional[str] = Field(None, description="Optional sub-category")
    
    # Future vectorization fields (empty by default)
    segments: List[Any] = Field(default_factory=list, description="Segments for vectorization")
    vectors: List[Any] = Field(default_factory=list, description="Vector embeddings")
    graph_nodes: List[Any] = Field(default_factory=list, description="Knowledge graph nodes")
    graph_edges: List[Any] = Field(default_factory=list, description="Knowledge graph edges")
    
    @field_validator('timestamp_ist')
    @classmethod
    def validate_timestamp_format(cls, v: str) -> str:
        """
        Validate timestamp format: YYYY-MM-DD HH:MM:SS IST (DAY_OF_WEEK)
        
        Example: "2025-11-26 10:54:33 IST (Wednesday)"
        """
        pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} IST \(([A-Za-z]+day)\)$'
        if not re.match(pattern, v):
            raise ValueError(
                f"Timestamp must be in format: YYYY-MM-DD HH:MM:SS IST (DAY_OF_WEEK). "
                f"Got: {v}"
            )
        return v
    
    @field_validator('complexity_score')
    @classmethod
    def validate_complexity_score(cls, v: int) -> int:
        """Validate complexity_score is between 1 and 10."""
        if not (1 <= v <= 10):
            raise ValueError(f"complexity_score must be between 1 and 10, got {v}")
        return v
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: Any) -> Category:
        """Ensure category is a valid Category enum value."""
        if isinstance(v, str):
            try:
                return Category(v)
            except ValueError:
                raise ValueError(
                    f"Invalid category: {v}. Must be one of: "
                    f"{[c.value for c in Category]}"
                )
        return v
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "question": "What is test-driven development?",
                "markdown_content": "# Answer\n\nTDD is...",
                "category": "topic_research",
                "sub_category": None,
                "question_id": "TR-20251126-105433IST-WED-QX18",
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
        }
    )

