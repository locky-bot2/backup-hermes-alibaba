---
name: code-review
description: "Code review checklist covering security, performance, maintainability, and best practices"
version: 1.0.0
author: Pikachu
platforms: [linux, macos]
metadata:
  pikachu:
    tags: [code-review, quality]
    team: pikachu
---

# Code Review

Systematic review checklist before marking a PR ready for Ash.

## Security Review

- [ ] No hardcoded secrets, tokens, or API keys
- [ ] User input validated and sanitized (XSS, injection)
- [ ] Authentication/authorization enforced on all endpoints
- [ ] Rate limiting applied to public endpoints
- [ ] Dependencies checked for known CVEs
- [ ] No SQL injection vectors (use parameterized queries)
- [ ] CORS configured correctly

## Performance Review

- [ ] N+1 queries eliminated
- [ ] Database queries have appropriate indexes
- [ ] Pagination on list endpoints
- [ ] Heavy computation cached or deferred
- [ ] Bundle size checked (no accidental large deps)
- [ ] Lazy loading for non-critical components

## Code Quality

- [ ] Follows project conventions and style guide
- [ ] No dead code, commented-out code, or TODOs
- [ ] Error handling is consistent and proper
- [ ] Logging at appropriate levels (info/warn/error)
- [ ] Functions are focused and testable
- [ ] No deeply nested callbacks or conditionals

## Testing

- [ ] Unit tests cover new code (≥80% coverage)
- [ ] Edge cases tested (empty, null, boundary values)
- [ ] Integration tests for API changes
- [ ] Tests all pass before committing

## PR Checklist

- [ ] Branch named `release/` or `release/<feature>`
- [ ] PR description explains what and why
- [ ] Coverage report included
- [ ] Self-reviewed diff before requesting Ash review
