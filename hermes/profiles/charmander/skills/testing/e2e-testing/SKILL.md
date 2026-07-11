---
name: e2e-testing
description: "End-to-end tests with Playwright or Cypress covering full user journeys"
version: 1.0.0
author: Charmander
platforms: [linux, macos]
metadata:
  charmander:
    tags: [testing, e2e, playwright, cypress]
    team: charmander
---

# E2E Testing Workflow

Test real user journeys from browser to backend.

## Tooling

- **Playwright** (preferred) — cross-browser, fast, auto-wait
- **Cypress** — if already in the project

## Scenarios to Cover

- User signup → login → logout flow
- Core CRUD workflows (create item, view it, edit it, delete it)
- Error states (bad input, expired session, 404 pages)
- Responsive layout at mobile and desktop breakpoints
- Auth gating (unauthenticated users redirected to login)

## Test Structure

```
tests/e2e/
  auth.spec.js
  crud.spec.js
  navigation.spec.js
```

## Rules

- Use test fixtures or seeded data — never depend on production state
- Tests must be idempotent (same result run 1 vs run 10)
- Screenshot on failure for debugging
- Keep tests fast: max 30s per test, parallelize where possible

## When to Run

- Before every release
- After major merges to main
- When Ash requests a smoke check