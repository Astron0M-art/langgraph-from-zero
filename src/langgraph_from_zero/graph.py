"""A deliberately small, deterministic state-graph runtime.

This first teaching release supports one outgoing edge per node. Conditional
routing, reducers, parallel supersteps, and persistence are added later so the
reason for each abstraction remains visible.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final, TypeAlias

State: TypeAlias = dict[str, object]
Node: TypeAlias = Callable[[Mapping[str, object]], Mapping[str, object]]

START: Final = "__start__"
END: Final = "__end__"


class GraphError(ValueError):
    """Raised when a graph is invalid or cannot make safe progress."""


@dataclass(frozen=True)
class Step:
    """One externally observable state transition."""

    index: int
    node: str
    update: Mapping[str, object]
    state: Mapping[str, object]


class StateGraph:
    """Mutable graph builder that compiles into an immutable runnable graph."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, list[str]] = {}

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

    def compile(self) -> CompiledGraph:
        if START not in self._edges:
            raise GraphError("graph has no START edge")
        allowed = set(self._nodes) | {START, END}
        for source, targets in self._edges.items():
            if source not in allowed:
                raise GraphError(f"edge starts at unknown node: {source}")
            if len(targets) != 1:
                raise GraphError(f"node {source!r} must have exactly one outgoing edge")
            if targets[0] not in allowed:
                raise GraphError(f"edge points to unknown node: {targets[0]}")
        entry = self._edges[START][0]
        if entry == END:
            raise GraphError("graph cannot end before running a node")
        for name in self._nodes:
            if name not in self._edges:
                raise GraphError(f"node has no outgoing edge: {name}")
        return CompiledGraph(
            dict(self._nodes), {key: values[0] for key, values in self._edges.items()}
        )


class CompiledGraph:
    """Validated graph with deterministic, copy-on-write state transitions."""

    def __init__(self, nodes: Mapping[str, Node], edges: Mapping[str, str]) -> None:
        self._nodes = dict(nodes)
        self._edges = dict(edges)

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
            steps.append(Step(index=index, node=current, update=update, state=dict(state)))
            current = self._edges[current]
            if current == END:
                return steps
        raise GraphError(f"graph exceeded max_steps={max_steps}")
