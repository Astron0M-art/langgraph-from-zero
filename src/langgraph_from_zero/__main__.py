"""Run a typed research loop with reducer-backed evidence accumulation."""

from collections.abc import Mapping
from typing import Annotated, NotRequired, TypedDict, cast

from .graph import END, START, StateGraph


def append_evidence(current: list[str], update: list[str]) -> list[str]:
    return [*current, *update]


class ResearchState(TypedDict):
    question: str
    evidence_needed: int
    evidence: Annotated[list[str], append_evidence]
    verdict: NotRequired[str]


def normalize(state: Mapping[str, object]) -> dict[str, object]:
    return {"question": str(state["question"]).strip()}


def collect(state: Mapping[str, object]) -> dict[str, object]:
    evidence = cast(list[str], state["evidence"])
    return {"evidence": [f"source-{len(evidence) + 1}"]}


def decide_after_collect(state: Mapping[str, object]) -> str:
    evidence = cast(list[str], state["evidence"])
    if len(evidence) < int(str(state["evidence_needed"])):
        return "continue"
    return "review"


def review(state: Mapping[str, object]) -> dict[str, object]:
    evidence = cast(list[str], state["evidence"])
    return {"verdict": f"reviewed {len(evidence)} evidence items"}


def main() -> None:
    graph = StateGraph(ResearchState)
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

    initial: ResearchState = {
        "question": "  What makes an agent durable?  ",
        "evidence_needed": 2,
        "evidence": [],
    }
    for step in graph.compile().stream(initial):
        print(
            f"step={step.index} node={step.node} "
            f"update={dict(step.update)} state={dict(step.state)} next={step.next_node}"
        )


if __name__ == "__main__":
    main()
