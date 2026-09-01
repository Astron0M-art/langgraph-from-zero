import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "snapshot" / "graph.py"
SPEC = importlib.util.spec_from_file_location("lesson_01_graph", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
GRAPH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GRAPH)


class MinimalGraphTests(unittest.TestCase):
    def test_demo_is_deterministic(self) -> None:
        initial = {"question": "  Durable agents?  "}
        state, trace = GRAPH.build_demo().run(initial)
        self.assertEqual(state["question"], "Durable agents?")
        self.assertEqual(state["plan"], ["define", "collect", "review"])
        self.assertEqual([line.split()[0] for line in trace], ["node=normalize", "node=plan"])
        self.assertEqual(initial, {"question": "  Durable agents?  "})

    def test_cycle_stops_at_budget(self) -> None:
        graph = GRAPH.StateGraph()
        graph.add_node("again", lambda state: {"count": int(state.get("count", 0)) + 1})
        graph.add_edge(GRAPH.START, "again")
        graph.add_edge("again", "again")
        with self.assertRaisesRegex(GRAPH.GraphError, "max_steps=2"):
            graph.compile().run({}, max_steps=2)


if __name__ == "__main__":
    unittest.main()
