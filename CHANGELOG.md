# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Cumulative regression coverage showing v0.2 retains static graphs and both the v0.3 snapshot and
  default CLI compose static edges, conditional routing, typed state, and reducers end to end.

### Changed

- Defined every lesson snapshot as the cumulative runtime through that version; independent
  execution now means reproducibility without future code, not a separate implementation line.
- The default `pytest` command now collects root tests and all frozen lesson suites.
- Updated the public automation policy to the even-date midnight schedule and three context-isolated
  AI audit rounds; automated audit is not presented as human review.

### Fixed

- Corrected v0.1 lesson text to describe its actual `run()` and string-trace interface, and tied its
  checked-in trace to an exact fixture assertion.
- Aligned the v0.3 frozen reducer contract with its lesson: invalid signatures fail early and reducer
  exceptions are wrapped in `GraphError` with the original cause.
- Restored the v0.1/v0.2 untyped `StateGraph()` entry in the cumulative v0.3 snapshot by keeping the
  v0.3 state schema optional, matching the latest runtime.

## [0.3.0] - 2026-09-04

### Added

- TypedDict-style state schemas with required-key, allowed-key, and runtime value validation.
- `Annotated` binary reducers for sequential accumulation and ordered update batches.
- Explicit conflict errors when one batch writes multiple values to a field without a reducer.
- Independent third lesson with pinned LangGraph channel mappings, fault experiments, offline
  tests, exercises, and a fixture-verified deterministic trace.

### Changed

- The research demo now preserves individual evidence updates through a reducer instead of
  replacing the evidence collection.

## [0.2.0] - 2026-09-02

### Added

- State-driven conditional edges with optional route-label mappings and explicit `END` targets.
- Observable `Step.next_node` decisions and runtime validation for unknown conditional targets.
- Independent second lesson with architecture, pinned LangGraph source map, fault labs, exercises,
  offline tests, and a deterministic research-loop trace.

### Changed

- The command-line demo now grows from a static plan into a bounded collect-and-review loop.

## [0.1.0] - 2026-09-01

### Added

- Minimal deterministic `StateGraph` and compiled runtime.
- Copy-on-write state updates, observable steps, graph validation, and a runtime step budget.
- Independent first lesson with architecture, upstream source map, lab, exercise, tests, and trace.
- Chinese and English project entry points, governance documents, CI, and production-growth gates.

[Unreleased]: https://github.com/Astron0M-art/langgraph-from-zero/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Astron0M-art/langgraph-from-zero/releases/tag/v0.3.0
[0.2.0]: https://github.com/Astron0M-art/langgraph-from-zero/releases/tag/v0.2.0
[0.1.0]: https://github.com/Astron0M-art/langgraph-from-zero/releases/tag/v0.1.0
