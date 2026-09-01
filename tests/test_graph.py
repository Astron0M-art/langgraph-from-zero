from __future__ import annotations

from collections.abc import Mapping

import pytest

from langgraph_from_zero import END, START, GraphError, StateGraph


def build_graph() -> StateGraph:
    graph = StateGraph()
    graph.add_node("normalize", lambda state: {"value": str(state["value"]).strip()})
    graph.add_node("measure", lambda state: {"length": len(str(state["value"]))})
    graph.add_edge(START, "normalize")
    graph.add_edge("normalize", "measure")
    graph.add_edge("measure", END)
    return graph


def test_graph_runs_in_order_without_mutating_input() -> None:
    initial: Mapping[str, object] = {"value": "  graph  "}

    result = build_graph().compile().invoke(initial)

    assert result == {"value": "graph", "length": 5}
    assert initial == {"value": "  graph  "}


def test_stream_exposes_external_transitions() -> None:
    steps = build_graph().compile().stream({"value": " state "})

    assert [step.node for step in steps] == ["normalize", "measure"]
    assert steps[0].update == {"value": "state"}
    assert steps[-1].state == {"value": "state", "length": 5}


@pytest.mark.parametrize(
    ("configure", "message"),
    [
        (lambda graph: None, "no START edge"),
        (lambda graph: graph.add_edge(START, "missing"), "unknown node"),
    ],
)
def test_compile_rejects_invalid_graph(configure: object, message: str) -> None:
    graph = StateGraph()
    graph.add_node("only", lambda _state: {})
    configure(graph)  # type: ignore[operator]

    with pytest.raises(GraphError, match=message):
        graph.compile()


def test_step_budget_stops_cycle() -> None:
    graph = StateGraph()
    graph.add_node("again", lambda state: {"count": int(state.get("count", 0)) + 1})
    graph.add_edge(START, "again").add_edge("again", "again")

    with pytest.raises(GraphError, match="exceeded max_steps=3"):
        graph.compile().invoke({}, max_steps=3)
