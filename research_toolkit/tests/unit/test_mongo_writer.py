"""
Unit tests for MongoDB persistence layer.

Tests that documents are correctly saved to MongoDB with validation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from bson import ObjectId


class TestMongoWriter:
    """Test MongoDB writer for System-1 persistence."""
    
    def test_inserts_document_into_collection(self):
        """Test that document is inserted into MongoDB collection."""
        from src.utils.mongo_writer import MongoWriter
        
        # Create mock MongoDB client
        mock_collection = Mock()
        mock_collection.insert_one = Mock()
        mock_collection.find_one = Mock(return_value=None)  # No duplicate
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        # Test document
        doc = {
            "conversation_id": "CV-20251126-183613-ABC12",
            "document_id": "TR-20251126-183613-XYZ12",
            "parent_id": None,
            "content_type": "text",
            "question": "Test question",
            "markdown_content": "Test content"
        }
        
        # Call save
        MongoWriter.save(
            doc=doc,
            mongo_client=mock_client,
            database_name="research_toolkit",
            collection_name="research_documents"
        )
        
        # Assert insert_one was called exactly once
        assert mock_collection.insert_one.call_count == 1
        
        # Assert called with the document
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args == doc
    
    def test_returns_inserted_document_id(self):
        """Test that save returns the inserted document ID."""
        from src.utils.mongo_writer import MongoWriter
        
        # Create mock with ObjectId
        mock_result = Mock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439011")
        
        mock_collection = Mock()
        mock_collection.insert_one = Mock(return_value=mock_result)
        mock_collection.find_one = Mock(return_value=None)  # No duplicate
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        doc = {
            "conversation_id": "CV-20251126-183613-ABC12",
            "document_id": "TR-20251126-183613-XYZ12",
            "parent_id": None,
            "content_type": "text",
            "question": "Test",
            "markdown_content": "Test"
        }
        
        result = MongoWriter.save(
            doc=doc,
            mongo_client=mock_client,
            database_name="research_toolkit",
            collection_name="research_documents"
        )
        
        # Assert inserted_id is returned
        assert "inserted_id" in result
        assert result["inserted_id"] == str(mock_result.inserted_id)
    
    def test_validates_collection_exists(self):
        """Test that ValueError is raised if collection does not exist."""
        from src.utils.mongo_writer import MongoWriter
        
        # Mock collection that doesn't exist
        mock_db = Mock()
        mock_db.list_collection_names = Mock(return_value=["other_collection"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        doc = {
            "conversation_id": "CV-20251126-183613-ABC12",
            "document_id": "TR-20251126-183613-XYZ12",
            "parent_id": None,
            "content_type": "text",
            "question": "Test",
            "markdown_content": "Test"
        }
        
        # Expect ValueError
        with pytest.raises(ValueError, match="collection not found"):
            MongoWriter.save(
                doc=doc,
                mongo_client=mock_client,
                database_name="research_toolkit",
                collection_name="research_documents"
            )
    
    def test_validates_db_exists(self):
        """Test that ValueError is raised if database does not exist."""
        from src.utils.mongo_writer import MongoWriter
        
        # Mock client with missing database
        mock_client = Mock()
        mock_client.list_database_names = Mock(return_value=["other_database"])
        
        doc = {
            "conversation_id": "CV-20251126-183613-ABC12",
            "document_id": "TR-20251126-183613-XYZ12",
            "parent_id": None,
            "content_type": "text",
            "question": "Test",
            "markdown_content": "Test"
        }
        
        # Expect ValueError
        with pytest.raises(ValueError, match="DB not found"):
            MongoWriter.save(
                doc=doc,
                mongo_client=mock_client,
                database_name="research_toolkit",
                collection_name="research_documents"
            )
    
    def test_prevents_duplicate_document_id(self):
        """Test that ValueError is raised if document_id already exists."""
        from src.utils.mongo_writer import MongoWriter
        
        # Mock collection with existing document
        existing_doc = {
            "document_id": "TR-20251126-183613-XYZ12",
            "conversation_id": "CV-20251126-183613-ABC12"
        }
        
        mock_collection = Mock()
        mock_collection.find_one = Mock(return_value=existing_doc)  # Duplicate exists
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        doc = {
            "conversation_id": "CV-20251126-183613-ABC12",
            "document_id": "TR-20251126-183613-XYZ12",  # Same as existing
            "parent_id": None,
            "content_type": "text",
            "question": "Test",
            "markdown_content": "Test"
        }
        
        # Expect ValueError for duplicate
        with pytest.raises(ValueError, match="duplicate document_id"):
            MongoWriter.save(
                doc=doc,
                mongo_client=mock_client,
                database_name="research_toolkit",
                collection_name="research_documents"
            )
    
    def test_returns_clean_output(self):
        """Test that save returns only the expected output fields."""
        from src.utils.mongo_writer import MongoWriter
        
        # Create mock with ObjectId
        mock_result = Mock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439011")
        
        mock_collection = Mock()
        mock_collection.insert_one = Mock(return_value=mock_result)
        mock_collection.find_one = Mock(return_value=None)  # No duplicate
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        doc = {
            "conversation_id": "CV-20251126-183613-ABC12",
            "document_id": "TR-20251126-183613-XYZ12",
            "parent_id": None,
            "content_type": "text",
            "question": "Test",
            "markdown_content": "Test"
        }
        
        result = MongoWriter.save(
            doc=doc,
            mongo_client=mock_client,
            database_name="research_toolkit",
            collection_name="research_documents"
        )
        
        # Expected output fields only
        expected_fields = {
            "document_id",
            "conversation_id",
            "parent_id",
            "content_type",
            "mongo_collection",
            "mongo_db",
            "inserted_id"
        }
        
        # Result must have exactly these fields (no extra)
        result_fields = set(result.keys())
        assert result_fields == expected_fields, \
            f"Output fields mismatch. Expected: {expected_fields}, Got: {result_fields}"

