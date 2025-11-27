"""
Integration tests for document orchestrator.

Tests the full System-1 pipeline: MetadataBuilder → DocumentAssembler → MongoWriter.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from bson import ObjectId


class TestDocumentOrchestrator:
    """Test document orchestrator for System-1 core entry point."""
    
    def test_saves_root_document_successfully(self):
        """Test that root document is saved successfully with all metadata."""
        from src.utils.document_orchestrator import DocumentOrchestrator
        
        # Mock MongoDB client
        mock_result = Mock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439011")
        
        mock_collection = Mock()
        mock_collection.insert_one = Mock(return_value=mock_result)
        mock_collection.find_one = Mock(return_value=None)  # No duplicate, no parent
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        question = "What is TDD?"
        markdown_content = "TDD is a software development methodology..."
        
        result = DocumentOrchestrator.save_document(
            question=question,
            markdown_content=markdown_content,
            parent_id=None,
            mongo_client=mock_client,
            database_name="research_toolkit",
            collection_name="research_documents"
        )
        
        # Assert metadata assembled
        assert "document_id" in result
        assert "conversation_id" in result
        assert "parent_id" in result
        assert "inserted_id" in result
        
        # Root document specific assertions
        assert result["parent_id"] is None
        
        # Assert document was inserted
        assert mock_collection.insert_one.call_count == 1
    
    def test_saves_followup_document_successfully(self):
        """Test that follow-up document inherits conversation_id from parent."""
        from src.utils.document_orchestrator import DocumentOrchestrator
        
        # Mock parent document
        parent_doc = {
            "document_id": "TR-20251126-183613-ABC12",
            "conversation_id": "CV-20251126-183613-XYZ12",
            "parent_id": None,
            "content_type": "text"
        }
        
        # Mock MongoDB client
        mock_result = Mock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439012")
        
        mock_collection = Mock()
        mock_collection.insert_one = Mock(return_value=mock_result)
        mock_collection.find_one = Mock(side_effect=[
            parent_doc,  # First call: find parent
            None  # Second call: check for duplicate
        ])
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        question = "Follow-up question"
        markdown_content = "Follow-up explanation"
        parent_id = "TR-20251126-183613-ABC12"
        
        result = DocumentOrchestrator.save_document(
            question=question,
            markdown_content=markdown_content,
            parent_id=parent_id,
            mongo_client=mock_client,
            database_name="research_toolkit",
            collection_name="research_documents"
        )
        
        # Assert conversation_id reused
        assert result["conversation_id"] == parent_doc["conversation_id"]
        
        # Assert parent_id set
        assert result["parent_id"] == parent_id
        
        # Assert new document_id generated
        assert result["document_id"] != parent_id
        assert result["document_id"] is not None
        
        # Assert inserted_id returned
        assert "inserted_id" in result
    
    def test_raises_error_when_parent_not_found(self):
        """Test that ValueError is raised when parent document is not found."""
        from src.utils.document_orchestrator import DocumentOrchestrator
        
        # Mock MongoDB client with no parent found
        mock_collection = Mock()
        mock_collection.find_one = Mock(return_value=None)  # Parent not found
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        question = "Follow-up question"
        markdown_content = "Follow-up explanation"
        parent_id = "TR-NONEXISTENT-123"
        
        # Expect ValueError
        with pytest.raises(ValueError, match="parent document not found"):
            DocumentOrchestrator.save_document(
                question=question,
                markdown_content=markdown_content,
                parent_id=parent_id,
                mongo_client=mock_client,
                database_name="research_toolkit",
                collection_name="research_documents"
            )
    
    def test_writes_to_correct_collection(self):
        """Test that orchestrator uses the correct database and collection."""
        from src.utils.document_orchestrator import DocumentOrchestrator
        
        # Mock MongoDB client
        mock_result = Mock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439013")
        
        mock_collection = Mock()
        mock_collection.insert_one = Mock(return_value=mock_result)
        mock_collection.find_one = Mock(return_value=None)
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        question = "Test question"
        markdown_content = "Test content"
        db_name = "research_toolkit"
        coll_name = "research_documents"
        
        DocumentOrchestrator.save_document(
            question=question,
            markdown_content=markdown_content,
            parent_id=None,
            mongo_client=mock_client,
            database_name=db_name,
            collection_name=coll_name
        )
        
        # Assert correct database accessed
        mock_client.__getitem__.assert_called_with(db_name)
        
        # Assert correct collection accessed
        mock_db.__getitem__.assert_called_with(coll_name)
    
    def test_preserves_question_and_markdown(self):
        """Test that orchestrator does not modify question or markdown_content."""
        from src.utils.document_orchestrator import DocumentOrchestrator
        
        # Mock MongoDB client
        mock_result = Mock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439014")
        
        mock_collection = Mock()
        mock_collection.insert_one = Mock(return_value=mock_result)
        mock_collection.find_one = Mock(return_value=None)
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        question = "Original question text"
        markdown_content = "Original markdown content"
        
        result = DocumentOrchestrator.save_document(
            question=question,
            markdown_content=markdown_content,
            parent_id=None,
            mongo_client=mock_client,
            database_name="research_toolkit",
            collection_name="research_documents"
        )
        
        # Get the document that was inserted
        inserted_doc = mock_collection.insert_one.call_args[0][0]
        
        # Assert original fields preserved
        assert inserted_doc["question"] == question
        assert inserted_doc["markdown_content"] == markdown_content
    
    def test_returns_mongo_metadata_in_output(self):
        """Test that final output includes all MongoDB metadata fields."""
        from src.utils.document_orchestrator import DocumentOrchestrator
        
        # Mock MongoDB client
        mock_result = Mock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439015")
        
        mock_collection = Mock()
        mock_collection.insert_one = Mock(return_value=mock_result)
        mock_collection.find_one = Mock(return_value=None)
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        question = "Test question"
        markdown_content = "Test content"
        
        result = DocumentOrchestrator.save_document(
            question=question,
            markdown_content=markdown_content,
            parent_id=None,
            mongo_client=mock_client,
            database_name="research_toolkit",
            collection_name="research_documents"
        )
        
        # Expected output fields
        expected_fields = {
            "document_id",
            "conversation_id",
            "parent_id",
            "content_type",
            "mongo_db",
            "mongo_collection",
            "inserted_id"
        }
        
        # Assert all expected fields present
        result_fields = set(result.keys())
        assert result_fields == expected_fields, \
            f"Output fields mismatch. Expected: {expected_fields}, Got: {result_fields}"
    
    def test_integrates_all_modules(self):
        """Test that orchestrator calls MetadataBuilder, DocumentAssembler, and MongoWriter."""
        from src.utils.document_orchestrator import DocumentOrchestrator
        
        # Mock MongoDB client
        mock_result = Mock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439016")
        
        mock_collection = Mock()
        mock_collection.insert_one = Mock(return_value=mock_result)
        mock_collection.find_one = Mock(return_value=None)
        
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_db.list_collection_names = Mock(return_value=["research_documents"])
        
        mock_client = Mock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_client.list_database_names = Mock(return_value=["research_toolkit"])
        
        question = "Test question"
        markdown_content = "Test content"
        
        # Patch all three modules to verify integration
        # Patch MetadataBuilder.build method (used by DocumentAssembler)
        # Patch DocumentAssembler and MongoWriter in orchestrator
        with patch('src.utils.metadata_builder.MetadataBuilder.build') as mock_metadata_build, \
             patch('src.utils.document_orchestrator.DocumentAssembler') as mock_assembler, \
             patch('src.utils.document_orchestrator.MongoWriter') as mock_writer:
            
            # Setup MetadataBuilder.build mock return value
            mock_metadata_build.return_value = {
                "conversation_id": "CV-20251126-183613-ABC12",
                "document_id": "TR-20251126-183613-XYZ12",
                "parent_id": None,
                "content_type": "text"
            }
            
            # Setup DocumentAssembler mock - make it call real method but track calls
            from src.utils.document_assembler import DocumentAssembler as RealAssembler
            def assembler_build(*args, **kwargs):
                # Call real assembler which will call mocked MetadataBuilder.build
                return RealAssembler.build(*args, **kwargs)
            
            mock_assembler.build.side_effect = assembler_build
            
            mock_writer.save.return_value = {
                "document_id": "TR-20251126-183613-XYZ12",
                "conversation_id": "CV-20251126-183613-ABC12",
                "parent_id": None,
                "content_type": "text",
                "mongo_db": "research_toolkit",
                "mongo_collection": "research_documents",
                "inserted_id": str(mock_result.inserted_id)
            }
            
            # Call orchestrator
            DocumentOrchestrator.save_document(
                question=question,
                markdown_content=markdown_content,
                parent_id=None,
                mongo_client=mock_client,
                database_name="research_toolkit",
                collection_name="research_documents"
            )
            
            # Assert MetadataBuilder.build was called (through DocumentAssembler)
            assert mock_metadata_build.called
            
            # Assert DocumentAssembler.build was called
            assert mock_assembler.build.called
            
            # Assert MongoWriter.save was called
            assert mock_writer.save.called

