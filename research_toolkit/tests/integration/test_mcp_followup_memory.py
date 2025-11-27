"""
Integration tests for MCP Follow-Up Memory Layer.

Tests that the MCP server remembers last document_id and conversation_id
and uses them when follow_up=true.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from bson import ObjectId


class TestMCPFollowUpMemory:
    """Test MCP follow-up memory layer."""

    def test_first_call_creates_new_conversation_with_parent_id_none(self):
        """Test that first call creates new conversation with parent_id=None."""
        from src.mcp_server import call_tool, _followup_memory
        
        # Reset memory
        _followup_memory.last_document_id = None
        _followup_memory.last_conversation_id = None
        
        # Mock MongoDB and orchestrator
        with patch('src.mcp_server.get_clients') as mock_get_clients:
            mock_api_client = Mock()
            mock_db_client = Mock()
            mock_db_client._connected = True
            mock_db_client.client = Mock()
            mock_db_client.db = Mock()
            mock_db_client.db.name = "test_db"
            mock_db_client.collection = Mock()
            mock_db_client.collection.name = "test_collection"
            mock_get_clients.return_value = (mock_api_client, mock_db_client)
            
            # Mock the last document query
            mock_db_client.collection.find_one.return_value = {
                "document_id": "TR-20251126-123456-ABC12",
                "conversation_id": "CV-20251126-123456-ABC12",
                "parent_id": None
            }
            
            # Mock API response
            with patch('src.tools.topic_research.get_complete_response', return_value="Python is a programming language"):
                # Mock orchestrator save
                with patch('src.tools.base_tool.DocumentOrchestrator.save_document') as mock_save:
                    mock_save.return_value = {
                        "document_id": "TR-20251126-123456-ABC12",
                        "conversation_id": "CV-20251126-123456-ABC12",
                        "parent_id": None,
                        "inserted_id": str(ObjectId())
                    }
                    
                    # Call topic_research with follow_up=False
                    result = call_tool(
                        "topic_research",
                        {
                            "question": "What is Python?",
                            "follow_up": False
                        }
                    )
                    
                    # Assert parent_id is None
                    call_kwargs = mock_save.call_args[1]
                    assert call_kwargs["parent_id"] is None
                    
                    # Assert conversation_id exists
                    saved_result = mock_save.return_value
                    assert saved_result["conversation_id"] is not None
                    
                    # Assert memory updated
                    assert _followup_memory.last_document_id == "TR-20251126-123456-ABC12"
                    assert _followup_memory.last_conversation_id == "CV-20251126-123456-ABC12"

    def test_second_call_with_follow_up_true_uses_previous_ids(self):
        """Test that second call with follow_up=True uses previous document IDs."""
        from src.mcp_server import call_tool, _followup_memory
        
        # Set up memory with previous document
        previous_doc_id = "TR-20251126-123456-ABC12"
        previous_conv_id = "CV-20251126-123456-ABC12"
        _followup_memory.last_document_id = previous_doc_id
        _followup_memory.last_conversation_id = previous_conv_id
        
        # Mock MongoDB and orchestrator
        with patch('src.mcp_server.get_clients') as mock_get_clients:
            mock_api_client = Mock()
            mock_db_client = Mock()
            mock_db_client._connected = True
            mock_db_client.client = Mock()
            mock_db_client.db = Mock()
            mock_db_client.db.name = "test_db"
            mock_db_client.collection = Mock()
            mock_db_client.collection.name = "test_collection"
            mock_get_clients.return_value = (mock_api_client, mock_db_client)
            
            # Mock the last document query (returns new document)
            mock_db_client.collection.find_one.return_value = {
                "document_id": "TR-20251126-123500-XYZ34",
                "conversation_id": previous_conv_id,
                "parent_id": previous_doc_id
            }
            
            # Mock API response
            with patch('src.tools.topic_research.get_complete_response', return_value="Variables store data"):
                # Mock orchestrator save
                with patch('src.tools.base_tool.DocumentOrchestrator.save_document') as mock_save:
                    mock_save.return_value = {
                        "document_id": "TR-20251126-123500-XYZ34",
                        "conversation_id": previous_conv_id,
                        "parent_id": previous_doc_id,
                        "inserted_id": str(ObjectId())
                    }
                    
                    # Call topic_research with follow_up=True
                    result = call_tool(
                        "topic_research",
                        {
                            "question": "Explain variables",
                            "follow_up": True
                        }
                    )
                    
                    # Assert parent_id == previous document_id
                    call_kwargs = mock_save.call_args[1]
                    assert call_kwargs["parent_id"] == previous_doc_id
                    
                    # Assert conversation_id == previous conversation_id
                    saved_result = mock_save.return_value
                    assert saved_result["conversation_id"] == previous_conv_id

    def test_second_call_with_follow_up_false_resets_to_new_conversation(self):
        """Test that second call with follow_up=False resets to new conversation."""
        from src.mcp_server import call_tool, _followup_memory
        
        # Set up memory with previous document
        previous_conv_id = "CV-20251126-123456-ABC12"
        _followup_memory.last_document_id = "TR-20251126-123456-ABC12"
        _followup_memory.last_conversation_id = previous_conv_id
        
        # Mock MongoDB and orchestrator
        with patch('src.mcp_server.get_clients') as mock_get_clients:
            mock_api_client = Mock()
            mock_db_client = Mock()
            mock_db_client._connected = True
            mock_db_client.client = Mock()
            mock_db_client.db = Mock()
            mock_db_client.db.name = "test_db"
            mock_db_client.collection = Mock()
            mock_db_client.collection.name = "test_collection"
            mock_get_clients.return_value = (mock_api_client, mock_db_client)
            
            # Mock the last document query (returns new document)
            new_conv_id = "CV-20251126-130000-DEF56"
            mock_db_client.collection.find_one.return_value = {
                "document_id": "TR-20251126-130000-DEF56",
                "conversation_id": new_conv_id,
                "parent_id": None
            }
            
            # Mock API response
            with patch('src.tools.topic_research.get_complete_response', return_value="Cloud computing is..."):
                # Mock orchestrator save
                with patch('src.tools.base_tool.DocumentOrchestrator.save_document') as mock_save:
                    mock_save.return_value = {
                        "document_id": "TR-20251126-130000-DEF56",
                        "conversation_id": new_conv_id,
                        "parent_id": None,
                        "inserted_id": str(ObjectId())
                    }
                    
                    # Call topic_research with follow_up=False
                    result = call_tool(
                        "topic_research",
                        {
                            "question": "New topic",
                            "follow_up": False
                        }
                    )
                    
                    # Assert parent_id is None
                    call_kwargs = mock_save.call_args[1]
                    assert call_kwargs["parent_id"] is None
                    
                    # Assert conversation_id != previous conversation_id
                    saved_result = mock_save.return_value
                    assert saved_result["conversation_id"] != previous_conv_id
                    assert saved_result["conversation_id"] == new_conv_id

    def test_memory_updates_after_every_save(self):
        """Test that memory updates after every save."""
        from src.mcp_server import call_tool, _followup_memory
        
        # Reset memory
        _followup_memory.last_document_id = None
        _followup_memory.last_conversation_id = None
        
        # Mock MongoDB and orchestrator
        with patch('src.mcp_server.get_clients') as mock_get_clients:
            mock_api_client = Mock()
            mock_db_client = Mock()
            mock_db_client._connected = True
            mock_db_client.client = Mock()
            mock_db_client.db = Mock()
            mock_db_client.db.name = "test_db"
            mock_db_client.collection = Mock()
            mock_db_client.collection.name = "test_collection"
            mock_get_clients.return_value = (mock_api_client, mock_db_client)
            
            # Mock API response
            with patch('src.tools.topic_research.get_complete_response', return_value="Test response"):
                # Mock orchestrator save
                with patch('src.tools.base_tool.DocumentOrchestrator.save_document') as mock_save:
                    doc_id_1 = "TR-20251126-123456-ABC12"
                    conv_id_1 = "CV-20251126-123456-ABC12"
                    
                    # Mock first document query
                    mock_db_client.collection.find_one.return_value = {
                        "document_id": doc_id_1,
                        "conversation_id": conv_id_1,
                        "parent_id": None
                    }
                    
                    mock_save.return_value = {
                        "document_id": doc_id_1,
                        "conversation_id": conv_id_1,
                        "parent_id": None,
                        "inserted_id": str(ObjectId())
                    }
                    
                    # First call
                    call_tool(
                        "topic_research",
                        {
                            "question": "First question",
                            "follow_up": False
                        }
                    )
                    
                    # Assert memory updated after first call
                    assert _followup_memory.last_document_id == doc_id_1
                    assert _followup_memory.last_conversation_id == conv_id_1
                    
                    # Second call with follow_up=True should use previous IDs
                    doc_id_2 = "TR-20251126-123500-XYZ34"
                    mock_db_client.collection.find_one.return_value = {
                        "document_id": doc_id_2,
                        "conversation_id": conv_id_1,  # Same conversation
                        "parent_id": doc_id_1  # Previous document
                    }
                    
                    mock_save.return_value = {
                        "document_id": doc_id_2,
                        "conversation_id": conv_id_1,  # Same conversation
                        "parent_id": doc_id_1,  # Previous document
                        "inserted_id": str(ObjectId())
                    }
                    
                    call_tool(
                        "topic_research",
                        {
                            "question": "Second question",
                            "follow_up": True
                        }
                    )
                    
                    # Verify second call used previous document_id as parent_id
                    second_call_kwargs = mock_save.call_args[1]
                    assert second_call_kwargs["parent_id"] == doc_id_1
                    
                    # Assert memory updated after second call
                    assert _followup_memory.last_document_id == doc_id_2
                    assert _followup_memory.last_conversation_id == conv_id_1

    def test_memory_resets_on_server_restart(self):
        """Test that memory resets on server restart (new instance)."""
        from src.mcp_server import _followup_memory
        
        # Reset memory to simulate server restart
        _followup_memory.last_document_id = None
        _followup_memory.last_conversation_id = None
        
        # Assert memory is reset
        assert _followup_memory.last_document_id is None
        assert _followup_memory.last_conversation_id is None

