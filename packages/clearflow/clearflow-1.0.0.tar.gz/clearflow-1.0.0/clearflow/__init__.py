"""ClearFlow: Zero-dependency async workflow orchestration framework.

Provides type-safe workflow composition with explicit routing and single termination.
Built for mission-critical AI orchestration.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, cast, final, override

__all__ = [
    "Node",
    "NodeResult",
    "flow",
]

RouteKey = tuple[str, str]  # (node_name, outcome)


class NodeBase(Protocol):
    """Non-generic base protocol for all nodes.

    Provides the common interface without type parameters,
    allowing heterogeneous collections of nodes.
    """

    name: str

    async def __call__(
        self,
        state: object,  # clearflow: ignore[ARCH009]  # Type erasure needed for heterogeneous collections
    ) -> "NodeResult[object]":  # clearflow: ignore[ARCH009]  # Type erasure needed for heterogeneous collections
        """Execute the node with any state type."""
        ...


@final
@dataclass(frozen=True)
class NodeResult[T]:
    """Result of node execution.

    Attributes:
        state: The transformed state from node execution.
        outcome: The routing outcome determining next node.

    """

    state: T
    outcome: str


@dataclass(frozen=True, kw_only=True)
class Node[TIn, TOut = TIn](ABC, NodeBase):
    """Abstract base for workflow nodes.

    Subclass and implement async exec() to process state and return outcomes for routing.
    Supports optional prep() and post() hooks for setup and cleanup.

    Type parameters:
        TIn: Input state type
        TOut: Output state type (defaults to TIn for non-transforming nodes)

    """

    name: str

    def __post_init__(self) -> None:
        """Validate node configuration after initialization.

        Raises:
            ValueError: If node name is empty or contains only whitespace.

        """
        if not self.name or not self.name.strip():
            msg = f"Node name must be a non-empty string, got: {self.name!r}"
            raise ValueError(msg)

    @override
    async def __call__(self, state: TIn) -> NodeResult[TOut]:  # pyright: ignore[reportIncompatibleMethodOverride]  # NodeBase uses object for type erasure but Node preserves type safety
        """Execute node lifecycle.

        Returns:
            NodeResult containing transformed state and routing outcome.

        """
        state = await self.prep(state)
        result = await self.exec(state)
        return await self.post(result)

    async def prep(self, state: TIn) -> TIn:  # noqa: PLR6301  # Template method hook for subclasses
        """Pre-execution hook.

        Returns:
            State passed through unchanged by default.

        """
        return state

    @abstractmethod
    async def exec(self, state: TIn) -> NodeResult[TOut]:
        """Execute main node logic - must be implemented by subclasses."""
        ...

    async def post(self, result: NodeResult[TOut]) -> NodeResult[TOut]:  # noqa: PLR6301  # Template method hook for subclasses
        """Post-execution hook.

        Returns:
            Result passed through unchanged by default.

        """
        return result


@final
@dataclass(frozen=True, kw_only=True)
class _Flow[TStartIn, TEndOut = TStartIn](Node[TStartIn, TEndOut]):
    """Internal flow implementation that transforms TStartIn to TEndOut.

    Implementation note: We use 'object' for node types internally because
    Python's type system cannot track types through runtime-determined paths.
    Type safety is maintained at the public API boundaries - exec() guarantees
    TStartIn→TEndOut transformation through construction-time validation.
    """

    start: NodeBase
    routes: Mapping[RouteKey, NodeBase | None]

    @override
    async def exec(self, state: TStartIn) -> NodeResult[TEndOut]:
        """Execute the flow by routing through nodes based on outcomes.

        Returns:
            Final node result containing transformed state and None outcome.

        Raises:
            ValueError: If no route is defined for an outcome from a node.

        """
        current_node = self.start
        current_state: object = state  # clearflow: ignore[ARCH009]  # Type erasure needed for dynamic routing

        while True:
            # Execute node
            result = await current_node(current_state)
            key = (current_node.name, result.outcome)

            # Raise error if no route defined - all outcomes must be explicitly handled
            if key not in self.routes:
                msg = f"No route defined for outcome '{result.outcome}' from node '{current_node.name}'"
                raise ValueError(msg)

            # Check next node
            next_node = self.routes[key]
            if next_node is None:
                return cast("NodeResult[TEndOut]", result)

            # Continue
            current_node = next_node
            current_state = result.state


@final
@dataclass(frozen=True, kw_only=True)
class _FlowBuilder[TStartIn, TStartOut]:
    """Flow builder for composing node routes.

    Type parameters:
        TStartIn: The input type the flow accepts (from start node)
        TStartOut: The output type of the start node

    Call end() to specify where the flow ends and get the completed flow.
    """

    _name: str
    _start: Node[TStartIn, TStartOut]
    _routes: MappingProxyType[RouteKey, NodeBase | None]
    _reachable: frozenset[str]  # Node names that are reachable from start

    def _validate_and_create_route(
        self, from_node: NodeBase, outcome: str, *, is_termination: bool = False
    ) -> RouteKey:
        """Validate that a route can be added from the given node.

        Args:
            from_node: The node to route from
            outcome: The outcome that triggers this route
            is_termination: Whether this is a termination route

        Returns:
            The route key for this route

        Raises:
            ValueError: If from_node is not reachable or route already exists

        """
        # Check reachability
        if from_node.name not in self._reachable:
            action = "end at" if is_termination else "route from"
            msg = f"Cannot {action} '{from_node.name}' - not reachable from start"
            raise ValueError(msg)

        # Check for duplicate routes
        route_key: RouteKey = (from_node.name, outcome)
        if route_key in self._routes:
            msg = f"Route already defined for outcome '{outcome}' from node '{from_node.name}'"
            raise ValueError(msg)

        return route_key

    def route(
        self,
        from_node: NodeBase,
        outcome: str,
        to_node: NodeBase,
    ) -> "_FlowBuilder[TStartIn, TStartOut]":
        """Connect nodes: from_node --outcome--> to_node.

        Args:
            from_node: Source node
            outcome: Outcome that triggers this route
            to_node: Destination node (use end() for flow completion)

        Returns:
            Builder for continued route definition and flow completion

        Raises:
            ValueError: If from_node is not reachable or route already exists

        """
        route_key = self._validate_and_create_route(from_node, outcome)

        # Add route and mark to_node as reachable
        new_routes = {**self._routes, route_key: to_node}
        new_reachable = self._reachable | {to_node.name}

        return _FlowBuilder[TStartIn, TStartOut](
            _name=self._name,
            _start=self._start,
            _routes=MappingProxyType(new_routes),
            _reachable=new_reachable,
        )

    def end[TEndIn, TEndOut](
        self,
        end: Node[TEndIn, TEndOut],
        outcome: str,
    ) -> Node[TStartIn, TEndOut]:
        """End the flow at the specified node and outcome.

        This completes the flow definition by specifying where it ends.
        The flow's output type is determined by the final node's output type.

        Args:
            end: The node where the flow ends
            outcome: The outcome from this node that completes the flow

        Returns:
            A flow node that transforms TStartIn to TEndOut

        Raises:
            ValueError: If end node is not reachable or route already exists

        """
        route_key = self._validate_and_create_route(end, outcome, is_termination=True)

        new_routes = {**self._routes, route_key: None}

        return _Flow[TStartIn, TEndOut](
            name=self._name,
            start=self._start,
            routes=MappingProxyType(new_routes),
        )


def flow[TStartIn, TStartOut](
    name: str,
    start: Node[TStartIn, TStartOut],
) -> _FlowBuilder[TStartIn, TStartOut]:
    """Create a flow with the given name and starting node.

    Args:
        name: The name of the flow
        start: The starting node that accepts TStartIn and outputs TStartOut

    Returns:
        Builder for route definition and flow completion

    """
    return _FlowBuilder[TStartIn, TStartOut](
        _name=name,
        _start=start,
        _routes=MappingProxyType({}),
        _reachable=frozenset({start.name}),  # Start node is always reachable
    )
