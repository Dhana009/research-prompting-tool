"""
Unit tests for document assembly and persistence layer.

Tests that documents are assembled with metadata and ready for MongoDB storage.
"""

import pytest


class TestDocumentAssembler:
    """Test document assembly for System-1 → System-2 integration."""
    
    def test_assembles_root_document_with_metadata(self):
        """Test root document is assembled with all required metadata fields."""
        from src.utils.document_assembler import DocumentAssembler
        
        question = "What is TDD?"
        markdown_content = "TDD explanation ..."
        
        doc = DocumentAssembler.build(
            question=question,
            markdown_content=markdown_content,
            parent=None
        )
        
        # Metadata fields must exist
        assert "conversation_id" in doc
        assert "document_id" in doc
        assert "parent_id" in doc
        assert "content_type" in doc
        
        # Root document specific assertions
        assert doc["parent_id"] is None
        assert doc["content_type"] == "text"
        
        # Original content preserved
        assert doc["question"] == question
        assert doc["markdown_content"] == markdown_content
    
    def test_assembles_followup_document_with_metadata(self):
        """Test follow-up document inherits conversation_id from parent."""
        from src.utils.document_assembler import DocumentAssembler
        
        # Create parent document
        parent_doc = {
            "document_id": "TR-20251126-183613-ABC12",
            "conversation_id": "CV-20251126-183613-XYZ12"
        }
        
        question = "Follow-up question"
        markdown_content = "Follow-up explanation"
        
        doc = DocumentAssembler.build(
            question=question,
            markdown_content=markdown_content,
            parent=parent_doc
        )
        
        # Follow-up specific assertions
        assert doc["conversation_id"] == parent_doc["conversation_id"]
        assert doc["parent_id"] == parent_doc["document_id"]
        
        # New document_id generated
        assert doc["document_id"] != parent_doc["document_id"]
        assert doc["document_id"] is not None
        
        # Content type determined correctly
        assert doc["content_type"] in ["text", "code"]
    
    def test_preserves_original_fields(self):
        """Test that original question and markdown_content are preserved."""
        from src.utils.document_assembler import DocumentAssembler
        
        question = "Explain unit tests"
        markdown_content = "Unit tests verify small functions…"
        
        doc = DocumentAssembler.build(
            question=question,
            markdown_content=markdown_content,
            parent=None
        )
        
        # Original fields must be preserved exactly
        assert doc["question"] == question
        assert doc["markdown_content"] == markdown_content
    
    def test_detects_code_content(self):
        """Test that code content is correctly detected."""
        from src.utils.document_assembler import DocumentAssembler
        
        question = "Show me a test example"
        markdown_content = "def test_add(): assert add(1,2)==3"
        
        doc = DocumentAssembler.build(
            question=question,
            markdown_content=markdown_content,
            parent=None
        )
        
        # Code content must be detected
        assert doc["content_type"] == "code"
    
    def test_output_document_is_mongo_ready(self):
        """Test that output document has exactly the fields MongoDB expects."""
        from src.utils.document_assembler import DocumentAssembler
        
        question = "Test question"
        markdown_content = "Test content"
        
        doc = DocumentAssembler.build(
            question=question,
            markdown_content=markdown_content,
            parent=None
        )
        
        # Expected fields for MongoDB (System-1 → System-2 flow)
        expected_fields = {
            "conversation_id",
            "document_id",
            "parent_id",
            "content_type",
            "question",
            "markdown_content"
        }
        
        # Document must have exactly these fields (no extra, no missing)
        doc_fields = set(doc.keys())
        assert doc_fields == expected_fields, \
            f"Document fields mismatch. Expected: {expected_fields}, Got: {doc_fields}"

