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


def build_research_loop() -> StateGraph:
    graph = StateGraph()
    graph.add_node("collect", lambda state: {"count": int(state.get("count", 0)) + 1})
    graph.add_node("review", lambda state: {"reviewed": state["count"]})
    graph.add_edge(START, "collect")
    graph.add_conditional_edges(
        "collect",
        lambda state: "continue" if int(state["count"]) < 2 else "review",
        {"continue": "collect", "review": "review"},
    )
    graph.add_edge("review", END)
    return graph


def test_graph_runs_in_order_without_mutating_input() -> None:
    initial: Mapping[str, object] = {"value": "  graph  "}

    result = build_graph().compile().invoke(initial)

    assert result == {"value": "graph", "length": 5}
    assert initial == {"value": "  graph  "}


def test_conditional_route_reads_merged_update_and_terminates() -> None:
    steps = build_research_loop().compile().stream({})

    assert [step.node for step in steps] == ["collect", "collect", "review"]
    assert [step.next_node for step in steps] == ["collect", "review", END]
    assert steps[-1].state == {"count": 2, "reviewed": 2}


def test_direct_route_can_return_node_name_without_path_map() -> None:
    graph = StateGraph()
    graph.add_node("choose", lambda _state: {"ready": True})
    graph.add_node("finish", lambda _state: {"done": True})
    graph.add_edge(START, "choose")
    graph.add_conditional_edges("choose", lambda state: "finish" if state["ready"] else END)
    graph.add_edge("finish", END)

    assert graph.compile().invoke({}) == {"ready": True, "done": True}


def test_unknown_mapped_route_fails_at_decision_boundary() -> None:
    graph = StateGraph()
    graph.add_node("choose", lambda _state: {})
    graph.add_edge(START, "choose")
    graph.add_conditional_edges("choose", lambda _state: "unexpected", {"done": END})

    with pytest.raises(GraphError, match="unknown route 'unexpected' from node 'choose'"):
        graph.compile().invoke({})


def test_unknown_direct_route_fails_before_node_execution() -> None:
    graph = StateGraph()
    graph.add_node("choose", lambda _state: {})
    graph.add_edge(START, "choose")
    graph.add_conditional_edges("choose", lambda _state: "missing")

    with pytest.raises(GraphError, match="points to unknown node: 'missing'"):
        graph.compile().invoke({})


@pytest.mark.parametrize(
    ("configure", "message"),
    [
        (lambda graph: None, "no START edge"),
        (lambda graph: graph.add_edge(START, "missing"), "unknown node"),
        (
            lambda graph: (
                graph.add_edge(START, "only")
                .add_edge("only", END)
                .add_conditional_edges("only", lambda _state: "done", {"done": END})
            ),
            "both static and conditional",
        ),
        (
            lambda graph: graph.add_edge(START, "only").add_conditional_edges(
                "only", lambda _state: "bad", {"bad": "missing"}
            ),
            "conditional edge points to unknown node",
        ),
    ],
)
def test_compile_rejects_invalid_graph(configure: object, message: str) -> None:
    graph = StateGraph()
    graph.add_node("only", lambda _state: {})
    configure(graph)  # type: ignore[operator]

    with pytest.raises(GraphError, match=message):
        graph.compile()


def test_step_budget_stops_conditional_cycle() -> None:
    graph = StateGraph()
    graph.add_node("again", lambda state: {"count": int(state.get("count", 0)) + 1})
    graph.add_edge(START, "again")
    graph.add_conditional_edges("again", lambda _state: "again")

    with pytest.raises(GraphError, match="exceeded max_steps=3"):
        graph.compile().invoke({}, max_steps=3)
