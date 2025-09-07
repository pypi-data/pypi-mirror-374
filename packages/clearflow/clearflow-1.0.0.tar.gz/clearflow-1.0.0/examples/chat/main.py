#!/usr/bin/env python3
"""Main entry point for the human-in-the-loop chat application."""

import asyncio
import os
import sys

from dotenv import load_dotenv

from examples.chat.chat_flow import create_chat_flow
from examples.chat.nodes import ChatState


async def main() -> None:
    """Main application entry point."""
    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    # Welcome message
    print("Welcome to ClearFlow Chat!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("-" * 50)

    try:
        # Create human-in-the-loop flow
        flow = create_chat_flow()

        # Start with initial empty state
        initial_state = ChatState()

        # Let the flow handle all human-AI interaction until termination
        await flow(initial_state)

    except (KeyboardInterrupt, EOFError):
        # User interrupted - exit gracefully
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
