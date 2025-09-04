#!/usr/bin/env python3
"""
PromptLifter - Main application entry point.

A conversation-focused LLM interface with intelligent context management,
optional search integration, and optimized LLM interactions.
"""

import argparse
import asyncio
import json
import sys
from typing import Any

from .conversation_llm import ConversationLLM, ConversationResponse
from .logging_config import setup_logging


def validate_configuration() -> None:
    """Validate that all required configuration is present."""
    from .config import (
        ANTHROPIC_API_KEY,
        CUSTOM_LLM_ENDPOINT,
        CUSTOM_LLM_MODEL,
        GOOGLE_API_KEY,
        OPENAI_API_KEY,
        PINECONE_API_KEY,
        PINECONE_INDEX,
        TAVILY_API_KEY,
        validate_config,
    )

    missing_vars = []

    # Validate configuration
    config_errors = validate_config()
    if config_errors:
        print("❌ Configuration validation failed:")
        for error in config_errors:
            print(f"  - {error}")
        sys.exit(1)

    # Check for at least one LLM provider
    llm_providers = [
        ("Custom LLM", CUSTOM_LLM_ENDPOINT and CUSTOM_LLM_MODEL),
        ("OpenAI", OPENAI_API_KEY),
        ("Anthropic", ANTHROPIC_API_KEY),
        ("Google", GOOGLE_API_KEY),
    ]

    available_providers = [name for name, available in llm_providers if available]

    if not available_providers:
        print("❌ No LLM providers configured!")
        print("Please configure at least one of:")
        print("  - Custom LLM (CUSTOM_LLM_ENDPOINT + CUSTOM_LLM_MODEL)")
        print("  - OpenAI (OPENAI_API_KEY)")
        print("  - Anthropic (ANTHROPIC_API_KEY)")
        print("  - Google (GOOGLE_API_KEY)")
        sys.exit(1)

    print(f"✅ LLM providers available: {', '.join(available_providers)}")

    # Check required search/vector services
    if not PINECONE_API_KEY:
        missing_vars.append("PINECONE_API_KEY")
    if not PINECONE_INDEX:
        missing_vars.append("PINECONE_INDEX")
    if not TAVILY_API_KEY:
        missing_vars.append("TAVILY_API_KEY")

    if missing_vars:
        print("⚠️  Missing optional environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("Some features may not work without these.")

        # Special note about Pinecone
        if "PINECONE_API_KEY" in missing_vars or "PINECONE_INDEX" in missing_vars:
            print(
                "\n💡 Note: Pinecone is optional. The system will work without it, "
                "but won't have access to internal knowledge base."
            )
            print(
                "   To enable Pinecone: Set PINECONE_API_KEY and PINECONE_INDEX "
                "in your .env file"
            )


def save_result_to_file(
    result: Any, filename: str = "promptlifter_result.json"
) -> None:
    """Save the workflow result to a JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Result saved to {filename}")
    except Exception as e:
        print(f"Error saving result to file: {e}")


def print_result_summary(response: Any) -> None:
    """Print a summary of the conversation response."""
    print("\n" + "=" * 60)
    print("📊 PROMPTLIFTER RESPONSE")
    print("=" * 60)

    if hasattr(response, "message"):
        print("📝 Response Generated: ✅")

        # Show preview of the response
        lines = response.message.split("\n")
        preview_lines = lines[:10]  # Show first 10 lines
        preview = "\n".join(preview_lines)

        print("\n📄 Content Preview:")
        print(preview)

        if len(lines) > 10:
            print("...")

        # Show context sources if available
        if hasattr(response, "context_sources") and response.context_sources:
            print(f"\n🔍 Context Sources: {', '.join(response.context_sources)}")

        # Show token usage if available
        if hasattr(response, "tokens_used") and response.tokens_used:
            print(f"🔢 Tokens Used: {response.tokens_used}")
    else:
        print("📝 Response Generated: ❌")

    print("=" * 60)


async def interactive_mode() -> None:
    """Run the application in interactive mode."""
    print("🚀 PromptLifter Interactive Mode")
    print("Type 'quit', 'exit', or 'q' to exit")

    # Initialize conversation LLM
    llm = ConversationLLM()

    while True:
        try:
            query = input("\n💬 Message: ").strip()

            if query.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break

            if not query:
                print("Please enter a valid message.")
                continue

            print(f"\n🚀 Processing message: {query}")

            # Run the conversation
            response = await llm.chat(query)

            print_result_summary(response)

            # Ask if user wants to save the result
            save_choice = input("\n💾 Save result to file? (y/n): ").strip().lower()
            if save_choice in ["y", "yes"]:
                filename = input(
                    "📁 Filename (default: promptlifter_result.json): "
                ).strip()
                if not filename:
                    filename = "promptlifter_result.json"
                save_result_to_file(response.__dict__, filename)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main() -> None:
    """Main application entry point."""
    # Setup logging
    setup_logging(level="INFO")

    parser = argparse.ArgumentParser(
        description="PromptLifter - Conversation-focused LLM interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            """
Examples:
  python main.py --query "What is machine learning?"
  python main.py --interactive
  python main.py --query "Explain quantum computing" --save result.json
            """
        ),
    )

    parser.add_argument("--query", "-q", type=str, help="Message to send to the LLM")

    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )

    parser.add_argument("--save", "-s", type=str, help="Save result to specified file")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Validate configuration
    validate_configuration()

    if args.interactive:
        asyncio.run(interactive_mode())
    elif args.query:
        print(f"🚀 Processing message: {args.query}")

        # Initialize and run conversation
        async def run_query() -> ConversationResponse:
            llm = ConversationLLM()
            response = await llm.chat(args.query)
            return response

        result = asyncio.run(run_query())

        print_result_summary(result)

        if args.save:
            save_result_to_file(result.__dict__, args.save)
        elif args.verbose:
            print("\n📄 Full Result:")
            print(json.dumps(result.__dict__, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
