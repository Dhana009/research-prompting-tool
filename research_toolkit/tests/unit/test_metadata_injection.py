"""
Unit tests for metadata injection layer.

Tests conversation_id, parent_id, content_type, and document_id generation.
"""

import pytest
import re


class TestMetadataInjection:
    """Test metadata injection for System-2 integration."""
    
    def test_generates_conversation_id_for_root_document(self):
        """Test conversation_id is generated for root document (no parent)."""
        from src.utils.metadata_builder import MetadataBuilder
        
        metadata = MetadataBuilder.build(
            question="What is TDD?",
            parent_id=None
        )
        
        # conversation_id must exist
        assert "conversation_id" in metadata
        assert metadata["conversation_id"] is not None
        
        # Format: CV-<YYYYMMDD>-<HHMMSS>-<short_id>
        pattern = r'^CV-\d{8}-\d{6}-[A-Z0-9]+$'
        assert re.match(pattern, metadata["conversation_id"]), \
            f"conversation_id format invalid: {metadata['conversation_id']}"
        
        # parent_id must be None for root
        assert metadata["parent_id"] is None
    
    def test_reuses_conversation_id_for_followup(self):
        """Test conversation_id is reused from parent for follow-up documents."""
        from src.utils.metadata_builder import MetadataBuilder
        
        parent_conversation_id = "CV-20251126-183613-XYZ12"
        
        metadata = MetadataBuilder.build(
            question="Follow-up",
            parent_id="TR-123",
            parent_conversation_id=parent_conversation_id
        )
        
        # conversation_id must match parent
        assert metadata["conversation_id"] == parent_conversation_id
    
    def test_generates_parent_id_and_document_id(self):
        """Test document_id and parent_id are generated correctly."""
        from src.utils.metadata_builder import MetadataBuilder
        
        metadata = MetadataBuilder.build(
            question="Test question",
            parent_id=None
        )
        
        # document_id must exist
        assert "document_id" in metadata
        assert metadata["document_id"] is not None
        
        # Format: <PREFIX>-<YYYYMMDD>-<HHMMSS>-<shortid>
        # Example: TR-20251126-183613-ABC12
        pattern = r'^[A-Z]{2}-\d{8}-\d{6}-[A-Z0-9]+$'
        assert re.match(pattern, metadata["document_id"]), \
            f"document_id format invalid: {metadata['document_id']}"
        
        # parent_id must be passed through
        assert metadata["parent_id"] is None
        
        # Test with parent_id
        parent_doc_id = "TR-20251126-183613-ABC12"
        metadata_with_parent = MetadataBuilder.build(
            question="Follow-up",
            parent_id=parent_doc_id
        )
        
        assert metadata_with_parent["parent_id"] == parent_doc_id
    
    def test_determines_content_type(self):
        """Test content_type is determined correctly (text vs code)."""
        from src.utils.metadata_builder import MetadataBuilder
        
        # Code content
        code_content = "def add(x, y):\n    return x + y"
        metadata_code = MetadataBuilder.build(
            question="Test",
            parent_id=None,
            markdown_content=code_content
        )
        
        assert "content_type" in metadata_code
        assert metadata_code["content_type"] == "code"
        
        # Text content
        text_content = "TDD is a software methodology that emphasizes writing tests before code."
        metadata_text = MetadataBuilder.build(
            question="Test",
            parent_id=None,
            markdown_content=text_content
        )
        
        assert "content_type" in metadata_text
        assert metadata_text["content_type"] == "text"

