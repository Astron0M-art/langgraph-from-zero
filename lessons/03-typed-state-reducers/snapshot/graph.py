"""Frozen v0.3.0 snapshot: typed state, reducers, and update conflicts."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import (
    Annotated,
    Any,
    NotRequired,
    Required,
    TypedDict,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

START = "__start__"
END = "__end__"
Node = Callable[[Mapping[str, object]], Mapping[str, object]]
Route = Callable[[Mapping[str, object]], str]
Reducer = Callable[[object, object], object]


class GraphError(ValueError):
    pass


class StateSpec:
    def __init__(self, schema: type[object]) -> None:
        hints = get_type_hints(schema, include_extras=True)
        declared_required = set(getattr(schema, "__required_keys__", hints))
        self.required = {
            key
            for key, annotation in hints.items()
            if get_origin(annotation) is Required
            or (get_origin(annotation) is not NotRequired and key in declared_required)
        }
        self.fields: dict[str, tuple[object, Reducer | None]] = {}
        for key, annotation in hints.items():
            if get_origin(annotation) in {Required, NotRequired}:
                annotation = get_args(annotation)[0]
            reducer = None
            if get_origin(annotation) is Annotated:
                annotation, *metadata = get_args(annotation)
                if metadata and callable(metadata[-1]):
                    reducer = metadata[-1]
            self.fields[key] = (annotation, reducer)

    def validate(self, state: Mapping[str, object]) -> dict[str, object]:
        unknown = set(state) - set(self.fields)
        if unknown:
            raise GraphError(f"unknown state keys: {sorted(unknown)!r}")
        missing = self.required - set(state)
        if missing:
            raise GraphError(f"missing required state keys: {sorted(missing)!r}")
        result = dict(state)
        for key, value in result.items():
            self._check_type(key, value)
        return result

    def merge(
        self,
        state: Mapping[str, object],
        updates: Sequence[Mapping[str, object]],
    ) -> dict[str, object]:
        result = dict(state)
        grouped: dict[str, list[object]] = {}
        for update in updates:
            for key, value in update.items():
                if key not in self.fields:
                    raise GraphError(f"unknown update key: {key!r}")
                grouped.setdefault(key, []).append(value)

        for key, values in grouped.items():
            _, reducer = self.fields[key]
            if len(values) > 1 and reducer is None:
                raise GraphError(f"conflicting updates for {key!r} without a reducer")
            if reducer is None:
                value = values[0]
            else:
                if key not in result:
                    raise GraphError(f"reducer key {key!r} must be initialized")
                value = result[key]
                for update in values:
                    value = reducer(value, update)
            self._check_type(key, value)
            result[key] = value
        return result

    def _check_type(self, key: str, value: object) -> None:
        expected, _ = self.fields[key]
        origin = get_origin(expected)
        if expected is Any:
            return
        if origin is list:
            args = get_args(expected)
            valid = isinstance(value, list) and (
                not args or all(isinstance(item, args[0]) for item in value)
            )
        else:
            valid = isinstance(expected, type) and isinstance(value, expected)
        if not valid:
            raise GraphError(f"invalid type for state key {key!r}")


class StateGraph:
    def __init__(self, state_schema: type[object]) -> None:
        self.spec = StateSpec(state_schema)
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, str] = {}
        self.branches: dict[str, tuple[Route, dict[str, str]]] = {}

    def add_node(self, name: str, node: Node) -> None:
        if name in self.nodes or name in {START, END}:
            raise GraphError(f"invalid or duplicate node: {name}")
        self.nodes[name] = node

    def add_edge(self, source: str, target: str) -> None:
        if source in self.edges:
            raise GraphError(f"duplicate static edge from: {source}")
        self.edges[source] = target

    def add_conditional_edges(self, source: str, route: Route, path_map: Mapping[str, str]) -> None:
        self.branches[source] = (route, dict(path_map))

    def compile(self) -> CompiledGraph:
        if START not in self.edges:
            raise GraphError("graph has no START edge")
        targets = set(self.nodes) | {END}
        for source, target in self.edges.items():
            if source not in set(self.nodes) | {START} or target not in targets:
                raise GraphError("static edge references an unknown node")
        for source, (_, path_map) in self.branches.items():
            if source not in self.nodes or any(
                target not in targets for target in path_map.values()
            ):
                raise GraphError("conditional edge references an unknown node")
        for name in self.nodes:
            if int(name in self.edges) + int(name in self.branches) != 1:
                raise GraphError(f"node {name!r} needs one outgoing edge")
        return CompiledGraph(self.spec, self.nodes, self.edges, self.branches)


class CompiledGraph:
    def __init__(
        self,
        spec: StateSpec,
        nodes: Mapping[str, Node],
        edges: Mapping[str, str],
        branches: Mapping[str, tuple[Route, dict[str, str]]],
    ) -> None:
        self.spec = spec
        self.nodes = dict(nodes)
        self.edges = dict(edges)
        self.branches = dict(branches)

    def merge_updates(
        self,
        state: Mapping[str, object],
        updates: Sequence[Mapping[str, object]],
    ) -> dict[str, object]:
        return self.spec.merge(self.spec.validate(state), updates)

    def run(
        self, initial: Mapping[str, object], max_steps: int = 100
    ) -> tuple[dict[str, object], list[str]]:
        state = self.spec.validate(initial)
        node_name = self.edges[START]
        trace: list[str] = []
        for _ in range(max_steps):
            update = dict(self.nodes[node_name](dict(state)))
            state = self.spec.merge(state, [update])
            next_node = self._next(node_name, state)
            trace.append(f"node={node_name} update={update!r} state={state!r} next={next_node}")
            if next_node == END:
                return state, trace
            node_name = next_node
        raise GraphError(f"graph exceeded max_steps={max_steps}")

    def _next(self, source: str, state: Mapping[str, object]) -> str:
        if source not in self.branches:
            return self.edges[source]
        route, path_map = self.branches[source]
        label = route(dict(state))
        if label not in path_map:
            raise GraphError(f"unknown route {label!r}")
        return path_map[label]


def append_evidence(current: list[str], update: list[str]) -> list[str]:
    return [*current, *update]


class ResearchState(TypedDict):
    evidence_needed: int
    evidence: Annotated[list[str], append_evidence]
    verdict: NotRequired[str]


def build_demo() -> CompiledGraph:
    graph = StateGraph(ResearchState)

    def collect(state: Mapping[str, object]) -> dict[str, object]:
        evidence = cast(list[str], state["evidence"])
        return {"evidence": [f"source-{len(evidence) + 1}"]}

    def review(state: Mapping[str, object]) -> dict[str, object]:
        evidence = cast(list[str], state["evidence"])
        return {"verdict": f"reviewed {len(evidence)} items"}

    def route(state: Mapping[str, object]) -> str:
        evidence = cast(list[str], state["evidence"])
        needed = cast(int, state["evidence_needed"])
        return "continue" if len(evidence) < needed else "review"

    graph.add_node("collect", collect)
    graph.add_node("review", review)
    graph.add_edge(START, "collect")
    graph.add_conditional_edges(
        "collect",
        route,
        {"continue": "collect", "review": "review"},
    )
    graph.add_edge("review", END)
    return graph.compile()


if __name__ == "__main__":
    final_state, steps = build_demo().run({"evidence_needed": 2, "evidence": []})
    print("\n".join(steps))
    print(f"final={final_state!r}")
