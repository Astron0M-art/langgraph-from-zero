# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
