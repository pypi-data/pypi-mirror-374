"""Test Node abstraction features of ClearFlow.

This module tests the Node class functionality including lifecycle hooks,
lifecycle hooks, and routing patterns for mission-critical AI orchestration.

"""

from dataclasses import dataclass as dc
from dataclasses import replace
from typing import override

from clearflow import Node, NodeResult
from tests.conftest import AgentState, Message, ValidationState

# Module-level test nodes to reduce complexity


@dc(frozen=True)
class TokenCountNode(Node[ValidationState]):
    """Node for token counting in LLM validation."""

    name: str = "token_counter"

    @override
    async def exec(self, state: ValidationState) -> NodeResult[ValidationState]:
        # Transformation: count tokens (simplified)
        token_count = len(state.input_text.split())

        if token_count > 100:
            errors = (*state.errors, f"Token count {token_count} exceeds limit")
            new_state = replace(state, errors=errors, validated=False)
            outcome = "too_long"
        else:
            new_state = replace(state, validated=True)
            outcome = "valid_length"

        return NodeResult(new_state, outcome=outcome)


@dc(frozen=True)
class PromptState:
    """Immutable state for prompt engineering pipeline."""

    raw_prompt: str
    sanitized: bool = False
    validated: bool = False
    enhanced: bool = False


@dc(frozen=True)
class PromptEngineeringNode(Node[PromptState]):
    """Node demonstrating lifecycle hooks for prompt engineering."""

    name: str = "prompt_engineer"

    @override
    async def prep(self, state: PromptState) -> PromptState:
        # Sanitize prompt in prep phase
        return replace(state, sanitized=True)

    @override
    async def exec(self, state: PromptState) -> NodeResult[PromptState]:
        # Validate prompt in main execution
        new_state = replace(state, validated=True)
        return NodeResult(new_state, outcome="validated")

    @override
    async def post(
        self,
        result: NodeResult[PromptState],
    ) -> NodeResult[PromptState]:
        # Enhance prompt in post phase
        new_state = replace(result.state, enhanced=True)
        return NodeResult(new_state, outcome=result.outcome)


@dc(frozen=True)
class LLMRouterNode(Node[AgentState]):
    """Routes to different paths based on LLM analysis."""

    name: str = "llm_router"

    @override
    async def exec(self, state: AgentState) -> NodeResult[AgentState]:
        # Analyze last user message for intent (simulating LLM classification)
        last_msg = state.messages[-1] if state.messages else None

        # Determine outcome and response based on message content
        outcome, response = self._classify_intent(last_msg)

        # Immutable state update
        new_state = AgentState(
            messages=(*state.messages, response),
            context=state.context,
            temperature=0.3 if outcome == "code_generation" else state.temperature,
        )
        return NodeResult(new_state, outcome=outcome)

    def _classify_intent(self, msg: Message | None) -> tuple[str, Message]:
        """Classify user intent from message.

        Returns:
            Tuple of (intent string, response message).
        """
        if not msg or msg.role != "user":
            return "no_input", Message(role="assistant", content="Please provide input.")

        content_lower = msg.content.lower()
        if "weather" in content_lower:
            return "tool_required", Message(
                role="assistant",
                content="I'll check the weather for you.",
            )
        if "code" in content_lower:
            return "code_generation", Message(
                role="assistant",
                content="I'll help you write code.",
            )

        return "direct_response", Message(
            role="assistant",
            content="I understand your request.",
        )


class TestNode:
    """Test the Node abstraction."""

    @staticmethod
    async def test_immutable_transformations() -> None:
        """Test that nodes perform immutable transformations - same input produces same output."""
        node = TokenCountNode()
        initial = ValidationState(input_text="Short prompt for testing")

        # Multiple calls with same input produce same output (immutable transformations)
        result1 = await node(initial)
        result2 = await node(initial)

        assert result1.state == result2.state
        assert result1.outcome == result2.outcome

    @staticmethod
    async def test_validation_success() -> None:
        """Test successful validation for short text."""
        node = TokenCountNode()
        initial = ValidationState(input_text="Short prompt for testing")

        result = await node(initial)

        assert result.state.validated is True
        assert result.outcome == "valid_length"
        # Verify immutability
        assert initial.validated is False

    @staticmethod
    async def test_validation_failure() -> None:
        """Test validation failure for long text."""
        node = TokenCountNode()
        # Create text with more than 100 words
        long_text = " ".join(["word"] * 101)
        initial = ValidationState(input_text=long_text)

        result = await node(initial)

        assert result.state.validated is False
        assert result.outcome == "too_long"
        assert len(result.state.errors) == 1
        assert "exceeds limit" in result.state.errors[0]

    @staticmethod
    async def test_lifecycle_hooks() -> None:
        """Test that prep and post hooks work correctly."""
        node = PromptEngineeringNode()
        initial = PromptState(raw_prompt="Explain quantum computing")
        result = await node(initial)

        assert result.state.sanitized is True
        assert result.state.validated is True
        assert result.state.enhanced is True
        assert initial.sanitized is False  # Original unchanged

    @staticmethod
    async def test_router_no_input() -> None:
        """Test router handles missing user input."""
        node = LLMRouterNode()
        empty_state = AgentState(messages=(), context="assistant")
        result = await node(empty_state)

        assert result.outcome == "no_input"
        assert "Please provide input" in result.state.messages[0].content

    @staticmethod
    async def test_router_tool_required() -> None:
        """Test router identifies tool-required intent."""
        node = LLMRouterNode()
        weather_state = AgentState(
            messages=(Message(role="user", content="What's the weather in NYC?"),),
            context="weather_assistant",
        )
        result = await node(weather_state)

        assert result.outcome == "tool_required"
        assert len(result.state.messages) == 2
        assert "check the weather" in result.state.messages[-1].content

    @staticmethod
    async def test_router_code_generation() -> None:
        """Test router identifies code generation intent and adjusts temperature."""
        node = LLMRouterNode()
        code_state = AgentState(
            messages=(Message(role="user", content="Help me write Python code"),),
            context="coding_assistant",
            temperature=0.7,
        )
        result = await node(code_state)

        assert result.outcome == "code_generation"
        assert result.state.temperature == 0.3  # Lowered for code generation
        assert "write code" in result.state.messages[-1].content

    @staticmethod
    async def test_router_direct_response() -> None:
        """Test router handles general queries."""
        node = LLMRouterNode()
        general_state = AgentState(
            messages=(Message(role="user", content="Tell me about history"),),
            context="assistant",
        )
        result = await node(general_state)

        assert result.outcome == "direct_response"
        assert "understand your request" in result.state.messages[-1].content
