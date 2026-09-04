# LangGraph from Zero

[简体中文](README.md) | [English](README_EN.md)

A Chinese-first course for readers with basic Python experience who want to study graph-runtime
semantics through small, runnable implementations. It starts with an approximately 100-line
deterministic state graph and gradually studies recoverable agent workflows.

> This project studies the source of [LangGraph](https://github.com/langchain-ai/langgraph). It is
> not an official LangChain project, a port of LangGraph, or an API-compatible replacement.

## What works today

Current release: [`v0.3.0`, Typed State and Reducers](lessons/03-typed-state-reducers/README.md).
It derives a key contract from `TypedDict`, accumulates annotated fields with reducers, and rejects
unknown keys, invalid values, or multiple same-batch writes to a plain field when they arrive as
explicit initial state or node updates. It does not depend on LangChain, LangGraph, or a live model.

The current runtime executes one node at a time. It supports static edges, conditional routing,
and an ordered update-batch experiment. The demo exposes four deterministic steps: normalize a
question, collect two offline evidence items, then route to review. Each step shows the local
update, merged state, and selected destination.

## What is not implemented

There are no channels, Pregel-style supersteps, parallel scheduling, checkpoints, persistence,
crash recovery, or interrupts, and there are no built-in model, network, or external-side-effect
adapters. The `merge_updates()` method is a teaching seam for reducer and plain-field conflict
semantics; it is not a parallel runtime. User-supplied Python nodes, routes, and reducers remain
trusted callbacks: the runtime makes only shallow state copies and cannot prevent them from
mutating nested objects or performing side effects. The roadmap capabilities are not part of
`v0.3.0`.

## Quick start

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m langgraph_from_zero
pytest
```

## Course contract

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
`pi-agent-from-zero` studies how a local coding agent acts; this project's roadmap studies how
long-running agents coordinate state, concurrency, recovery, human oversight, and verification.

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
