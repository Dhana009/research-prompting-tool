"""
Unit tests for MongoDB document schema validation.

Tests document structure matches requirements exactly.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError


class TestDocumentSchema:
    """Test MongoDB document schema structure."""
    
    def test_document_structure_matches_requirements(self):
        """Test document has all required fields from requirements."""
        from src.models.document import ResearchDocument
        
        # Create a valid document
        doc = ResearchDocument(
            question="What is test-driven development?",
            markdown_content="# Answer\n\nTDD is...",
            category="topic_research",
            question_id="TR-20251126-105433IST-WED-QX18",
            timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
            model_used="gemini-2.5-flash",
            complexity_score=3,
            contains_code=False,
            estimated_segments=1,
            language_tags=[],
            segments=[],
            vectors=[],
            graph_nodes=[],
            graph_edges=[]
        )
        
        # Verify all required fields exist
        assert hasattr(doc, "question")
        assert hasattr(doc, "markdown_content")
        assert hasattr(doc, "category")
        assert hasattr(doc, "question_id")
        assert hasattr(doc, "timestamp_ist")
        assert hasattr(doc, "model_used")
        assert hasattr(doc, "complexity_score")
        assert hasattr(doc, "contains_code")
        assert hasattr(doc, "estimated_segments")
        assert hasattr(doc, "language_tags")
        assert hasattr(doc, "segments")
        assert hasattr(doc, "vectors")
        assert hasattr(doc, "graph_nodes")
        assert hasattr(doc, "graph_edges")
    
    def test_timestamp_format(self):
        """Test timestamp format: YYYY-MM-DD HH:MM:SS IST (DAY_OF_WEEK)."""
        from src.models.document import ResearchDocument
        
        # Valid timestamp
        valid_timestamp = "2025-11-26 10:54:33 IST (Wednesday)"
        doc = ResearchDocument(
            question="Test",
            markdown_content="Test",
            category="topic_research",
            question_id="TR-20251126-105433IST-WED-QX18",
            timestamp_ist=valid_timestamp,
            model_used="test",
            complexity_score=1,
            contains_code=False,
            estimated_segments=1,
            language_tags=[],
            segments=[],
            vectors=[],
            graph_nodes=[],
            graph_edges=[]
        )
        
        assert doc.timestamp_ist == valid_timestamp
        
        # Invalid timestamp formats should fail
        invalid_formats = [
            "2025-11-26 10:54:33",  # Missing IST and day
            "2025-11-26T10:54:33",  # ISO format
            "26-11-2025 10:54:33 IST (Wednesday)",  # Wrong date format
        ]
        
        for invalid_ts in invalid_formats:
            with pytest.raises(ValidationError):
                ResearchDocument(
                    question="Test",
                    markdown_content="Test",
                    category="topic_research",
                    question_id="TR-20251126-105433IST-WED-QX18",
                    timestamp_ist=invalid_ts,
                    model_used="test",
                    complexity_score=1,
                    contains_code=False,
                    estimated_segments=1,
                    language_tags=[],
                    segments=[],
                    vectors=[],
                    graph_nodes=[],
                    graph_edges=[]
                )
    
    def test_category_enum_validation(self):
        """Test category must be one of 5 valid categories."""
        from src.models.document import ResearchDocument
        
        valid_categories = [
            "topic_research",
            "coding_research",
            "debugging",
            "architecture",
            "general"
        ]
        
        for category in valid_categories:
            doc = ResearchDocument(
                question="Test",
                markdown_content="Test",
                category=category,
                question_id="TR-20251126-105433IST-WED-QX18",
                timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
                model_used="test",
                complexity_score=1,
                contains_code=False,
                estimated_segments=1,
                language_tags=[],
                segments=[],
                vectors=[],
                graph_nodes=[],
                graph_edges=[]
            )
            assert doc.category == category
        
        # Invalid category should fail
        with pytest.raises(ValidationError):
            ResearchDocument(
                question="Test",
                markdown_content="Test",
                category="invalid_category",
                question_id="TR-20251126-105433IST-WED-QX18",
                timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
                model_used="test",
                complexity_score=1,
                contains_code=False,
                estimated_segments=1,
                language_tags=[],
                segments=[],
                vectors=[],
                graph_nodes=[],
                graph_edges=[]
            )
    
    def test_required_fields_validation(self):
        """Test missing required fields raise validation error."""
        from src.models.document import ResearchDocument
        
        # Test missing question
        with pytest.raises(ValidationError):
            ResearchDocument(
                markdown_content="Test",
                category="topic_research",
                question_id="TR-20251126-105433IST-WED-QX18",
                timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
                model_used="test",
                complexity_score=1,
                contains_code=False,
                estimated_segments=1,
                language_tags=[],
                segments=[],
                vectors=[],
                graph_nodes=[],
                graph_edges=[]
            )
        
        # Test missing markdown_content
        with pytest.raises(ValidationError):
            ResearchDocument(
                question="Test",
                category="topic_research",
                question_id="TR-20251126-105433IST-WED-QX18",
                timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
                model_used="test",
                complexity_score=1,
                contains_code=False,
                estimated_segments=1,
                language_tags=[],
                segments=[],
                vectors=[],
                graph_nodes=[],
                graph_edges=[]
            )
        
        # Test missing category
        with pytest.raises(ValidationError):
            ResearchDocument(
                question="Test",
                markdown_content="Test",
                question_id="TR-20251126-105433IST-WED-QX18",
                timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
                model_used="test",
                complexity_score=1,
                contains_code=False,
                estimated_segments=1,
                language_tags=[],
                segments=[],
                vectors=[],
                graph_nodes=[],
                graph_edges=[]
            )
    
    def test_complexity_score_range(self):
        """Test complexity_score must be between 1 and 10."""
        from src.models.document import ResearchDocument
        
        # Valid scores
        for score in [1, 5, 10]:
            doc = ResearchDocument(
                question="Test",
                markdown_content="Test",
                category="topic_research",
                question_id="TR-20251126-105433IST-WED-QX18",
                timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
                model_used="test",
                complexity_score=score,
                contains_code=False,
                estimated_segments=1,
                language_tags=[],
                segments=[],
                vectors=[],
                graph_nodes=[],
                graph_edges=[]
            )
            assert doc.complexity_score == score
        
        # Invalid scores should fail
        for invalid_score in [0, 11, -1, 100]:
            with pytest.raises(ValidationError):
                ResearchDocument(
                    question="Test",
                    markdown_content="Test",
                    category="topic_research",
                    question_id="TR-20251126-105433IST-WED-QX18",
                    timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
                    model_used="test",
                    complexity_score=invalid_score,
                    contains_code=False,
                    estimated_segments=1,
                    language_tags=[],
                    segments=[],
                    vectors=[],
                    graph_nodes=[],
                    graph_edges=[]
                )
    
    def test_optional_fields(self):
        """Test optional fields (sub_category) can be None or provided."""
        from src.models.document import ResearchDocument
        
        # Without sub_category
        doc1 = ResearchDocument(
            question="Test",
            markdown_content="Test",
            category="topic_research",
            question_id="TR-20251126-105433IST-WED-QX18",
            timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
            model_used="test",
            complexity_score=1,
            contains_code=False,
            estimated_segments=1,
            language_tags=[],
            segments=[],
            vectors=[],
            graph_nodes=[],
            graph_edges=[]
        )
        assert doc1.sub_category is None
        
        # With sub_category
        doc2 = ResearchDocument(
            question="Test",
            markdown_content="Test",
            category="topic_research",
            sub_category="python",
            question_id="TR-20251126-105433IST-WED-QX18",
            timestamp_ist="2025-11-26 10:54:33 IST (Wednesday)",
            model_used="test",
            complexity_score=1,
            contains_code=False,
            estimated_segments=1,
            language_tags=[],
            segments=[],
            vectors=[],
            graph_nodes=[],
            graph_edges=[]
        )
        assert doc2.sub_category == "python"

