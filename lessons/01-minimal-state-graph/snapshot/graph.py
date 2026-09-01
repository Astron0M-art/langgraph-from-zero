"""Frozen v0.1.0 snapshot: a minimal deterministic state graph."""

from __future__ import annotations

from collections.abc import Callable, Mapping

START = "__start__"
END = "__end__"


class GraphError(ValueError):
    pass


class StateGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Callable[[Mapping[str, object]], Mapping[str, object]]] = {}
        self.edges: dict[str, list[str]] = {}

    def add_node(
        self, name: str, node: Callable[[Mapping[str, object]], Mapping[str, object]]
    ) -> None:
        if name in self.nodes or name in {START, END}:
            raise GraphError(f"invalid or duplicate node: {name}")
        self.nodes[name] = node

    def add_edge(self, source: str, target: str) -> None:
        self.edges.setdefault(source, []).append(target)

    def compile(self) -> CompiledGraph:
        allowed = set(self.nodes) | {START, END}
        if START not in self.edges:
            raise GraphError("graph has no START edge")
        for source, targets in self.edges.items():
            if source not in allowed or any(target not in allowed for target in targets):
                raise GraphError("edge references an unknown node")
            if len(targets) != 1:
                raise GraphError("v0.1 supports exactly one outgoing edge")
        if any(name not in self.edges for name in self.nodes):
            raise GraphError("every node needs an outgoing edge")
        return CompiledGraph(
            dict(self.nodes), {source: targets[0] for source, targets in self.edges.items()}
        )


class CompiledGraph:
    def __init__(self, nodes: Mapping[str, Callable], edges: Mapping[str, str]) -> None:
        self.nodes = dict(nodes)
        self.edges = dict(edges)

    def run(
        self, initial: Mapping[str, object], max_steps: int = 100
    ) -> tuple[dict[str, object], list[str]]:
        state = dict(initial)
        node_name = self.edges[START]
        trace: list[str] = []
        for _ in range(max_steps):
            update = dict(self.nodes[node_name](dict(state)))
            state.update(update)
            trace.append(f"node={node_name} update={update!r}")
            node_name = self.edges[node_name]
            if node_name == END:
                return state, trace
        raise GraphError(f"graph exceeded max_steps={max_steps}")


def build_demo() -> CompiledGraph:
    graph = StateGraph()
    graph.add_node("normalize", lambda state: {"question": str(state["question"]).strip()})
    graph.add_node("plan", lambda state: {"plan": ["define", "collect", "review"]})
    graph.add_edge(START, "normalize")
    graph.add_edge("normalize", "plan")
    graph.add_edge("plan", END)
    return graph.compile()


if __name__ == "__main__":
    final_state, steps = build_demo().run({"question": "  What makes an agent durable?  "})
    print("\n".join(steps))
    print(f"final={final_state!r}")
