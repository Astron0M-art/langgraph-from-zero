import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "snapshot" / "graph.py"
TRACE_PATH = pathlib.Path(__file__).parents[1] / "traces" / "happy-path.txt"
SPEC = importlib.util.spec_from_file_location("lesson_02_graph", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
GRAPH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GRAPH)


class ConditionalGraphTests(unittest.TestCase):
    def test_demo_routes_on_merged_state_and_is_deterministic(self) -> None:
        initial = {"evidence_needed": 2}
        state, trace = GRAPH.build_demo().run(initial)
        self.assertEqual(
            state, {"evidence_needed": 2, "evidence_collected": 2, "verdict": "reviewed 2 items"}
        )
        self.assertEqual(
            [line.split()[0] for line in trace], ["node=collect", "node=collect", "node=review"]
        )
        self.assertIn("next=collect", trace[0])
        self.assertIn("next=review", trace[1])
        self.assertIn(f"next={GRAPH.END}", trace[2])
        self.assertEqual(initial, {"evidence_needed": 2})

        rendered = "\n".join([*trace, f"final={state!r}"]) + "\n"
        self.assertEqual(rendered, TRACE_PATH.read_text(encoding="utf-8"))

    def test_unknown_route_is_explicit(self) -> None:
        graph = GRAPH.StateGraph()
        graph.add_node("choose", lambda state: {})
        graph.add_edge(GRAPH.START, "choose")
        graph.add_conditional_edges("choose", lambda state: "publish", {"review": GRAPH.END})
        with self.assertRaisesRegex(GRAPH.GraphError, "unknown route 'publish'"):
            graph.compile().run({})

    def test_conditional_cycle_stops_at_budget(self) -> None:
        graph = GRAPH.StateGraph()
        graph.add_node("again", lambda state: {"count": int(state.get("count", 0)) + 1})
        graph.add_edge(GRAPH.START, "again")
        graph.add_conditional_edges("again", lambda state: "again")
        with self.assertRaisesRegex(GRAPH.GraphError, "max_steps=3"):
            graph.compile().run({}, max_steps=3)


if __name__ == "__main__":
    unittest.main()
