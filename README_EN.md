# LangGraph from Zero

[简体中文](README.md) | [English](README_EN.md)

A Chinese-first, source-grounded course that rebuilds a durable agent graph runtime from
approximately 100 lines of Python.

The course grows through routing, reducers, Pregel-style supersteps, checkpoints, interrupts,
idempotent retries, subgraphs, memory, and trajectory evaluation. Its final outcome is a
recoverable Deep Research Agent with auditable evidence.

> This project studies the source of [LangGraph](https://github.com/langchain-ai/langgraph). It is
> not an official LangChain project, a port of LangGraph, or an API-compatible replacement.

## Status

Current release: [`v0.2.0`, Conditional Routing and Loops](lessons/02-conditional-routing/README.md).
It routes on merged node updates, maps stable labels to destinations, records each chosen next
node, terminates explicitly at `END`, and fails safely on unknown routes or exhausted step budgets.
It does not depend on LangChain, LangGraph, or a live model.

## Quick start

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m langgraph_from_zero
pytest
```

The demo deterministically normalizes a question, collects two offline evidence items, and routes
to review while exposing every selected destination.

## Course promise

- Every tagged lesson snapshot runs independently.
- Each release begins with a demonstrated limitation and adds one minimal abstraction.
- Source claims map to a pinned upstream commit and public symbols or tests.
- Offline fakes and fixtures are the default; API keys are never required for the course.
- Fault injection is labeled as an experiment and never presented as production experience.
- Production readiness is defined by evidence-based gates, not marketing language.

The full sequence is documented in [ROADMAP.md](ROADMAP.md). Chinese lessons are the source of
truth; this English README keeps release-level status, setup, limitations, governance, authorship,
and license information in sync.

## Relationship to Pi Agent from Zero

This repository does not repeat file tools, shell tools, TUI, MCP, or Skills as its main subject.
`pi-agent-from-zero` studies how a local coding agent acts; this project studies how long-running
agents coordinate state, concurrency, recovery, human oversight, and verification.

## Governance

- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Upstream Baseline](docs/upstream-baseline.md)
- [Automation Policy](docs/automation-policy.md)

## Author and maintainer

- [Astron_ma](https://github.com/Astron0M-art), GitHub `Astron0M-art`

## License

[MIT](LICENSE). Upstream and third-party projects retain their own licenses and attribution.
