---
name: test-suite-runner
description: "Run the full test suite after Ash merges a PR and report results"
version: 1.0.0
author: Charmander
platforms: [linux, macos]
metadata:
  charmander:
    tags: [testing, ci, pipeline]
    team: charmander
---

# Test Suite Runner

Run the full test pyramid when Ash merges a PR.

## Execution Order

1. **Unit tests** (Pikachu's tests) — fast, fail first
2. **Integration tests** — API + DB layer
3. **E2E tests** — full user journeys (slowest, run last)

## Commands

- Python: `pytest tests/ -v --tb=short`
- Node: `npm test` or specific runner
- Coverage: `pytest --cov=src tests/`

## Report Format

```
Test Suite Results
==================
Unit tests:   [N] passed, [N] failed
Integration:  [N] passed, [N] failed
E2E:          [N] passed, [N] failed
Coverage:     [N]%

BLOCKERS: [list any failures that prevent release]
```

## On Failure

- If unit tests fail → flag Pikachu to fix before anything else
- If integration tests fail → check if the merge changed contracts
- If E2E tests fail → provide the failing test name + screenshot
- Always attach reproduction info for each failure