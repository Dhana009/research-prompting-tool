"""
Integration tests for System-1 MCP Server.

Tests MCP tool exposure and integration with DocumentOrchestrator.
"""

import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from bson import ObjectId


class TestMCPServerSystem1:
    """Test System-1 MCP Server integration."""
    
    def test_mcp_exposes_save_research_document_tool(self):
        """Test that MCP server registers save_research_document tool."""
        from src.mcp_server_system1 import list_tools
        
        tools = list_tools()
        
        # Find save_research_document tool
        tool_names = [tool["name"] for tool in tools]
        assert "save_research_document" in tool_names, \
            f"save_research_document tool not found. Available tools: {tool_names}"
    
    def test_save_research_document_calls_orchestrator(self):
        """Test that save_research_document tool calls DocumentOrchestrator."""
        from src.mcp_server_system1 import call_tool
        
        # Mock DocumentOrchestrator
        with patch('src.mcp_server_system1.DocumentOrchestrator') as mock_orchestrator:
            mock_orchestrator.save_document.return_value = {
                "document_id": "TR-20251126-183613-ABC12",
                "conversation_id": "CV-20251126-183613-XYZ12",
                "parent_id": None,
                "content_type": "text",
                "mongo_db": "research_toolkit",
                "mongo_collection": "research_documents",
                "inserted_id": str(ObjectId())
            }
            
            # Mock MongoDB client
            mock_client = Mock()
            with patch('src.mcp_server_system1.get_mongo_client', return_value=mock_client):
                # Call MCP tool
                arguments = {
                    "question": "What is TDD?",
                    "markdown_content": "TDD is ...",
                    "parent_id": None
                }
                
                result = call_tool("save_research_document", arguments)
                
                # Assert orchestrator was called
                assert mock_orchestrator.save_document.called
                
                # Assert correct arguments passed
                call_args = mock_orchestrator.save_document.call_args
                assert call_args[1]["question"] == "What is TDD?"
                assert call_args[1]["markdown_content"] == "TDD is ..."
                assert call_args[1]["parent_id"] is None
    
    def test_save_research_document_returns_result_payload(self):
        """Test that save_research_document returns correct result payload."""
        from src.mcp_server_system1 import call_tool
        
        # Mock orchestrator return
        expected_result = {
            "document_id": "TR-20251126-183613-ABC12",
            "conversation_id": "CV-20251126-183613-XYZ12",
            "parent_id": None,
            "content_type": "text",
            "mongo_db": "research_toolkit",
            "mongo_collection": "research_documents",
            "inserted_id": "507f1f77bcf86cd799439011"
        }
        
        with patch('src.mcp_server_system1.DocumentOrchestrator') as mock_orchestrator:
            mock_orchestrator.save_document.return_value = expected_result
            
            mock_client = Mock()
            with patch('src.mcp_server_system1.get_mongo_client', return_value=mock_client):
                arguments = {
                    "question": "Test",
                    "markdown_content": "Test content"
                }
                
                result = call_tool("save_research_document", arguments)
                
                # Assert result contains expected fields
                assert "content" in result
                content = result["content"][0]
                assert content["type"] == "text"
                
                # Parse JSON from text content
                import json
                result_data = json.loads(content["text"])
                
                assert result_data["document_id"] == expected_result["document_id"]
                assert result_data["conversation_id"] == expected_result["conversation_id"]
                assert result_data["inserted_id"] == expected_result["inserted_id"]
    
    def test_mcp_exposes_get_document_tool(self):
        """Test that MCP server registers get_research_document tool."""
        from src.mcp_server_system1 import list_tools
        
        tools = list_tools()
        
        # Find get_research_document tool
        tool_names = [tool["name"] for tool in tools]
        assert "get_research_document" in tool_names, \
            f"get_research_document tool not found. Available tools: {tool_names}"
    
    def test_get_document_returns_document_from_mongo(self):
        """Test that get_research_document returns document from MongoDB."""
        from src.mcp_server_system1 import call_tool
        
        # Mock MongoDB document
        mock_doc = {
            "document_id": "TR-20251126-183613-ABC12",
            "conversation_id": "CV-20251126-183613-XYZ12",
            "parent_id": None,
            "content_type": "text",
            "question": "What is TDD?",
            "markdown_content": "TDD is ..."
        }
        
        # Mock MongoDB client
        mock_collection = Mock()
        mock_collection.find_one = Mock(return_value=mock_doc)
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        with patch('src.mcp_server_system1.get_mongo_client', return_value=mock_client):
            arguments = {
                "document_id": "TR-20251126-183613-ABC12"
            }
            
            result = call_tool("get_research_document", arguments)
            
            # Assert MongoDB find_one was called
            assert mock_collection.find_one.called
            
            # Assert result contains document
            assert "content" in result
            content = result["content"][0]
            assert content["type"] == "text"
            
            import json
            result_data = json.loads(content["text"])
            assert result_data["document_id"] == mock_doc["document_id"]
            assert result_data["question"] == mock_doc["question"]
    
    def test_list_documents_returns_all_docs_in_collection(self):
        """Test that list_documents returns all documents in collection."""
        from src.mcp_server_system1 import call_tool
        
        # Mock MongoDB documents
        mock_docs = [
            {
                "document_id": "TR-20251126-183613-ABC12",
                "conversation_id": "CV-20251126-183613-XYZ12",
                "question": "Question 1"
            },
            {
                "document_id": "TR-20251126-183700-DEF34",
                "conversation_id": "CV-20251126-183613-XYZ12",
                "question": "Question 2"
            }
        ]
        
        # Mock MongoDB client
        mock_collection = Mock()
        mock_collection.find = Mock(return_value=mock_docs)
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        with patch('src.mcp_server_system1.get_mongo_client', return_value=mock_client):
            arguments = {}
            
            result = call_tool("list_documents", arguments)
            
            # Assert MongoDB find was called
            assert mock_collection.find.called
            
            # Assert result contains documents
            assert "content" in result
            content = result["content"][0]
            assert content["type"] == "text"
            
            import json
            result_data = json.loads(content["text"])
            assert len(result_data) == 2
            assert result_data[0]["document_id"] == mock_docs[0]["document_id"]
    
    def test_save_document_raises_error_if_missing_field(self):
        """Test that save_research_document raises error if required field is missing."""
        from src.mcp_server_system1 import call_tool
        
        mock_client = Mock()
        with patch('src.mcp_server_system1.get_mongo_client', return_value=mock_client):
            # Missing markdown_content
            arguments = {
                "question": "What is TDD?"
                # markdown_content missing
            }
            
            # Expect error
            with pytest.raises(Exception) as exc_info:
                call_tool("save_research_document", arguments)
            
            # Check error message indicates missing field
            error_msg = str(exc_info.value).lower()
            assert "markdown_content" in error_msg or "required" in error_msg or "missing" in error_msg
    
    def test_server_initializes_with_mongo_config_from_mcp_json(self):
        """Test that server loads MongoDB config from environment variables."""
        from src.mcp_server_system1 import load_mongodb_config, get_mongo_client
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'MONGODB_CONNECTION_STRING': 'mongodb://test-uri',
            'MONGODB_DATABASE': 'test_db',
            'MONGODB_COLLECTION': 'test_collection'
        }):
            # Load config
            config = load_mongodb_config()
            
            # Assert config loaded correctly
            assert "default" in config
            assert config["default"]["uri"] == "mongodb://test-uri"
            assert config["default"]["database"] == "test_db"
            assert config["default"]["collection"] == "test_collection"

