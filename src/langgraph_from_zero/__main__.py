"""Run a deterministic research loop with state-driven routing."""

from collections.abc import Mapping

from .graph import END, START, StateGraph


def normalize(state: Mapping[str, object]) -> dict[str, object]:
    return {"question": str(state["question"]).strip()}


def collect(state: Mapping[str, object]) -> dict[str, object]:
    collected = int(str(state.get("evidence_collected", 0))) + 1
    return {"evidence_collected": collected}


def decide_after_collect(state: Mapping[str, object]) -> str:
    collected = int(str(state["evidence_collected"]))
    needed = int(str(state["evidence_needed"]))
    if collected < needed:
        return "continue"
    return "review"


def review(state: Mapping[str, object]) -> dict[str, object]:
    return {"verdict": f"reviewed {state['evidence_collected']} evidence items"}


def main() -> None:
    graph = StateGraph()
    graph.add_node("normalize", normalize)
    graph.add_node("collect", collect)
    graph.add_node("review", review)
    graph.add_edge(START, "normalize").add_edge("normalize", "collect")
    graph.add_conditional_edges(
        "collect",
        decide_after_collect,
        {"continue": "collect", "review": "review"},
    )
    graph.add_edge("review", END)

    initial = {"question": "  What makes an agent durable?  ", "evidence_needed": 2}
    for step in graph.compile().stream(initial):
        print(
            f"step={step.index} node={step.node} update={dict(step.update)} next={step.next_node}"
        )


if __name__ == "__main__":
    main()
