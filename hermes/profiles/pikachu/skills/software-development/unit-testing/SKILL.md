---
name: unit-testing
description: "Write thorough unit tests with 80%+ coverage"
version: 1.0.0
author: Pikachu
platforms: [linux, macos]
metadata:
  pikachu:
    tags: [testing, pytest, coverage]
    team: pikachu
---

# Unit Testing Workflow

Write unit tests that prove the code works correctly.

## Tooling

- Python: pytest + pytest-cov
- JavaScript/TS: Vitest or Jest
- Go: go test
- Rust: cargo test

## Coverage Target

- Minimum 80% line coverage for the module/package
- Focus on business logic — config files and trivial getters can be excluded
- Run coverage report and attach to the PR

## Test Structure

- Mirror source tree: `tests/test_<module>.py`
- One test class per source class/function group
- Descriptive test names: `test_{function}_{scenario}_{expected_outcome}`

## What to Test

- Happy path
- Edge cases (empty input, boundary values, type mismatches)
- Error paths (exceptions, invalid states, network timeouts)
- Side effects (state mutations, file writes, DB calls)

## What NOT to Test

- Third-party library behavior (mock it)
- Trivial getters/setters
- Configuration loading (just the parsing function)

## Reporting

After running tests, include the coverage summary in the PR description