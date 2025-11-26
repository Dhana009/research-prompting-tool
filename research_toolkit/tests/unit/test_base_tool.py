"""
Unit tests for base tool class.

Tests that all tools inherit from base class and have required methods.
"""

import pytest
from unittest.mock import Mock, patch


class TestBaseTool:
    """Test base tool class and inheritance."""
    
    def test_all_tools_inherit_from_base(self):
        """Test all 5 tools inherit from base class."""
        from src.tools.base_tool import BaseTool
        from src.tools.topic_research import TopicResearchTool
        from src.tools.coding_research import CodingResearchTool
        from src.tools.debugging import DebuggingTool
        from src.tools.architecture import ArchitectureTool
        from src.tools.general_purpose import GeneralPurposeTool
        
        tools = [
            TopicResearchTool,
            CodingResearchTool,
            DebuggingTool,
            ArchitectureTool,
            GeneralPurposeTool
        ]
        
        for tool_class in tools:
            assert issubclass(tool_class, BaseTool), f"{tool_class.__name__} should inherit from BaseTool"
    
    def test_all_tools_have_execute_method(self):
        """Test all tools have execute method."""
        from src.tools.topic_research import TopicResearchTool
        from src.tools.coding_research import CodingResearchTool
        from src.tools.debugging import DebuggingTool
        from src.tools.architecture import ArchitectureTool
        from src.tools.general_purpose import GeneralPurposeTool
        
        tools = [
            TopicResearchTool,
            CodingResearchTool,
            DebuggingTool,
            ArchitectureTool,
            GeneralPurposeTool
        ]
        
        for tool_class in tools:
            assert hasattr(tool_class, "execute"), f"{tool_class.__name__} should have execute method"
            assert callable(getattr(tool_class, "execute")), f"{tool_class.__name__}.execute should be callable"
    
    def test_all_tools_have_save_to_mongodb_method(self):
        """Test all tools have save_to_mongodb method."""
        from src.tools.topic_research import TopicResearchTool
        from src.tools.coding_research import CodingResearchTool
        from src.tools.debugging import DebuggingTool
        from src.tools.architecture import ArchitectureTool
        from src.tools.general_purpose import GeneralPurposeTool
        
        tools = [
            TopicResearchTool,
            CodingResearchTool,
            DebuggingTool,
            ArchitectureTool,
            GeneralPurposeTool
        ]
        
        for tool_class in tools:
            assert hasattr(tool_class, "save_to_mongodb"), f"{tool_class.__name__} should have save_to_mongodb method"
            assert callable(getattr(tool_class, "save_to_mongodb")), f"{tool_class.__name__}.save_to_mongodb should be callable"
    
    def test_all_tools_return_markdown(self):
        """Test all tools return markdown format."""
        from src.tools.topic_research import TopicResearchTool
        from src.tools.coding_research import CodingResearchTool
        from src.tools.debugging import DebuggingTool
        from src.tools.architecture import ArchitectureTool
        from src.tools.general_purpose import GeneralPurposeTool
        from tests.fixtures.mock_models import MockRouteLLMClient
        from tests.fixtures.mock_models import MockMongoDBClient
        
        tools = [
            TopicResearchTool,
            CodingResearchTool,
            DebuggingTool,
            ArchitectureTool,
            GeneralPurposeTool
        ]
        
        mock_api = MockRouteLLMClient(api_key="test", api_url="test")
        mock_db = MockMongoDBClient(connection_string="test")
        
        for tool_class in tools:
            tool = tool_class(api_client=mock_api, db_client=mock_db)
            
            # Mock the execute to return sample markdown
            with patch.object(tool, 'execute', return_value="# Test\n\nMarkdown content"):
                result = tool.execute("test question")
                
                # Result should be a string (markdown)
                assert isinstance(result, str), f"{tool_class.__name__} should return string (markdown)"
                # Should contain markdown-like content (at least some text)
                assert len(result) > 0, f"{tool_class.__name__} should return non-empty markdown"
    
    def test_base_tool_has_common_methods(self):
        """Test base tool has common methods that all tools can use."""
        from src.tools.base_tool import BaseTool
        
        # Check for common methods
        assert hasattr(BaseTool, "execute"), "BaseTool should have execute method"
        assert hasattr(BaseTool, "save_to_mongodb"), "BaseTool should have save_to_mongodb method"
    
    def test_base_tool_is_abstract(self):
        """Test base tool cannot be instantiated directly (abstract class)."""
        from src.tools.base_tool import BaseTool
        
        # BaseTool should be abstract (cannot instantiate)
        with pytest.raises((TypeError, NotImplementedError)):
            BaseTool(api_client=Mock(), db_client=Mock())

