"""
Unit tests for model router.

Tests model selection logic for all 5 tools based on requirements.
"""

import pytest


class TestModelRouter:
    """Test model routing for all tools."""
    
    def test_topic_research_primary(self):
        """Test Topic Research routes to gemini-2.5-flash (primary)."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("topic_research", complexity="simple")
        
        assert model == "gemini-2.5-flash", "Topic Research should use gemini-2.5-flash as primary"
    
    def test_topic_research_large_conceptual(self):
        """Test Topic Research upgrades to gpt-5 for large conceptual topics."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("topic_research", complexity="large")
        
        assert model == "gpt-5", "Large conceptual topics should use gpt-5"
    
    def test_topic_research_backup(self):
        """Test Topic Research falls back to gpt-4o-mini if primary fails."""
        from src.router.model_router import get_model_for_tool
        
        # Simulate primary failure, get backup
        model = get_model_for_tool("topic_research", complexity="simple", use_backup=True)
        
        assert model == "gpt-4o-mini", "Backup for Topic Research should be gpt-4o-mini"
    
    def test_coding_research_simple(self):
        """Test Coding Research simple uses meta-llama/Meta-Llama-3.1-8B-Instruct."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("coding_research", complexity="simple")
        
        assert model == "meta-llama/Meta-Llama-3.1-8B-Instruct", "Simple coding should use Llama 3.1 8B"
    
    def test_coding_research_moderate(self):
        """Test Coding Research moderate uses deepseek/deepseek-v3.1."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("coding_research", complexity="moderate")
        
        assert model == "deepseek/deepseek-v3.1", "Moderate coding should use DeepSeek V3.1"
    
    def test_coding_research_deep(self):
        """Test Coding Research deep uses meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("coding_research", complexity="deep")
        
        assert model == "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "Deep coding should use Llama 4 Maverick"
    
    def test_debugging_tier1(self):
        """Test Debugging Tool routes to Tier-1 (deepseek-ai/DeepSeek-V3.1-Terminus)."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("debugging", tier=1)
        
        assert model == "deepseek-ai/DeepSeek-V3.1-Terminus", "Debugging Tier-1 should use DeepSeek Terminus"
    
    def test_debugging_tier2(self):
        """Test Debugging Tool Tier-2 uses deepseek/deepseek-v3.1."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("debugging", tier=2)
        
        assert model == "deepseek/deepseek-v3.1", "Debugging Tier-2 should use DeepSeek V3.1"
    
    def test_debugging_tier3(self):
        """Test Debugging Tool Tier-3 uses gpt-5 or claude-sonnet-4-20250514."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("debugging", tier=3)
        
        assert model in ["gpt-5", "claude-sonnet-4-20250514"], "Debugging Tier-3 should use gpt-5 or Claude Sonnet"
    
    def test_architecture_primary(self):
        """Test Architecture routes to claude-sonnet-4-20250514 (primary)."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("architecture", complexity="simple")
        
        assert model == "claude-sonnet-4-20250514", "Architecture should use Claude Sonnet as primary"
    
    def test_architecture_backup(self):
        """Test Architecture falls back to gpt-5 if primary fails."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("architecture", complexity="simple", use_backup=True)
        
        assert model == "gpt-5", "Backup for Architecture should be gpt-5"
    
    def test_general_purpose_default(self):
        """Test General Purpose routes to gpt-5-nano (default)."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("general", complexity="simple")
        
        assert model == "gpt-5-nano", "General Purpose should use gpt-5-nano as default"
    
    def test_general_purpose_auto_upgrade(self):
        """Test General Purpose auto-upgrades to gpt-4o-mini or gemini-2.5-flash on complexity."""
        from src.router.model_router import get_model_for_tool
        
        model = get_model_for_tool("general", complexity="medium")
        
        assert model in ["gpt-4o-mini", "gemini-2.5-flash"], "General Purpose should upgrade on complexity"
    
    def test_invalid_tool(self):
        """Test invalid tool raises error."""
        from src.router.model_router import get_model_for_tool
        
        with pytest.raises(ValueError):
            get_model_for_tool("invalid_tool", complexity="simple")
    
    def test_verified_models_only(self):
        """Test router only uses verified models from requirements."""
        from src.router.model_router import get_model_for_tool
        
        verified_models = [
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
        
        # Test all tools return verified models
        tools = ["topic_research", "coding_research", "debugging", "architecture", "general"]
        
        for tool in tools:
            if tool == "debugging":
                for tier in [1, 2, 3]:
                    model = get_model_for_tool(tool, tier=tier)
                    assert model in verified_models, f"{tool} tier {tier} returned unverified model {model}"
            elif tool == "coding_research":
                for complexity in ["simple", "moderate", "deep"]:
                    model = get_model_for_tool(tool, complexity=complexity)
                    assert model in verified_models, f"{tool} {complexity} returned unverified model {model}"
            else:
                model = get_model_for_tool(tool, complexity="simple")
                assert model in verified_models, f"{tool} returned unverified model {model}"

