"""
Command-line interface for Research & Debugging Toolkit.

Provides easy access to all 5 tools via command line.
"""

import argparse
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.utils.api_client import RouteLLMClient
from src.storage.mongodb import MongoDBClient
from src.tools.topic_research import TopicResearchTool
from src.tools.coding_research import CodingResearchTool
from src.tools.debugging import DebuggingTool
from src.tools.architecture import ArchitectureTool
from src.tools.general_purpose import GeneralPurposeTool


def create_clients():
    """Create API and database clients from environment variables."""
    try:
        api_client = RouteLLMClient()
        db_client = MongoDBClient()
        db_client.connect()
        return api_client, db_client
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nPlease set the required environment variables:", file=sys.stderr)
        print("  - ROUTELLM_API_KEY", file=sys.stderr)
        print("  - MONGODB_CONNECTION_STRING", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error connecting to services: {e}", file=sys.stderr)
        sys.exit(1)


def topic_research(args):
    """Handle topic research command."""
    api_client, db_client = create_clients()
    tool = TopicResearchTool(api_client, db_client)
    
    complexity = "large" if args.large else "simple"
    use_backup = args.backup
    
    print(f"Researching topic: {args.question}")
    print("=" * 60)
    
    try:
        result = tool.execute(
            question=args.question,
            complexity=complexity,
            use_backup=use_backup,
            save_to_db=not args.no_save
        )
        print(result)
        if not args.no_save:
            print("\n[Saved to MongoDB]")
    except (ValueError, ConnectionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        sys.exit(1)


def coding_research(args):
    """Handle coding research command."""
    api_client, db_client = create_clients()
    tool = CodingResearchTool(api_client, db_client)
    
    complexity = args.complexity if args.complexity in ["simple", "moderate", "deep"] else "simple"
    
    print(f"Researching coding question: {args.question}")
    print("=" * 60)
    
    try:
        result = tool.execute(
            question=args.question,
            complexity=complexity,
            save_to_db=not args.no_save
        )
        print(result)
        if not args.no_save:
            print("\n[Saved to MongoDB]")
    except (ValueError, ConnectionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        sys.exit(1)


def debugging(args):
    """Handle debugging command."""
    api_client, db_client = create_clients()
    tool = DebuggingTool(api_client, db_client)
    
    # Combine code and explanation into question
    question = f"Code:\n{args.code}\n\nExplanation:\n{args.explanation}"
    
    print("Analyzing debugging issue...")
    print("=" * 60)
    
    try:
        result = tool.execute(
            question=question,
            tier=args.tier,
            save_to_db=not args.no_save
        )
        print(result)
        if not args.no_save:
            print("\n[Saved to MongoDB]")
        
        if args.tier < 3:
            print(f"\n[Tip: If this doesn't help, you can escalate to tier {args.tier + 1}]")
    except (ValueError, ConnectionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        sys.exit(1)


def architecture(args):
    """Handle architecture command."""
    api_client, db_client = create_clients()
    tool = ArchitectureTool(api_client, db_client)
    
    print(f"Designing architecture: {args.question}")
    print("=" * 60)
    
    try:
        result = tool.execute(
            question=args.question,
            use_backup=args.backup,
            save_to_db=not args.no_save
        )
        print(result)
        if not args.no_save:
            print("\n[Saved to MongoDB]")
    except (ValueError, ConnectionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        sys.exit(1)


def general(args):
    """Handle general purpose command."""
    api_client, db_client = create_clients()
    tool = GeneralPurposeTool(api_client, db_client)
    
    complexity = "medium" if args.medium else "simple"
    
    print(f"Processing query: {args.question}")
    print("=" * 60)
    
    try:
        result = tool.execute(
            question=args.question,
            complexity=complexity,
            save_to_db=not args.no_save
        )
        print(result)
        if not args.no_save:
            print("\n[Saved to MongoDB]")
    except (ValueError, ConnectionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Research & Debugging Toolkit - Multi-model AI system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Topic research
  python -m src.cli.main topic-research "What is test-driven development?"
  
  # Coding research
  python -m src.cli.main coding-research "How to implement error handling in Python?" --complexity moderate
  
  # Debugging
  python -m src.cli.main debugging --code "def func(): return x" --explanation "NameError: name 'x' is not defined"
  
  # Architecture
  python -m src.cli.main architecture "Design a microservices architecture for e-commerce"
  
  # General purpose
  python -m src.cli.main general "Explain quantum computing"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Topic Research
    parser_tr = subparsers.add_parser("topic-research", help="Research topics and concepts")
    parser_tr.add_argument("question", help="Research question")
    parser_tr.add_argument("--large", action="store_true", help="Use large model for complex topics")
    parser_tr.add_argument("--backup", action="store_true", help="Use backup model")
    parser_tr.add_argument("--no-save", action="store_true", help="Don't save to MongoDB")
    parser_tr.set_defaults(func=topic_research)
    
    # Coding Research
    parser_cr = subparsers.add_parser("coding-research", help="Research coding patterns and best practices")
    parser_cr.add_argument("question", help="Coding research question")
    parser_cr.add_argument("--complexity", choices=["simple", "moderate", "deep"], default="simple",
                          help="Complexity level (default: simple)")
    parser_cr.add_argument("--no-save", action="store_true", help="Don't save to MongoDB")
    parser_cr.set_defaults(func=coding_research)
    
    # Debugging
    parser_db = subparsers.add_parser("debugging", help="Debug code issues")
    parser_db.add_argument("--code", required=True, help="Failing code")
    parser_db.add_argument("--explanation", required=True, help="Error explanation or context")
    parser_db.add_argument("--tier", type=int, choices=[1, 2, 3], default=1,
                          help="Debugging tier (default: 1)")
    parser_db.add_argument("--no-save", action="store_true", help="Don't save to MongoDB")
    parser_db.set_defaults(func=debugging)
    
    # Architecture
    parser_ar = subparsers.add_parser("architecture", help="Design system architecture")
    parser_ar.add_argument("question", help="Architecture question")
    parser_ar.add_argument("--backup", action="store_true", help="Use backup model")
    parser_ar.add_argument("--no-save", action="store_true", help="Don't save to MongoDB")
    parser_ar.set_defaults(func=architecture)
    
    # General Purpose
    parser_gp = subparsers.add_parser("general", help="General purpose queries")
    parser_gp.add_argument("question", help="General question")
    parser_gp.add_argument("--medium", action="store_true", help="Use medium complexity model")
    parser_gp.add_argument("--no-save", action="store_true", help="Don't save to MongoDB")
    parser_gp.set_defaults(func=general)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()

