"""
Integration test for root document conversation_id generation.

Tests that root documents (no parent) get a brand-new conversation_id.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from bson import ObjectId


class TestRootConversationId:
    """Test that root documents get new conversation_id."""

    def test_root_document_gets_new_conversation_id(self):
        """Test that root document (no parent) gets a new conversation_id."""
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
            # Mock MongoWriter to capture the final document
            with patch('src.utils.document_orchestrator.MongoWriter.save') as mock_writer:
                mock_writer.return_value = {
                    "document_id": "TEST-123",
                    "conversation_id": "CV-20251126-123456-ABC12",
                    "parent_id": None,
                    "inserted_id": str(ObjectId())
                }

                tool = TopicResearchTool(mock_api_client, mock_db_client)

                # Call tool with parent_id=None (root document)
                result = tool.execute(
                    question="root question",
                    parent_id=None,
                    save_to_db=True
                )

                # Assert MongoWriter was called
                assert mock_writer.called
                call_kwargs = mock_writer.call_args[1]  # Get keyword arguments
                saved_doc = call_kwargs["doc"]

                # Verify root document has a conversation_id
                assert "conversation_id" in saved_doc
                assert saved_doc["conversation_id"] is not None
                assert saved_doc["conversation_id"] != ""
                
                # Verify conversation_id format (CV-YYYYMMDD-HHMMSS-SHORTID)
                assert saved_doc["conversation_id"].startswith("CV-")
                
                # Verify parent_id is None for root document
                assert saved_doc["parent_id"] is None

