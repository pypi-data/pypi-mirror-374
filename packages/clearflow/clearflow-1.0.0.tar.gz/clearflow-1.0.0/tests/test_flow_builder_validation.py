"""Test flow builder validation for reachability and duplicate routes.

This module tests that the flow builder enforces:
1. Nodes can only be routed from if reachable from start
2. Routes cannot be duplicated
3. Termination nodes must be reachable

"""

from dataclasses import dataclass
from typing import override

import pytest

from clearflow import Node, NodeResult, flow


@dataclass(frozen=True)
class SimpleState:
    """Simple state for testing."""

    value: str


@dataclass(frozen=True)
class SimpleNode(Node[SimpleState]):
    """Basic node for testing."""

    name: str

    @override
    async def exec(self, state: SimpleState) -> NodeResult[SimpleState]:
        return NodeResult(state, outcome="done")


class TestReachabilityValidation:
    """Test that nodes must be reachable to be used."""

    @staticmethod
    async def test_valid_linear_flow() -> None:
        """Test that a properly connected linear flow works."""
        start = SimpleNode(name="start")
        middle = SimpleNode(name="middle")
        end = SimpleNode(name="end")

        # This should work - all nodes are reachable
        valid_flow = flow("ValidFlow", start).route(start, "done", middle).route(middle, "done", end).end(end, "done")

        result = await valid_flow(SimpleState("test"))
        assert result.state.value == "test"

    @staticmethod
    async def test_valid_branching_flow() -> None:
        """Test that branching flows work when all nodes are reachable."""
        branch_a = SimpleNode(name="branch_a")
        branch_b = SimpleNode(name="branch_b")
        final = SimpleNode(name="final")

        @dataclass(frozen=True)
        class BranchingNode(Node[SimpleState]):
            name: str = "start"

            @override
            async def exec(self, state: SimpleState) -> NodeResult[SimpleState]:
                if state.value == "a":
                    return NodeResult(state, outcome="path_a")
                return NodeResult(state, outcome="path_b")

        start_branching = BranchingNode()

        # All branches properly connected
        branching_flow = (
            flow("BranchingFlow", start_branching)
            .route(start_branching, "path_a", branch_a)
            .route(start_branching, "path_b", branch_b)
            .route(branch_a, "done", final)
            .route(branch_b, "done", final)
            .end(final, "done")
        )

        result = await branching_flow(SimpleState("a"))
        assert result.state.value == "a"

    @staticmethod
    def test_routing_from_unreachable_node() -> None:
        """Test that routing from an unreachable node raises an error."""
        start = SimpleNode(name="start")
        orphan = SimpleNode(name="orphan")
        end = SimpleNode(name="end")

        # This should fail - orphan is never routed to
        with pytest.raises(ValueError, match="Cannot route from 'orphan' - not reachable"):
            flow("InvalidFlow", start).route(orphan, "done", end).end(end, "done")

    @staticmethod
    def test_ending_at_unreachable_node() -> None:
        """Test that ending at an unreachable node raises an error."""
        start = SimpleNode(name="start")
        middle = SimpleNode(name="middle")
        unreachable_end = SimpleNode(name="unreachable_end")

        # This should fail - unreachable_end is never routed to
        with pytest.raises(ValueError, match="Cannot end at 'unreachable_end' - not reachable"):
            flow("InvalidFlow", start).route(start, "done", middle).end(unreachable_end, "done")

    @staticmethod
    def test_disconnected_subgraph() -> None:
        """Test that disconnected subgraphs are detected."""
        start = SimpleNode(name="start")
        middle = SimpleNode(name="middle")

        # Create disconnected nodes
        island1 = SimpleNode(name="island1")
        island2 = SimpleNode(name="island2")

        # This should fail - island1 is not reachable from start
        with pytest.raises(ValueError, match="Cannot route from 'island1' - not reachable"):
            (
                flow("DisconnectedFlow", start)
                .route(start, "done", middle)
                .route(island1, "done", island2)  # Disconnected subgraph!
                .end(middle, "done")
            )

    @staticmethod
    def test_complex_reachability() -> None:
        """Test reachability with more complex routing patterns."""
        start = SimpleNode(name="start")
        a = SimpleNode(name="a")
        b = SimpleNode(name="b")
        c = SimpleNode(name="c")
        d = SimpleNode(name="d")

        # Build a flow where d is only reachable through a specific path
        complex_flow = (
            flow("ComplexFlow", start)
            .route(start, "to_a", a)
            .route(start, "to_b", b)
            .route(a, "to_c", c)
            .route(c, "to_d", d)
            # b can also go to d - this should work since d is reachable via a->c->d
            .route(b, "to_d", d)
            .end(d, "done")
        )

        # This should work - all nodes are properly connected
        assert complex_flow is not None


class TestDuplicateRouteDetection:
    """Test that duplicate routes are detected and prevented."""

    @staticmethod
    def test_duplicate_route_same_outcome() -> None:
        """Test that defining the same route twice raises an error."""
        start = SimpleNode(name="start")
        option1 = SimpleNode(name="option1")
        option2 = SimpleNode(name="option2")

        # This should fail - can't route "done" from start twice
        with pytest.raises(ValueError, match="Route already defined for outcome 'done' from node 'start'"):
            (
                flow("DuplicateRoute", start).route(start, "done", option1).route(start, "done", option2)  # Duplicate!
            )

    @staticmethod
    def test_same_outcome_different_nodes_allowed() -> None:
        """Test that same outcome from different nodes is allowed."""
        start = SimpleNode(name="start")
        middle1 = SimpleNode(name="middle1")
        middle2 = SimpleNode(name="middle2")
        end = SimpleNode(name="end")

        # This should work - same outcome but from different nodes
        valid_flow = (
            flow("ValidSameOutcome", start)
            .route(start, "path1", middle1)
            .route(start, "path2", middle2)
            .route(middle1, "done", end)  # "done" from middle1
            .route(middle2, "done", end)  # "done" from middle2 - OK!
            .end(end, "done")
        )

        assert valid_flow is not None

    @staticmethod
    def test_duplicate_termination_route() -> None:
        """Test that trying to add a route that conflicts with termination fails."""
        start = SimpleNode(name="start")
        middle = SimpleNode(name="middle")
        end = SimpleNode(name="end")

        # Try to route and terminate with the same outcome from same node
        with pytest.raises(ValueError, match="Route already defined for outcome 'done' from node 'end'"):
            (
                flow("DuplicateTermination", start)
                .route(start, "done", end)
                .route(end, "done", middle)  # First route from end
                .end(end, "done")  # Can't terminate with same outcome!
            )

    @staticmethod
    def test_route_then_terminate_same_outcome() -> None:
        """Test that routing and terminating with same outcome fails."""
        start = SimpleNode(name="start")
        middle = SimpleNode(name="middle")

        # This should fail - can't have both route and termination for same outcome
        with pytest.raises(ValueError, match="Route already defined for outcome 'done' from node 'middle'"):
            (
                flow("RouteAndTerminate", start)
                .route(start, "done", middle)
                .route(middle, "done", start)  # Creates a loop
                .end(middle, "done")  # Same outcome as the route above!
            )

    @staticmethod
    async def test_multiple_outcomes_single_node() -> None:
        """Test that a node can have multiple different outcomes."""

        @dataclass(frozen=True)
        class MultiOutcomeNode(Node[SimpleState]):
            name: str = "multi"

            @override
            async def exec(self, state: SimpleState) -> NodeResult[SimpleState]:
                if state.value == "error":
                    return NodeResult(state, outcome="error")
                if state.value == "retry":
                    return NodeResult(state, outcome="retry")
                return NodeResult(state, outcome="success")

        multi = MultiOutcomeNode()
        error_handler = SimpleNode(name="error_handler")
        retry_handler = SimpleNode(name="retry_handler")
        success_handler = SimpleNode(name="success_handler")

        # This should work - different outcomes from same node
        multi_flow = (
            flow("MultiOutcome", multi)
            .route(multi, "error", error_handler)
            .route(multi, "retry", retry_handler)
            .route(multi, "success", success_handler)
            .end(error_handler, "done")
            # Note: other handlers not terminated for this test
        )

        result = await multi_flow(SimpleState("error"))
        assert result.state.value == "error"
