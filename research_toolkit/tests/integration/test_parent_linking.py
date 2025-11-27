"""
Integration tests for parent linking functionality.

Tests that parent_id is correctly passed through and conversation_id is inherited.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from bson import ObjectId


class TestParentLinking:
    """Test parent linking in System-1 tools."""

    def test_parent_id_passthrough_calls_orchestrator(self):
        """Test that parent_id is passed through to DocumentOrchestrator."""
        from src.tools.topic_research import TopicResearchTool
        from src.utils.api_client import RouteLLMClient
        from src.storage.mongodb import MongoDBClient

        # Mock clients
        mock_api_client = Mock(spec=RouteLLMClient)
        mock_db_client = Mock(spec=MongoDBClient)
        mock_db_client._connected = True
        mock_db_client.client = Mock()
        mock_db_client.db = Mock()
        mock_db_client.db.name = "test_db"
        mock_db_client.collection = Mock()
        mock_db_client.collection.name = "test_collection"

        # Mock API response
        with patch('src.tools.topic_research.get_complete_response', return_value="Test response"):
            # Mock orchestrator
            with patch('src.tools.base_tool.DocumentOrchestrator.save_document') as mock_save:
                mock_save.return_value = {
                    "document_id": "TEST-123",
                    "conversation_id": "CV-123",
                    "parent_id": "PARENT-123",
                    "inserted_id": str(ObjectId())
                }

                tool = TopicResearchTool(mock_api_client, mock_db_client)
                
                # Call tool with parent_id
                result = tool.execute(
                    question="Explain red-green-refactor",
                    parent_id="PARENT-123",
                    save_to_db=True
                )

                # Assert orchestrator was called with parent_id
                assert mock_save.called
                call_kwargs = mock_save.call_args[1]  # Get keyword arguments
                assert call_kwargs["parent_id"] == "PARENT-123"

    def test_child_inherits_parent_conversation_id(self):
        """Test that child document inherits parent's conversation_id."""
        from src.tools.topic_research import TopicResearchTool
        from src.utils.api_client import RouteLLMClient
        from src.storage.mongodb import MongoDBClient

        # Fake parent document returned by Mongo
        fake_parent_doc = {
            "document_id": "PARENT-123",
            "conversation_id": "CONV-789",
            "question": "Parent question",
            "markdown_content": "Parent content"
        }

        # Mock clients
        mock_api_client = Mock(spec=RouteLLMClient)
        mock_db_client = Mock(spec=MongoDBClient)
        mock_db_client._connected = True
        mock_db_client.client = Mock()
        mock_db_client.db = Mock()
        mock_db_client.db.name = "test_db"
        mock_db_client.collection = Mock()
        mock_db_client.collection.name = "test_collection"

        # Mock API response
        with patch('src.tools.topic_research.get_complete_response', return_value="Child response"):
            # Mock parent loader to return fake parent
            with patch('src.utils.document_orchestrator.DocumentOrchestrator._load_parent', return_value=fake_parent_doc):
                # Mock save_document to capture what was assembled
                with patch('src.utils.document_orchestrator.MongoWriter.save') as mock_writer:
                    mock_writer.return_value = {
                        "document_id": "CHILD-456",
                        "conversation_id": "CONV-789",
                        "parent_id": "PARENT-123",
                        "inserted_id": str(ObjectId())
                    }

                    tool = TopicResearchTool(mock_api_client, mock_db_client)

                    # Call tool with parent_id
                    result = tool.execute(
                        question="child follow-up question",
                        parent_id="PARENT-123",
                        save_to_db=True
                    )

                    # Assert MongoWriter was called with correct document
                    assert mock_writer.called
                    call_kwargs = mock_writer.call_args[1]  # Get keyword arguments
                    saved_doc = call_kwargs["doc"]  # Document is passed as 'doc' keyword argument

                    # Verify child inherited parent's conversation_id
                    assert saved_doc["conversation_id"] == "CONV-789"
                    assert saved_doc["parent_id"] == "PARENT-123"
                    assert saved_doc["question"] == "child follow-up question"

