"""Test error handling and edge cases for ClearFlow.

This module tests error conditions, edge cases, and validation logic
to ensure robust behavior in mission-critical scenarios.

"""

from dataclasses import dataclass, replace
from dataclasses import dataclass as dc
from typing import override

import pytest

from clearflow import Node, NodeResult, flow


@dataclass(frozen=True)
class SimpleState:
    """Simple typed state for testing."""

    test: str


@dataclass(frozen=True)
class ErrorState:
    """State for error handling tests."""

    simulate_error: bool
    error: str = ""
    response: str = ""
    handled: bool = False
    message: str = ""
    processed: bool = False


class TestErrorHandling:
    """Test error handling and edge cases."""

    @staticmethod
    async def test_missing_route() -> None:
        """Test that undefined routes raise an error."""

        @dc(frozen=True)
        class UnpredictableNode(Node[dict[str, str]]):
            """Node with variable outcomes."""

            name: str = "unpredictable"

            @override
            async def exec(self, state: dict[str, str]) -> NodeResult[dict[str, str]]:
                # Return an outcome that might not be routed
                outcome = state.get("force_outcome", "unexpected")
                return NodeResult(state, outcome=outcome)

        @dc(frozen=True)
        class TerminalNode(Node[dict[str, str]]):
            """Terminal node for expected outcome."""

            name: str = "terminal"

            @override
            async def exec(self, state: dict[str, str]) -> NodeResult[dict[str, str]]:
                return NodeResult(state, outcome="completed")

        unpredictable = UnpredictableNode()
        terminal = TerminalNode()

        # Flow with incomplete routing - unexpected outcome not routed
        incomplete_flow = (
            flow("IncompleteFlow", unpredictable).route(unpredictable, "expected", terminal).end(terminal, "completed")
            # "unexpected" outcome not routed - should raise error
        )

        # Should raise ValueError for unhandled outcome
        with pytest.raises(ValueError, match="No route defined for outcome 'unexpected' from node 'unpredictable'"):
            await incomplete_flow({"force_outcome": "unexpected"})

    @staticmethod
    async def test_empty_node_name() -> None:
        """Test that node names must be non-empty."""

        @dc(frozen=True)
        class BadNode(Node[SimpleState]):
            name: str = ""  # Empty name

            @override
            async def exec(self, state: SimpleState) -> NodeResult[SimpleState]:
                return NodeResult(state, outcome="done")

        with pytest.raises(ValueError, match="non-empty string"):
            BadNode()

        @dc(frozen=True)
        class WhitespaceNode(Node[SimpleState]):
            name: str = "   "  # Whitespace name

            @override
            async def exec(self, state: SimpleState) -> NodeResult[SimpleState]:
                return NodeResult(state, outcome="done")

        with pytest.raises(ValueError, match="non-empty string"):
            WhitespaceNode()

    @staticmethod
    async def test_node_with_valid_name() -> None:
        """Test that nodes must have explicit names."""

        @dc(frozen=True)
        class MyCustomNode(Node[SimpleState]):
            name: str = "custom_node"

            @override
            async def exec(self, state: SimpleState) -> NodeResult[SimpleState]:
                return NodeResult(state, outcome="done")

        # Node with explicit name
        node = MyCustomNode()
        assert node.name == "custom_node"

        # Override name in instantiation
        named_node = MyCustomNode(name="override_name")
        assert named_node.name == "override_name"

    @staticmethod
    async def test_single_node_flow() -> None:
        """Test a flow with a single node that terminates immediately."""

        @dataclass(frozen=True)
        class ProcessState:
            test: str
            processed: bool

        @dc(frozen=True)
        class StandaloneNode(Node[ProcessState]):
            name: str = "standalone"

            @override
            async def exec(self, state: ProcessState) -> NodeResult[ProcessState]:
                new_state = replace(state, processed=True)
                return NodeResult(new_state, outcome="complete")

        node = StandaloneNode()

        # Create flow with single node that terminates
        single_flow = flow("SingleNodeFlow", node).end(node, "complete")

        # Execute
        initial_state = ProcessState(test="value", processed=False)
        result = await single_flow(initial_state)
        assert result.outcome == "complete"
        assert result.state.test == "value"
        assert result.state.processed is True

    @staticmethod
    async def test_complex_error_flow() -> None:
        """Test error handling in AI workflows."""

        @dataclass(frozen=True)
        class LLMState:
            simulate_error: bool = False
            error: str = ""
            response: str = ""
            handled: bool = False
            message: str = ""
            processed: bool = False

        @dc(frozen=True)
        class LLMNode(Node[LLMState]):
            """Simulates LLM API that can fail."""

            name: str = "llm"

            @override
            async def exec(self, state: LLMState) -> NodeResult[LLMState]:
                if state.simulate_error:
                    error_state = replace(state, error="API timeout")
                    return NodeResult(error_state, outcome="error")
                success_state = replace(state, response="Generated text")
                return NodeResult(success_state, outcome="success")

        @dc(frozen=True)
        class ErrorHandler(Node[LLMState]):
            """Handles errors from LLM."""

            name: str = "error_handler"

            @override
            async def exec(self, state: LLMState) -> NodeResult[LLMState]:
                error = state.error or "Unknown error"
                new_state = replace(
                    state,
                    handled=True,
                    message=f"Error handled: {error}",
                )
                return NodeResult(new_state, outcome="handled")

        @dc(frozen=True)
        class SuccessHandler(Node[LLMState]):
            """Processes successful LLM responses."""

            name: str = "success_handler"

            @override
            async def exec(self, state: LLMState) -> NodeResult[LLMState]:
                new_state = replace(state, processed=True)
                return NodeResult(new_state, outcome="complete")

        llm = LLMNode()
        error_handler = ErrorHandler()
        success_handler = SuccessHandler()

        # Flow with error handling
        error_flow = (
            flow("ErrorHandlingFlow", llm)
            .route(llm, "error", error_handler)
            .route(llm, "success", success_handler)
            .end(error_handler, "handled")
            # Note: success_handler has a different termination, showcasing flexibility
        )

        # Test error path
        error_input = LLMState(simulate_error=True)
        error_result = await error_flow(error_input)
        assert error_result.outcome == "handled"
        assert error_result.state.handled is True
        assert "API timeout" in error_result.state.message
