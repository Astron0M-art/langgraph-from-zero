import importlib.util
import pathlib
import sys
import unittest
from typing import Annotated, NotRequired, TypedDict

MODULE_PATH = pathlib.Path(__file__).parents[1] / "snapshot" / "graph.py"
TRACE_PATH = pathlib.Path(__file__).parents[1] / "traces" / "happy-path.txt"
SPEC = importlib.util.spec_from_file_location("lesson_03_graph", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
GRAPH = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GRAPH
SPEC.loader.exec_module(GRAPH)


def append_items(current: list[str], update: list[str]) -> list[str]:
    return [*current, *update]


def bad_reducer(only_one: object) -> object:
    return only_one


def exploding_reducer(current: list[str], update: list[str]) -> list[str]:
    raise RuntimeError("boom")


def defaulted_reducer(current: list[str], update: list[str] | None = None) -> list[str]:
    return [*current, *(update or [])]


class CompatibilityState(TypedDict):
    count: int
    items: Annotated[list[str], append_items]
    verdict: NotRequired[str]


class InvalidReducerState(TypedDict):
    items: Annotated[list[str], bad_reducer]


class ExplodingReducerState(TypedDict):
    items: Annotated[list[str], exploding_reducer]


class DefaultedReducerState(TypedDict):
    items: Annotated[list[str], defaulted_reducer]


class TypedStateTests(unittest.TestCase):
    def test_v01_untyped_state_graph_entry_remains_available(self) -> None:
        graph = GRAPH.StateGraph()
        graph.add_node("write", lambda state: {"value": f"{state['value']}-done"})
        graph.add_edge(GRAPH.START, "write")
        graph.add_edge("write", GRAPH.END)

        initial = {"value": "legacy"}
        state, trace = graph.compile().run(initial)

        self.assertEqual(state, {"value": "legacy-done"})
        self.assertEqual([line.split()[0] for line in trace], ["node=write"])
        self.assertEqual(initial, {"value": "legacy"})

    def test_v01_static_edges_and_v02_routing_compose_with_v03_state(self) -> None:
        graph = GRAPH.StateGraph(CompatibilityState)
        graph.add_node(
            "collect",
            lambda state: {
                "count": int(state["count"]) + 1,
                "items": [f"item-{int(state['count']) + 1}"],
            },
        )
        graph.add_node("review", lambda state: {"verdict": f"reviewed {len(state['items'])}"})
        graph.add_edge(GRAPH.START, "collect")
        graph.add_conditional_edges(
            "collect",
            lambda state: "continue" if int(state["count"]) < 2 else "review",
            {"continue": "collect", "review": "review"},
        )
        graph.add_edge("review", GRAPH.END)

        initial = {"count": 0, "items": []}
        state, trace = graph.compile().run(initial)

        self.assertEqual(
            state,
            {"count": 2, "items": ["item-1", "item-2"], "verdict": "reviewed 2"},
        )
        self.assertEqual(
            [line.split()[0] for line in trace],
            ["node=collect", "node=collect", "node=review"],
        )
        self.assertEqual(initial, {"count": 0, "items": []})

    def test_v02_direct_route_and_step_budget_remain_available(self) -> None:
        graph = GRAPH.StateGraph()
        graph.add_node("again", lambda state: {"count": int(state.get("count", 0)) + 1})
        graph.add_edge(GRAPH.START, "again")
        graph.add_conditional_edges("again", lambda _state: "again")

        with self.assertRaisesRegex(GRAPH.GraphError, "max_steps=3"):
            graph.compile().run({}, max_steps=3)

    def test_v02_duplicate_conditional_edge_is_rejected(self) -> None:
        graph = GRAPH.StateGraph()
        graph.add_node("choose", lambda _state: {})
        graph.add_edge(GRAPH.START, "choose")
        graph.add_conditional_edges("choose", lambda _state: GRAPH.END)

        with self.assertRaisesRegex(GRAPH.GraphError, "duplicate conditional edge"):
            graph.add_conditional_edges("choose", lambda _state: GRAPH.END)

    def test_demo_accumulates_updates_and_matches_trace(self) -> None:
        initial = {"evidence_needed": 2, "evidence": []}
        state, trace = GRAPH.build_demo().run(initial)

        self.assertEqual(
            state,
            {
                "evidence_needed": 2,
                "evidence": ["source-1", "source-2"],
                "verdict": "reviewed 2 items",
            },
        )
        self.assertEqual(initial, {"evidence_needed": 2, "evidence": []})
        rendered = "\n".join([*trace, f"final={state!r}"]) + "\n"
        self.assertEqual(rendered, TRACE_PATH.read_text(encoding="utf-8"))

    def test_reducer_merges_an_ordered_update_batch(self) -> None:
        graph = GRAPH.build_demo()
        merged = graph.merge_updates(
            {"evidence_needed": 2, "evidence": []},
            [{"evidence": ["a"]}, {"evidence": ["b"]}],
        )
        self.assertEqual(merged["evidence"], ["a", "b"])

    def test_plain_key_rejects_two_writers(self) -> None:
        graph = GRAPH.build_demo()
        with self.assertRaisesRegex(GRAPH.GraphError, "conflicting updates"):
            graph.merge_updates(
                {"evidence_needed": 2, "evidence": []},
                [{"evidence_needed": 3}, {"evidence_needed": 4}],
            )

    def test_schema_rejects_unknown_key_and_wrong_type(self) -> None:
        graph = GRAPH.build_demo()
        with self.assertRaisesRegex(GRAPH.GraphError, "unknown state keys"):
            graph.run({"evidence_needed": 2, "evidence": [], "private": "no"})
        with self.assertRaisesRegex(GRAPH.GraphError, "invalid type"):
            graph.run({"evidence_needed": "two", "evidence": []})

    def test_reducer_result_must_match_state_value_type(self) -> None:
        graph = GRAPH.build_demo()
        with self.assertRaisesRegex(GRAPH.GraphError, "invalid type"):
            graph.merge_updates(
                {"evidence_needed": 2, "evidence": []},
                [{"evidence": [1]}],
            )

    def test_invalid_reducer_signature_is_rejected(self) -> None:
        with self.assertRaisesRegex(GRAPH.GraphError, r"expected \(current, update\)"):
            GRAPH.StateGraph(InvalidReducerState)

    def test_two_parameter_reducer_with_default_matches_current_runtime(self) -> None:
        spec = GRAPH.StateSpec(DefaultedReducerState)

        merged = spec.merge({"items": []}, [{"items": ["a"]}, {"items": ["b"]}])

        self.assertEqual(merged, {"items": ["a", "b"]})

    def test_reducer_failure_is_wrapped_with_cause(self) -> None:
        spec = GRAPH.StateSpec(ExplodingReducerState)
        with self.assertRaisesRegex(GRAPH.GraphError, "reducer failed") as captured:
            spec.merge({"items": []}, [{"items": ["a"]}])
        self.assertIsInstance(captured.exception.__cause__, RuntimeError)


if __name__ == "__main__":
    unittest.main()
