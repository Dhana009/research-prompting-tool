"""
Model router for selecting appropriate AI models based on tool and complexity.

Routes models according to the strategy defined in requirements/final_draft_requirements.md
"""

from typing import Optional, Literal
import random


# Verified models from requirements
VERIFIED_MODELS = [
    "gpt-5-nano",
    "gpt-4.1-nano",
    "gpt-4o-mini",
    "gemini-2.5-flash",
    "gpt-5",
    "claude-sonnet-4-20250514",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "deepseek/deepseek-v3.1",
    "deepseek-ai/DeepSeek-V3.1-Terminus",
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
]


def get_model_for_tool(
    tool: str,
    complexity: Optional[Literal["simple", "moderate", "large", "medium", "deep"]] = None,
    tier: Optional[int] = None,
    use_backup: bool = False
) -> str:
    """
    Get the appropriate model for a given tool based on complexity or tier.
    
    Args:
        tool: Tool name (topic_research, coding_research, debugging, architecture, general)
        complexity: Complexity level (simple, moderate, large, medium, deep)
        tier: Tier level for debugging tool (1, 2, 3)
        use_backup: Whether to use backup model instead of primary
        
    Returns:
        Model name string
        
    Raises:
        ValueError: If tool is invalid or parameters are incompatible
    """
    tool = tool.lower()
    
    # Topic Research Tool
    if tool == "topic_research":
        if use_backup:
            return "gpt-4o-mini"
        if complexity == "large":
            return "gpt-5"
        return "gemini-2.5-flash"  # Primary
    
    # Coding Research Tool
    if tool == "coding_research":
        if complexity == "simple":
            return "meta-llama/Meta-Llama-3.1-8B-Instruct"
        elif complexity == "moderate":
            return "deepseek/deepseek-v3.1"
        elif complexity == "deep":
            return "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
        else:
            # Default to simple if complexity not specified
            return "meta-llama/Meta-Llama-3.1-8B-Instruct"
    
    # Debugging Tool (tier-based)
    if tool == "debugging":
        if tier == 1:
            return "deepseek-ai/DeepSeek-V3.1-Terminus"
        elif tier == 2:
            return "deepseek/deepseek-v3.1"
        elif tier == 3:
            # Tier-3 can use either gpt-5 or claude-sonnet-4-20250514
            # Default to gpt-5, but could be randomized
            return "gpt-5"
        else:
            # Default to Tier-1 if tier not specified
            return "deepseek-ai/DeepSeek-V3.1-Terminus"
    
    # Architecture & Design Tool
    if tool == "architecture":
        if use_backup:
            return "gpt-5"
        return "claude-sonnet-4-20250514"  # Primary
    
    # General Purpose Tool
    if tool == "general":
        if complexity == "medium":
            # Auto-upgrade to gpt-4o-mini or gemini-2.5-flash
            # Default to gemini-2.5-flash for consistency with topic research
            return "gemini-2.5-flash"
        return "gpt-5-nano"  # Default
    
    # Invalid tool
    raise ValueError(
        f"Invalid tool: {tool}. Must be one of: "
        "topic_research, coding_research, debugging, architecture, general"
    )

