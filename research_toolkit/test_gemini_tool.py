#!/usr/bin/env python3
"""
Quick test script for Gemini research tool.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.api_client import RouteLLMClient
from src.storage.mongodb import MongoDBClient
from src.tools.topic_research import TopicResearchTool

def test_topic_research():
    """Test the topic_research tool (uses Gemini)."""
    print("=" * 60)
    print("Testing Gemini Topic Research Tool")
    print("=" * 60)
    
    # Initialize clients
    try:
        api_client = RouteLLMClient()
        db_client = MongoDBClient()
        db_client.connect()
        print("✅ Clients initialized")
    except Exception as e:
        print(f"❌ Error initializing clients: {e}")
        return
    
    # Create tool
    tool = TopicResearchTool(api_client, db_client)
    print("✅ Tool created")
    
    # Test question
    question = "What is test-driven development?"
    print(f"\n📝 Question: {question}")
    print("\n🔄 Calling Gemini research tool...\n")
    
    try:
        # Execute research (this will save to MongoDB by default)
        result = tool.execute(
            question=question,
            complexity="simple",
            save_to_db=True,
            parent_id=None  # Root document
        )
        
        print("=" * 60)
        print("✅ Research completed successfully!")
        print("=" * 60)
        print("\n📄 Response (first 500 chars):")
        print("-" * 60)
        print(result[:500])
        if len(result) > 500:
            print("...")
        print("-" * 60)
        print(f"\n📊 Total response length: {len(result)} characters")
        print("\n💾 Document saved to MongoDB with new metadata:")
        print("   - conversation_id (new)")
        print("   - document_id (new)")
        print("   - parent_id (None for root)")
        print("   - content_type (text/code)")
        
    except Exception as e:
        print(f"\n❌ Error during research: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_topic_research()


