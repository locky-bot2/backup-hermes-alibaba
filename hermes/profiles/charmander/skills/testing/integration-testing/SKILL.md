---
name: integration-testing
description: "Write integration tests covering API endpoints, DB, and service interactions"
version: 1.0.0
author: Charmander
platforms: [linux, macos]
metadata:
  charmander:
    tags: [testing, integration, api]
    team: charmander
---

# Integration Testing Workflow

Test that components work together correctly.

## Scope

- API endpoint contracts (request/response shape, status codes)
- Database read/write operations
- Service-to-service calls (internal APIs, message queues)
- Authentication and authorization flows
- File I/O and external service integration

## Tooling

- Python: pytest + httpx (async) or requests
- Node/JS: Supertest + Vitest
- Go: httptest package
- Use testcontainers or local fixtures for dependencies (DB, Redis, etc.)

## Test Rules

- Each test cleans up after itself (teardown or temp isolation)
- Use a test DB or in-memory store — never the production DB
- Mock external third-party APIs, but test your adapter's integration
- Tests must be independent and runnable in any order

## When to Write

- After each new endpoint or data layer change
- When Ash merges Pikachu's PR into main
- Before signing off on a release