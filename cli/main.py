#!/usr/bin/env python3
"""
DuckAI CLI - Command line interface for DuckDuckGo AI
"""

import sys
import argparse
from typing import Optional

sys.path.insert(0, "/home/ia/Projects/websites/duck-ai-ca/src")

from duckai import DuckAIClient
from duckai.utils import print_stream_chunk


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog="duckai",
        description="CLI for DuckDuckGo AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  duckai chat "What is Python?"
  duckai chat --model claude-3-haiku "Explain quantum computing"
  duckai interactive
  duckai models
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Send a single chat message")
    chat_parser.add_argument("message", nargs="+", help="Message to send")
    chat_parser.add_argument(
        "--model",
        "-m",
        default="gpt-4o-mini",
        help="Model to use (default: gpt-4o-mini)",
    )
    chat_parser.add_argument(
        "--stream", "-s", action="store_true", help="Stream response"
    )

    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactive chat session")

    # List models
    subparsers.add_parser("models", help="List available models")

    return parser


def cmd_chat(args) -> int:
    """Handle chat command"""
    client = DuckAIClient()
    message = " ".join(args.message)

    try:
        if args.stream:
            print("Assistant: ", end="", flush=True)
            for chunk in client.stream_chat(message, model=args.model):
                print_stream_chunk(chunk)
            print()  # Final newline
        else:
            response = client.chat(message, model=args.model)
            print(f"Assistant: {response}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_interactive() -> int:
    """Handle interactive mode"""
    client = DuckAIClient()
    print("DuckAI Interactive Mode")
    print("Type 'exit' or 'quit' to exit, 'models' to list models")
    print("-" * 50)

    current_model = "gpt-4o-mini"

    while True:
        try:
            user_input = input(f"\n[{current_model}] You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            if user_input.lower() == "models":
                models = client.get_available_models()
                print("\nAvailable models:")
                for i, model in enumerate(models, 1):
                    marker = " *" if model == current_model else ""
                    print(f"  {i}. {model}{marker}")
                continue

            if user_input.startswith("/model "):
                new_model = user_input[7:].strip()
                if new_model in client.get_available_models():
                    current_model = new_model
                    print(f"Switched to model: {current_model}")
                else:
                    print(f"Unknown model: {new_model}")
                continue

            # Send message
            print("\nAssistant: ", end="", flush=True)
            for chunk in client.stream_chat(user_input, model=current_model):
                print_stream_chunk(chunk)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

    return 0


def cmd_models() -> int:
    """Handle models command"""
    client = DuckAIClient()
    models = client.get_available_models()

    print("Available models:")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")

    return 0


def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "chat":
        return cmd_chat(args)
    elif args.command == "interactive":
        return cmd_interactive()
    elif args.command == "models":
        return cmd_models()

    return 0


if __name__ == "__main__":
    sys.exit(main())
