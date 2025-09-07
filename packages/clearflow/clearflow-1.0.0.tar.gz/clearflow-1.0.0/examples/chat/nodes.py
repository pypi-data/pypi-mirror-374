"""Chat node implementations - intelligent entities with complete I/O capabilities."""

import dataclasses
from dataclasses import dataclass
from typing import Literal, override

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from clearflow import Node, NodeResult


@dataclass(frozen=True)
class ChatMessage:
    """Immutable chat message structure."""

    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class ChatState:
    """Immutable chat application state.

    All fields are required - we use dataclasses.replace() to update.
    Empty defaults make initialization clean.
    """

    messages: tuple[ChatMessage, ...] = ()
    last_response: str = ""
    user_input: str = ""


def _to_openai_message(msg: ChatMessage) -> ChatCompletionMessageParam:
    """Convert ChatMessage to OpenAI format with type narrowing.

    OpenAI expects specific role literals for each message type,
    not a union. This helper provides the type narrowing.

    Returns:
        OpenAI-compatible message dictionary with correct role literal.
    """
    if msg.role == "user":
        return {"role": "user", "content": msg.content}
    if msg.role == "assistant":
        return {"role": "assistant", "content": msg.content}
    # system
    return {"role": "system", "content": msg.content}


def _ensure_system_message(messages: tuple[ChatMessage, ...], system_prompt: str) -> tuple[ChatMessage, ...]:
    """Ensure conversation has a system message.

    Returns:
        Messages tuple with system message prepended if missing.
    """
    if not messages:
        return (ChatMessage(role="system", content=system_prompt),)
    return messages


async def _get_ai_response(messages: tuple[ChatMessage, ...], model: str) -> str:
    """Call OpenAI API and get response.

    Returns:
        AI-generated response content string.
    """
    client = AsyncOpenAI()
    # OpenAI API requires a list, not a tuple - this is outside our control
    api_messages = [  # clearflow: ignore[IMM006] # OpenAI requires list
        _to_openai_message(msg) for msg in messages
    ]

    response = await client.chat.completions.create(
        model=model,
        messages=api_messages,
    )

    content = response.choices[0].message.content
    return content or ""


@dataclass(frozen=True)
class HumanNode(Node[ChatState]):
    """Human intelligent entity with complete I/O capabilities.

    This node represents a human participant in the conversation, handling:
    - Input: Getting console input from the user
    - Output: Displaying AI responses on the console
    - Cognition: Deciding whether to continue or quit the conversation
    - Memory: Adding human messages to the conversation history

    The human is a complete intelligent entity, not just an input source.
    """

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        """Execute human interaction cycle: display, input, decide.

        Returns:
            NodeResult with "responded" (message sent) or "quit" (exit).
        """
        # Output capability: Display AI response if present
        if state.last_response:
            print(f"\nAssistant: {state.last_response}")
            print("-" * 50)

        # Input capability: Get human input
        try:
            user_input = input("You: ")

            # Cognitive process: Decide to quit or continue
            if user_input.lower() in {"quit", "exit", "bye"}:
                print("\nGoodbye!")
                return NodeResult(state, outcome="quit")

            # Memory management: Add human message to conversation
            messages = (*state.messages, ChatMessage(role="user", content=user_input))
            new_state = dataclasses.replace(
                state,
                messages=messages,
                user_input=user_input,
                last_response="",  # Clear for next cycle
            )
            return NodeResult(new_state, outcome="responded")

        except (EOFError, KeyboardInterrupt):
            # Graceful exit on interrupt
            print("\nGoodbye!")
            return NodeResult(state, outcome="quit")


@dataclass(frozen=True)
class LlmNode(Node[ChatState]):
    """LLM intelligent entity with complete I/O capabilities.

    This node represents an AI participant in the conversation, handling:
    - Input: Receiving human messages from state
    - Output: Generating responses via OpenAI API
    - Cognition: Reasoning about context and generating appropriate responses
    - Memory: Adding AI responses to the conversation history

    The LLM is a complete intelligent entity, not just a processing function.
    """

    model: str = "gpt-5-nano-2025-08-07"
    system_prompt: str = "You are a helpful assistant."

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        """Execute LLM interaction cycle: receive, process, respond.

        Returns:
            NodeResult with "responded" outcome (always responds).
        """
        # Ensure system message exists for context
        messages = _ensure_system_message(state.messages, self.system_prompt)

        # Input capability: Receive human message from state
        # (Already in messages from HumanNode)

        # Cognitive process + Output capability: Generate response via API
        assistant_response = await _get_ai_response(messages, self.model)

        # Memory management: Add AI response to conversation
        messages = (*messages, ChatMessage(role="assistant", content=assistant_response))
        new_state = dataclasses.replace(
            state,
            messages=messages,
            last_response=assistant_response,
            user_input="",  # Clear human input after processing
        )

        # LLM always responds (no quit outcome)
        return NodeResult(new_state, outcome="responded")
