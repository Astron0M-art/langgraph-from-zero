# Repository Agent Rules

## Scope

Maintain this repository as an independent, Chinese-first, source-grounded course about durable
agent graph runtimes. Never modify the sibling repository
`/Users/astron/Demo_projects/pi-agent-from-zero` while working here.

The upstream LangGraph reference is read-only. Public source maps are authoritative; never make a
local upstream checkout a reader requirement.

## Release discipline

- Follow `ROADMAP.md` in order and complete at most one teaching release per scheduled run.
- Never create an empty release to satisfy a calendar.
- Maintain one cumulative runtime: version `vN` contains every verified behavior from `vN-1` plus
  one new runtime semantic. Never replace the runtime with a parallel demo.
- A release requires runnable code, lesson documentation, source map, exercises, tests, trace
  evidence, changelog entry, and synchronized README status.
- A lesson snapshot is the cumulative runtime as of that version. Keep it independently runnable
  without future code; "independent" never means unrelated to previous versions.
- Before release, run the new behavior, all historical regressions, and at least one end-to-end graph
  that composes two or more previously released capabilities.
- Preserve public API, CLI, state schema, and future checkpoint formats, or document and test an
  explicit migration. Silent compatibility breaks block release.
- Tag and create a GitHub Release only after the PR is merged and all checks pass.

## Safety

- Never read or commit secrets, tokens, cookies, private files, generated sessions, or personal data.
- Preserve user changes and stage explicit files only.
- Do not force-push, bypass CI, weaken required checks, or merge a failing branch.
- Automated changes use `codex/` branches and Pull Requests; never push automation directly to main.
- Real network and model adapters stay optional and off in default tests.

## Quality

- Prefer deterministic fakes, fixtures, seeded clocks, and observable assertions.
- Separate graph state, channel updates, durable checkpoints, external side effects, and traces.
- Label fault injection as an experiment; write a postmortem only for an actual observed failure.
- Treat production readiness as the gates in `docs/production-readiness.md`.
- Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, lesson tests, and package build
  before release.

## Git

- Use Conventional Commits in English.
- Do not commit incomplete code or unverified generated artifacts.
- Upstream upgrades require an explicit baseline diff; never silently move the pinned commit.
