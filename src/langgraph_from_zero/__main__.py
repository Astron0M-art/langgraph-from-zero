"""Run the first deterministic research-planning graph."""

from collections.abc import Mapping

from .graph import END, START, StateGraph


def normalize(state: Mapping[str, object]) -> dict[str, object]:
    return {"question": str(state["question"]).strip()}


def plan(state: Mapping[str, object]) -> dict[str, object]:
    question = str(state["question"])
    return {"plan": [f"Define terms in: {question}", "Collect evidence", "Review conflicts"]}


def main() -> None:
    graph = StateGraph()
    graph.add_node("normalize", normalize).add_node("plan", plan)
    graph.add_edge(START, "normalize").add_edge("normalize", "plan").add_edge("plan", END)

    for step in graph.compile().stream({"question": "  What makes an agent durable?  "}):
        print(f"step={step.index} node={step.node} update={dict(step.update)}")


if __name__ == "__main__":
    main()
