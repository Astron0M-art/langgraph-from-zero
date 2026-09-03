"""A small deterministic state graph with typed update contracts.

State schemas now define allowed keys, required inputs, runtime value checks,
and optional reducers. Parallel scheduling is deliberately still absent; an
explicit update-batch seam makes merge and conflict semantics testable first.
"""

from __future__ import annotations

import types
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from inspect import Parameter, signature
from typing import (
    Annotated,
    Any,
    Final,
    Literal,
    NotRequired,
    Required,
    TypeAlias,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

State: TypeAlias = dict[str, object]
Node: TypeAlias = Callable[[Mapping[str, object]], Mapping[str, object]]
Route: TypeAlias = Callable[[Mapping[str, object]], str]
Reducer: TypeAlias = Callable[[object, object], object]

START: Final = "__start__"
END: Final = "__end__"


class GraphError(ValueError):
    """Raised when a graph or state update violates the teaching runtime contract."""


@dataclass(frozen=True)
class Step:
    """One externally observable transition after reducer application."""

    index: int
    node: str
    update: Mapping[str, object]
    state: Mapping[str, object]
    next_node: str


@dataclass(frozen=True)
class _StateField:
    value_type: object
    reducer: Reducer | None


@dataclass(frozen=True)
class _StateSpec:
    fields: Mapping[str, _StateField] | None
    required_keys: frozenset[str]

    @classmethod
    def from_schema(cls, schema: type[object] | None) -> _StateSpec:
        if schema is None:
            return cls(fields=None, required_keys=frozenset())
        try:
            hints = get_type_hints(schema, include_extras=True)
        except (NameError, TypeError) as error:
            raise GraphError(f"cannot inspect state schema {schema!r}") from error
        if not hints:
            raise GraphError("state schema must declare at least one field")

        declared_required = set(getattr(schema, "__required_keys__", hints.keys()))
        required = frozenset(
            key
            for key, annotation in hints.items()
            if get_origin(annotation) is Required
            or (get_origin(annotation) is not NotRequired and key in declared_required)
        )
        fields = {key: _field_from_annotation(key, annotation) for key, annotation in hints.items()}
        return cls(fields=fields, required_keys=required)

    def validate_initial(self, state: Mapping[str, object]) -> State:
        result = dict(state)
        if self.fields is None:
            return result
        unknown = set(result) - set(self.fields)
        if unknown:
            raise GraphError(f"state contains unknown keys: {sorted(unknown)!r}")
        missing = set(self.required_keys) - set(result)
        if missing:
            raise GraphError(f"state is missing required keys: {sorted(missing)!r}")
        for key, value in result.items():
            _validate_value(key, value, self.fields[key].value_type)
        return result

    def merge(self, state: Mapping[str, object], updates: Sequence[Mapping[str, object]]) -> State:
        result = dict(state)
        grouped: dict[str, list[object]] = {}
        for update in updates:
            for key, value in update.items():
                if self.fields is not None and key not in self.fields:
                    raise GraphError(f"update contains unknown state key: {key!r}")
                grouped.setdefault(key, []).append(value)

        for key, values in grouped.items():
            field = self.fields[key] if self.fields is not None else None
            reducer = field.reducer if field is not None else None
            if len(values) > 1 and reducer is None:
                raise GraphError(
                    f"conflicting updates for state key {key!r}: "
                    f"received {len(values)} values without a reducer"
                )
            if reducer is None:
                value = values[0]
            else:
                if key not in result:
                    raise GraphError(f"reducer state key {key!r} must be initialized")
                value = result[key]
                for update_value in values:
                    try:
                        value = reducer(value, update_value)
                    except Exception as error:
                        raise GraphError(f"reducer failed for state key {key!r}") from error
            if field is not None:
                _validate_value(key, value, field.value_type)
            result[key] = value
        return result


def _field_from_annotation(key: str, annotation: object) -> _StateField:
    if get_origin(annotation) in {Required, NotRequired}:
        annotation = get_args(annotation)[0]

    reducer: Reducer | None = None
    if get_origin(annotation) is Annotated:
        value_type, *metadata = get_args(annotation)
        annotation = value_type
        if metadata and callable(metadata[-1]):
            candidate = metadata[-1]
            try:
                positional = [
                    parameter
                    for parameter in signature(candidate).parameters.values()
                    if parameter.kind
                    in {Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD}
                ]
            except (TypeError, ValueError) as error:
                raise GraphError(f"cannot inspect reducer for state key {key!r}") from error
            if len(positional) != 2:
                raise GraphError(
                    f"invalid reducer for state key {key!r}: expected (current, update)"
                )
            reducer = cast(Reducer, candidate)
    return _StateField(value_type=annotation, reducer=reducer)


def _validate_value(key: str, value: object, expected: object) -> None:
    if not _matches_type(value, expected):
        raise GraphError(
            f"invalid value for state key {key!r}: "
            f"expected {_type_name(expected)}, got {type(value).__name__}"
        )


def _matches_type(value: object, expected: object) -> bool:
    if expected in {Any, object}:
        return True
    origin = get_origin(expected)
    args = get_args(expected)
    if origin in {Union, types.UnionType}:
        return any(_matches_type(value, option) for option in args)
    if origin is Literal:
        return value in args
    if origin is list:
        return isinstance(value, list) and (
            not args or all(_matches_type(item, args[0]) for item in value)
        )
    if origin is set:
        return isinstance(value, set) and (
            not args or all(_matches_type(item, args[0]) for item in value)
        )
    if origin is dict:
        return isinstance(value, dict) and (
            len(args) != 2
            or all(
                _matches_type(item_key, args[0]) and _matches_type(item_value, args[1])
                for item_key, item_value in value.items()
            )
        )
    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        if not args:
            return True
        if len(args) == 2 and args[1] is Ellipsis:
            return all(_matches_type(item, args[0]) for item in value)
        return len(value) == len(args) and all(
            _matches_type(item, item_type) for item, item_type in zip(value, args, strict=True)
        )
    runtime_type = origin or expected
    return isinstance(runtime_type, type) and isinstance(value, runtime_type)


def _type_name(expected: object) -> str:
    if get_origin(expected) is None:
        return getattr(expected, "__name__", str(expected).replace("typing.", ""))
    return str(expected).replace("typing.", "")


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
    """Mutable graph builder with an optional TypedDict-style state schema."""

    def __init__(self, state_schema: type[object] | None = None) -> None:
        self._state_spec = _StateSpec.from_schema(state_schema)
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
        """Choose a validated destination after a node's update is reduced."""
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
            state_spec=self._state_spec,
        )


class CompiledGraph:
    """Validated graph with deterministic reducer-backed state transitions."""

    def __init__(
        self,
        nodes: Mapping[str, Node],
        edges: Mapping[str, str],
        branches: Mapping[str, _ConditionalEdge],
        state_spec: _StateSpec,
    ) -> None:
        self._nodes = dict(nodes)
        self._edges = dict(edges)
        self._branches = dict(branches)
        self._state_spec = state_spec

    def invoke(self, initial_state: Mapping[str, object], *, max_steps: int = 100) -> State:
        state = self._state_spec.validate_initial(initial_state)
        for step in self.stream(initial_state, max_steps=max_steps):
            state = dict(step.state)
        return state

    def stream(self, initial_state: Mapping[str, object], *, max_steps: int = 100) -> list[Step]:
        if max_steps < 1:
            raise GraphError("max_steps must be positive")
        state = self._state_spec.validate_initial(initial_state)
        current = self._edges[START]
        steps: list[Step] = []
        for index in range(1, max_steps + 1):
            update = dict(self._nodes[current](dict(state)))
            state = self._state_spec.merge(state, [update])
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

    def merge_updates(
        self,
        state: Mapping[str, object],
        updates: Sequence[Mapping[str, object]],
    ) -> State:
        """Apply one ordered update batch without scheduling nodes.

        This teaching seam makes reducer and conflict semantics observable
        before a later release adds supersteps and parallel scheduling.
        """
        validated = self._state_spec.validate_initial(state)
        return self._state_spec.merge(validated, updates)

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
