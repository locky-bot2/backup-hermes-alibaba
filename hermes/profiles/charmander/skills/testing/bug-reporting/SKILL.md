---
name: bug-reporting
description: "Document bugs with clear reproduction steps for Ash and Pikachu"
version: 1.0.0
author: Charmander
platforms: [linux, macos]
metadata:
  charmander:
    tags: [testing, bugs, reporting]
    team: charmander
---

# Bug Reporting Workflow

Never fix bugs. Report them clearly so Ash and Pikachu can act.

## Bug Report Template

```
## Bug: [Short Title]

### Severity
[critical / major / minor / cosmetic]

### Environment
- OS: [e.g. Linux 6.8]
- Browser: [if frontend]
- Branch/Commit: [where it was found]

### Steps to Reproduce
1. Go to ...
2. Click on ...
3. See error

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Screenshots / Logs
[Attach evidence]
```

## Discovery Channels

- While running integration tests
- While running E2E tests
- When exploring the app manually

## Rules

- One bug = one report (no bundling)
- Always include reproduction steps
- Attach relevant test output, screenshots, or logs
- Flag critical bugs immediately to Ash
- Do NOT fix the bug — not even a small one