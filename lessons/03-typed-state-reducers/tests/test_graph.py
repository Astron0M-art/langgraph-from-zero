import importlib.util
import pathlib
import sys
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "snapshot" / "graph.py"
TRACE_PATH = pathlib.Path(__file__).parents[1] / "traces" / "happy-path.txt"
SPEC = importlib.util.spec_from_file_location("lesson_03_graph", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
GRAPH = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GRAPH
SPEC.loader.exec_module(GRAPH)


class TypedStateTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
