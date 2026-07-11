---
name: pr-workflow
description: "Create clean release branches and pull requests on GitHub"
version: 1.0.0
author: Pikachu
platforms: [linux, macos]
metadata:
  pikachu:
    tags: [github, pr, branches]
    team: pikachu
---

# PR Workflow

Create well-structured branches and pull requests for Ash to review.

## Branch Naming

- `feature/<short-description>` — new features
- `fix/<short-description>` — bug fixes
- `refactor/<short-description>` — code cleanup/refactoring
- `chore/<short-description>` — tooling, CI, dependencies

## Process

1. Create a branch from `main` (or the working base branch)
2. Implement the feature per Ash's spec
3. Commit with clear messages using conventional commits:
   - `feat: add user authentication endpoint`
   - `fix: handle null pointer in profile loader`
   - `test: add coverage for payment service`
4. Push the branch
5. Open a PR with title matching the feature/fix, description summarizing changes, test results, and coverage percentage
6. Report the PR URL to Ash

## PR Description Template

```
## What
[Summary of changes]

## Why
[Link to spec or issue]

## Test Results
Tests: [N] passed, [N] failed
Coverage: [N]%

## Checklist
- Code follows project conventions
- Tests pass (80%+ coverage)
- Self-review completed
- No debug/print statements left
```