"""Frozen v0.2.0 snapshot: conditional routing and bounded loops."""

from __future__ import annotations

from collections.abc import Callable, Mapping

START = "__start__"
END = "__end__"
Node = Callable[[Mapping[str, object]], Mapping[str, object]]
Route = Callable[[Mapping[str, object]], str]


class GraphError(ValueError):
    pass


class StateGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, str] = {}
        self.branches: dict[str, tuple[Route, dict[str, str] | None]] = {}

    def add_node(self, name: str, node: Node) -> None:
        if name in self.nodes or name in {START, END}:
            raise GraphError(f"invalid or duplicate node: {name}")
        self.nodes[name] = node

    def add_edge(self, source: str, target: str) -> None:
        if source in self.edges:
            raise GraphError(f"duplicate static edge from: {source}")
        self.edges[source] = target

    def add_conditional_edges(
        self, source: str, route: Route, path_map: Mapping[str, str] | None = None
    ) -> None:
        if source in self.branches:
            raise GraphError(f"duplicate conditional edge from: {source}")
        self.branches[source] = (route, dict(path_map) if path_map is not None else None)

    def compile(self) -> CompiledGraph:
        if START not in self.edges:
            raise GraphError("graph has no START edge")
        targets = set(self.nodes) | {END}
        for source, target in self.edges.items():
            if source not in set(self.nodes) | {START} or target not in targets:
                raise GraphError("static edge references an unknown node")
        for source, (_, path_map) in self.branches.items():
            if source not in self.nodes:
                raise GraphError("conditional edge starts at an unknown node")
            if path_map is not None and any(target not in targets for target in path_map.values()):
                raise GraphError("conditional edge targets an unknown node")
        for name in self.nodes:
            outgoing = int(name in self.edges) + int(name in self.branches)
            if outgoing != 1:
                raise GraphError(f"node {name!r} needs one static or conditional edge")
        return CompiledGraph(self.nodes, self.edges, self.branches)


class CompiledGraph:
    def __init__(
        self,
        nodes: Mapping[str, Node],
        edges: Mapping[str, str],
        branches: Mapping[str, tuple[Route, dict[str, str] | None]],
    ) -> None:
        self.nodes = dict(nodes)
        self.edges = dict(edges)
        self.branches = dict(branches)

    def run(
        self, initial: Mapping[str, object], max_steps: int = 100
    ) -> tuple[dict[str, object], list[str]]:
        state = dict(initial)
        node_name = self.edges[START]
        trace: list[str] = []
        for _ in range(max_steps):
            update = dict(self.nodes[node_name](dict(state)))
            state.update(update)
            next_node = self._next(node_name, state)
            trace.append(f"node={node_name} update={update!r} next={next_node}")
            if next_node == END:
                return state, trace
            node_name = next_node
        raise GraphError(f"graph exceeded max_steps={max_steps}")

    def _next(self, source: str, state: Mapping[str, object]) -> str:
        if source not in self.branches:
            return self.edges[source]
        route, path_map = self.branches[source]
        label = route(dict(state))
        if path_map is not None:
            if label not in path_map:
                raise GraphError(f"unknown route {label!r} from node {source!r}")
            target = path_map[label]
        else:
            target = label
        if target != END and target not in self.nodes:
            raise GraphError(f"route targets unknown node: {target!r}")
        return target


def build_demo() -> CompiledGraph:
    graph = StateGraph()
    graph.add_node(
        "collect", lambda state: {"evidence_collected": int(state.get("evidence_collected", 0)) + 1}
    )
    graph.add_node(
        "review", lambda state: {"verdict": f"reviewed {state['evidence_collected']} items"}
    )
    graph.add_edge(START, "collect")
    graph.add_conditional_edges(
        "collect",
        lambda state: (
            "continue"
            if int(state["evidence_collected"]) < int(state["evidence_needed"])
            else "review"
        ),
        {"continue": "collect", "review": "review"},
    )
    graph.add_edge("review", END)
    return graph.compile()


if __name__ == "__main__":
    final_state, steps = build_demo().run({"evidence_needed": 2})
    print("\n".join(steps))
    print(f"final={final_state!r}")
