"""A deliberately small, deterministic state-graph runtime.

This release adds state-driven conditional routing and explicit termination.
Reducers, parallel supersteps, and persistence remain intentionally absent so
the routing contract stays visible.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final, TypeAlias

State: TypeAlias = dict[str, object]
Node: TypeAlias = Callable[[Mapping[str, object]], Mapping[str, object]]
Route: TypeAlias = Callable[[Mapping[str, object]], str]

START: Final = "__start__"
END: Final = "__end__"


class GraphError(ValueError):
    """Raised when a graph is invalid or cannot make safe progress."""


@dataclass(frozen=True)
class Step:
    """One externally observable state transition and its chosen destination."""

    index: int
    node: str
    update: Mapping[str, object]
    state: Mapping[str, object]
    next_node: str


@dataclass(frozen=True)
class _ConditionalEdge:
    route: Route
    path_map: Mapping[str, str] | None

    def resolve(self, state: Mapping[str, object], *, source: str) -> str:
        label = self.route(dict(state))
        if not isinstance(label, str):
            raise GraphError(f"route from {source!r} must return a string")
        if self.path_map is None:
            return label
        try:
            return self.path_map[label]
        except KeyError as error:
            raise GraphError(f"unknown route {label!r} from node {source!r}") from error


class StateGraph:
    """Mutable graph builder that compiles into an immutable runnable graph."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, list[str]] = {}
        self._branches: dict[str, _ConditionalEdge] = {}

    def add_node(self, name: str, node: Node) -> StateGraph:
        if not name or name in {START, END}:
            raise GraphError(f"invalid node name: {name!r}")
        if name in self._nodes:
            raise GraphError(f"duplicate node: {name}")
        self._nodes[name] = node
        return self

    def add_edge(self, source: str, target: str) -> StateGraph:
        self._edges.setdefault(source, []).append(target)
        return self

    def add_conditional_edges(
        self,
        source: str,
        route: Route,
        path_map: Mapping[str, str] | None = None,
    ) -> StateGraph:
        """Choose a destination after ``source`` updates the state.

        Without ``path_map``, the route result is the destination node name.
        With a map, the route returns a stable label that is resolved to a node
        name or ``END``.
        """
        if source in self._branches:
            raise GraphError(f"duplicate conditional edge from node: {source}")
        self._branches[source] = _ConditionalEdge(
            route=route,
            path_map=dict(path_map) if path_map is not None else None,
        )
        return self

    def compile(self) -> CompiledGraph:
        if START not in self._edges:
            raise GraphError("graph has no START edge")
        if START in self._branches:
            raise GraphError("START cannot have conditional edges")

        allowed_sources = set(self._nodes) | {START}
        allowed_targets = set(self._nodes) | {END}
        for source, targets in self._edges.items():
            if source not in allowed_sources:
                raise GraphError(f"edge starts at unknown node: {source}")
            if len(targets) != 1:
                raise GraphError(f"node {source!r} must have exactly one outgoing edge")
            if targets[0] not in allowed_targets:
                raise GraphError(f"edge points to unknown node: {targets[0]}")

        entry = self._edges[START][0]
        if entry == END:
            raise GraphError("graph cannot end before running a node")

        for source, branch in self._branches.items():
            if source not in self._nodes:
                raise GraphError(f"conditional edge starts at unknown node: {source}")
            if branch.path_map is not None:
                for target in branch.path_map.values():
                    if target not in allowed_targets:
                        raise GraphError(f"conditional edge points to unknown node: {target}")

        for name in self._nodes:
            has_static = name in self._edges
            has_conditional = name in self._branches
            if has_static and has_conditional:
                raise GraphError(f"node has both static and conditional edges: {name}")
            if not has_static and not has_conditional:
                raise GraphError(f"node has no outgoing edge: {name}")

        return CompiledGraph(
            nodes=dict(self._nodes),
            edges={key: values[0] for key, values in self._edges.items()},
            branches=dict(self._branches),
        )


class CompiledGraph:
    """Validated graph with deterministic, copy-on-write state transitions."""

    def __init__(
        self,
        nodes: Mapping[str, Node],
        edges: Mapping[str, str],
        branches: Mapping[str, _ConditionalEdge],
    ) -> None:
        self._nodes = dict(nodes)
        self._edges = dict(edges)
        self._branches = dict(branches)

    def invoke(self, initial_state: Mapping[str, object], *, max_steps: int = 100) -> State:
        state = dict(initial_state)
        for step in self.stream(initial_state, max_steps=max_steps):
            state = dict(step.state)
        return state

    def stream(self, initial_state: Mapping[str, object], *, max_steps: int = 100) -> list[Step]:
        if max_steps < 1:
            raise GraphError("max_steps must be positive")
        state = dict(initial_state)
        current = self._edges[START]
        steps: list[Step] = []
        for index in range(1, max_steps + 1):
            update = dict(self._nodes[current](dict(state)))
            state.update(update)
            next_node = self._next_node(current, state)
            steps.append(
                Step(
                    index=index,
                    node=current,
                    update=update,
                    state=dict(state),
                    next_node=next_node,
                )
            )
            if next_node == END:
                return steps
            current = next_node
        raise GraphError(f"graph exceeded max_steps={max_steps}")

    def _next_node(self, source: str, state: Mapping[str, object]) -> str:
        if source in self._branches:
            target = self._branches[source].resolve(state, source=source)
        else:
            target = self._edges[source]
        if target == START:
            raise GraphError(f"route from {source!r} cannot target START")
        if target != END and target not in self._nodes:
            raise GraphError(f"route from {source!r} points to unknown node: {target!r}")
        return target
