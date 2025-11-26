"""
Base tool class for all AI research and debugging tools.

Provides common functionality and abstract interface for all tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import pytz

from src.models.question import generate_question_id
from src.models.document import ResearchDocument, Category
from src.storage.mongodb import MongoDBClient
from src.utils.api_client import RouteLLMClient


class BaseTool(ABC):
    """
    Abstract base class for all research and debugging tools.
    
    Provides common functionality:
    - Question ID generation
    - IST timestamp generation
    - MongoDB document creation and storage
    - API client integration
    """
    
    def __init__(
        self,
        api_client: RouteLLMClient,
        db_client: MongoDBClient,
        category: Category
    ):
        """
        Initialize base tool.
        
        Args:
            api_client: RouteLLM API client instance
            db_client: MongoDB client instance
            category: Tool category (from Category enum)
        """
        self.api_client = api_client
        self.db_client = db_client
        self.category = category
        self._tool_prefix = self._get_tool_prefix()
    
    def _get_tool_prefix(self) -> str:
        """Get question ID prefix based on category."""
        prefix_map = {
            Category.TOPIC_RESEARCH: "TR",
            Category.CODING_RESEARCH: "CR",
            Category.DEBUGGING: "DB",
            Category.ARCHITECTURE: "AR",
            Category.GENERAL: "GP"
        }
        return prefix_map.get(self.category, "GP")
    
    def _generate_timestamp_ist(self) -> str:
        """
        Generate timestamp in IST format: YYYY-MM-DD HH:MM:SS IST (DAY_OF_WEEK)
        
        Returns:
            Formatted timestamp string
        """
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        
        # Format: 2025-11-26 10:54:33 IST (Wednesday)
        day_name = now.strftime("%A")
        timestamp = now.strftime(f"%Y-%m-%d %H:%M:%S IST ({day_name})")
        
        return timestamp
    
    def _detect_code_in_content(self, content: str) -> bool:
        """
        Detect if markdown content contains code blocks.
        
        Args:
            content: Markdown content string
            
        Returns:
            True if code blocks found, False otherwise
        """
        # Check for code blocks (```)
        code_block_pattern = r'```'
        import re
        matches = re.findall(code_block_pattern, content)
        return len(matches) >= 2  # At least opening and closing
    
    def _detect_language_tags(self, content: str) -> list:
        """
        Detect programming languages in code blocks.
        
        Args:
            content: Markdown content string
            
        Returns:
            List of detected language tags
        """
        import re
        languages = []
        
        # Pattern to match code block language specifiers: ```python, ```javascript, etc.
        pattern = r'```(\w+)'
        matches = re.findall(pattern, content)
        
        # Common language mappings
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'rb': 'ruby',
            'sh': 'bash',
            'yml': 'yaml'
        }
        
        for match in matches:
            lang = match.lower()
            # Map aliases
            if lang in language_map:
                lang = language_map[lang]
            if lang not in languages:
                languages.append(lang)
        
        return languages
    
    def _estimate_segments(self, content: str) -> int:
        """
        Estimate number of segments for future vectorization.
        
        Simple heuristic: count code blocks and major sections.
        
        Args:
            content: Markdown content string
            
        Returns:
            Estimated number of segments
        """
        import re
        
        # Count code blocks
        code_blocks = len(re.findall(r'```', content)) // 2
        
        # Count major markdown sections (headers)
        headers = len(re.findall(r'^#+\s', content, re.MULTILINE))
        
        # At least 1 segment, plus code blocks and sections
        return max(1, code_blocks + headers)
    
    def _create_document(
        self,
        question: str,
        markdown_content: str,
        model_used: str,
        complexity_score: int,
        sub_category: Optional[str] = None
    ) -> ResearchDocument:
        """
        Create a ResearchDocument from tool response.
        
        Args:
            question: User's question
            markdown_content: AI response in markdown
            model_used: Model name used
            complexity_score: Complexity score (1-10)
            sub_category: Optional sub-category
            
        Returns:
            ResearchDocument instance
        """
        question_id = generate_question_id(self._tool_prefix)
        timestamp_ist = self._generate_timestamp_ist()
        contains_code = self._detect_code_in_content(markdown_content)
        language_tags = self._detect_language_tags(markdown_content)
        estimated_segments = self._estimate_segments(markdown_content)
        
        return ResearchDocument(
            question=question,
            markdown_content=markdown_content,
            category=self.category,
            sub_category=sub_category,
            question_id=question_id,
            timestamp_ist=timestamp_ist,
            model_used=model_used,
            complexity_score=complexity_score,
            contains_code=contains_code,
            estimated_segments=estimated_segments,
            language_tags=language_tags,
            segments=[],
            vectors=[],
            graph_nodes=[],
            graph_edges=[]
        )
    
    def save_to_mongodb(
        self,
        question: str,
        markdown_content: str,
        model_used: str,
        complexity_score: int,
        sub_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save research response to MongoDB.
        
        Args:
            question: User's question
            markdown_content: AI response in markdown
            model_used: Model name used
            complexity_score: Complexity score (1-10)
            sub_category: Optional sub-category
            
        Returns:
            MongoDB insert result dictionary
        """
        document = self._create_document(
            question=question,
            markdown_content=markdown_content,
            model_used=model_used,
            complexity_score=complexity_score,
            sub_category=sub_category
        )
        
        # Convert Pydantic model to dict for MongoDB
        doc_dict = document.model_dump()
        
        # Insert into MongoDB
        result = self.db_client.insert_one(doc_dict)
        return result
    
    @abstractmethod
    def execute(self, question: str, **kwargs) -> str:
        """
        Execute the tool and return markdown response.
        
        This method must be implemented by each tool.
        
        Args:
            question: User's question or input
            **kwargs: Additional tool-specific parameters
            
        Returns:
            Markdown response string
        """
        pass

