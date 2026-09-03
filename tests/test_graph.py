from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, TypedDict

import pytest

from langgraph_from_zero import END, START, GraphError, StateGraph


def append_items(current: list[str], update: list[str]) -> list[str]:
    return [*current, *update]


def bad_reducer(only_one: object) -> object:
    return only_one


class ResearchState(TypedDict):
    count: int
    evidence: Annotated[list[str], append_items]
    reviewed: bool


def build_research_loop() -> StateGraph:
    graph = StateGraph(ResearchState)
    graph.add_node(
        "collect",
        lambda state: {
            "count": int(state["count"]) + 1,
            "evidence": [f"source-{int(state['count']) + 1}"],
        },
    )
    graph.add_node("review", lambda _state: {"reviewed": True})
    graph.add_edge(START, "collect")
    graph.add_conditional_edges(
        "collect",
        lambda state: "continue" if int(state["count"]) < 2 else "review",
        {"continue": "collect", "review": "review"},
    )
    graph.add_edge("review", END)
    return graph


def test_reducer_accumulates_sequential_node_updates() -> None:
    initial: Mapping[str, object] = {"count": 0, "evidence": [], "reviewed": False}

    steps = build_research_loop().compile().stream(initial)

    assert [step.node for step in steps] == ["collect", "collect", "review"]
    assert steps[0].state["evidence"] == ["source-1"]
    assert steps[-1].state == {
        "count": 2,
        "evidence": ["source-1", "source-2"],
        "reviewed": True,
    }
    assert initial == {"count": 0, "evidence": [], "reviewed": False}


def test_reducer_merges_ordered_update_batch() -> None:
    compiled = build_research_loop().compile()

    result = compiled.merge_updates(
        {"count": 0, "evidence": [], "reviewed": False},
        [{"evidence": ["source-a"]}, {"evidence": ["source-b"]}],
    )

    assert result["evidence"] == ["source-a", "source-b"]


def test_batch_rejects_multiple_values_without_reducer() -> None:
    compiled = build_research_loop().compile()

    with pytest.raises(
        GraphError,
        match="conflicting updates for state key 'count': received 2 values without a reducer",
    ):
        compiled.merge_updates(
            {"count": 0, "evidence": [], "reviewed": False},
            [{"count": 1}, {"count": 2}],
        )


@pytest.mark.parametrize(
    ("initial", "message"),
    [
        ({"count": 0, "evidence": []}, r"missing required keys: \['reviewed'\]"),
        (
            {"count": 0, "evidence": [], "reviewed": False, "extra": True},
            r"unknown keys: \['extra'\]",
        ),
        (
            {"count": "zero", "evidence": [], "reviewed": False},
            "state key 'count': expected int, got str",
        ),
    ],
)
def test_schema_rejects_invalid_initial_state(initial: dict[str, object], message: str) -> None:
    with pytest.raises(GraphError, match=message):
        build_research_loop().compile().invoke(initial)


def test_schema_rejects_unknown_node_update() -> None:
    graph = StateGraph(ResearchState)
    graph.add_node("bad", lambda _state: {"citation": "missing from schema"})
    graph.add_edge(START, "bad").add_edge("bad", END)

    with pytest.raises(GraphError, match="unknown state key: 'citation'"):
        graph.compile().invoke({"count": 0, "evidence": [], "reviewed": False})


def test_schema_rejects_wrong_node_update_type() -> None:
    graph = StateGraph(ResearchState)
    graph.add_node("bad", lambda _state: {"count": "one"})
    graph.add_edge(START, "bad").add_edge("bad", END)

    with pytest.raises(GraphError, match="state key 'count': expected int, got str"):
        graph.compile().invoke({"count": 0, "evidence": [], "reviewed": False})


def test_schema_rejects_wrong_reducer_result_type() -> None:
    compiled = build_research_loop().compile()

    with pytest.raises(GraphError, match=r"state key 'evidence': expected list\[str\], got list"):
        compiled.merge_updates(
            {"count": 0, "evidence": [], "reviewed": False},
            [{"evidence": [1]}],
        )


def test_invalid_reducer_signature_is_rejected() -> None:
    class BadState(TypedDict):
        values: Annotated[list[str], bad_reducer]

    with pytest.raises(GraphError, match=r"expected \(current, update\)"):
        StateGraph(BadState)


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
    ],
)
def test_compile_rejects_invalid_graph(configure: object, message: str) -> None:
    graph = StateGraph()
    graph.add_node("only", lambda _state: {})
    configure(graph)  # type: ignore[operator]

    with pytest.raises(GraphError, match=message):
        graph.compile()


def test_legacy_untyped_graph_still_runs() -> None:
    graph = StateGraph()
    graph.add_node("write", lambda _state: {"value": "done"})
    graph.add_edge(START, "write").add_edge("write", END)

    assert graph.compile().invoke({}) == {"value": "done"}


def test_step_budget_stops_conditional_cycle() -> None:
    graph = StateGraph()
    graph.add_node("again", lambda state: {"count": int(state.get("count", 0)) + 1})
    graph.add_edge(START, "again")
    graph.add_conditional_edges("again", lambda _state: "again")

    with pytest.raises(GraphError, match="exceeded max_steps=3"):
        graph.compile().invoke({}, max_steps=3)
