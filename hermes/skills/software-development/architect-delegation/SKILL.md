---
name: architect-delegation
description: "Architect designs solutions, delegates to specialized agents, reviews via GitHub PRs, approves only when satisfied."
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [architecture, delegation, workflow, code-review, pr, github]
    related_skills: [subagent-driven-development, github-pr-workflow, github-code-review, writing-plans]
---

# Architect Delegation Workflow

## Overview

An architect-driven development workflow: the architect designs the solution, delegates implementation to specialized agents, and reviews deliverables via GitHub Pull Requests. The architect never implements directly — they think in systems, delegate execution, and ensure quality through structured review.

**Core principle:** Domain → Design → Delegate → Review → Approve

## When to Use

Use this workflow when:
- You have a system or feature to build with clear architectural responsibility
- You have specialized agents with defined roles (developer, QA, DevOps)
- Quality gates and structured code review are important
- You want GitHub as the source of truth for changes
- Multiple independent workstreams (parallel agent tasks)

**vs. subagent-driven-development (which is within-session subtasking):**
- Subagent-driven dev: fire-and-forget subagents within one session, inline review
- Architect delegation: durable profiles with role separation, PR-based handoff, async review cycle

## Agent Roles

| Role | Name | Responsibility |
|------|------|---------------|
| **Architect** | Ash (main) | Designs solutions, delegates, reviews, approves |
| **Developer** | Pikachu | Implements code, writes tests, creates PRs |
| **QA** | Charmander | Writes and runs tests, reports bugs |
| **DevOps** | Squirtle | Infrastructure, CI/CD, deployment |

## The Workflow

### Phase 1: Design

Before delegating, understand the problem space and produce a clear spec:

1. **Define requirements** — what needs to be built and why
2. **Architecture decisions** — technology choices, component boundaries, data flow
3. **Spec document** — write a clear spec the agent can execute against
4. **Break into tasks** — independent work items for parallel delegation

Output: a written spec or plan that the agent reads as their single source of truth.

### Phase 2: Delegate

Dispatch tasks to the appropriate agent:

```python
# Delegate implementation to Pikachu
delegate_task(
    goal="Implement user authentication feature per the spec",
    context="""
    SPEC: docs/specs/auth-feature.md
    
    WORKFLOW FOR THIS TASK:
    1. Read the spec document
    2. Implement all components
    3. Write unit tests (≥80% coverage)
    4. Run tests — all must pass
    5. Commit all changes
    6. Create branch: release (or release/<feature-name>)
    7. Push to GitHub origin
    8. Create PR from release → main
    9. Report PR URL back to Ash for review
    
    CRITICAL: Do NOT merge the PR. Ash reviews and approves.
    """,
    toolsets=['terminal', 'file']
)
```

Key delegation rules:
- **Pikachu** builds, tests, creates the PR — never merges
- **Charmander** tests, verifies, writes test suites
- **Squirtle** deploys, configures infrastructure, manages CI/CD
- All agents provide their work via verifiable handles (PR URLs, deployed URLs, test reports)

### Phase 3: Review

When the agent reports back with a PR, review on GitHub:

```text
Review dimensions (in order):
1. Architecture alignment — does this match the spec/design?
2. Code quality — clean, maintainable, idiomatic?
3. Test coverage — ≥80%? Edge cases covered?
4. Security — no obvious vulnerabilities?
5. Edge cases — handled correctly?

Provide feedback directly on the GitHub PR:
- Approve inline comments for specific lines
- Request changes when requirements aren't met
- Summarize blocking vs. nice-to-have feedback
```

Use the `github-code-review` skill for structured PR review workflow.

### Phase 4: Approve or Steer

| If... | Then... |
|-------|---------|
| All review dimensions pass | Approve and merge the PR |
| Minor issues found | Comment on the PR, ask for fixes, approve after addressed |
| Major issues found | Request changes on the PR, steer the agent to fix, re-review |
| Spec misalignment | Pause, re-clarify requirements, re-delegate with corrected spec |

### Phase 5: Deploy

After merge, Squirtle handles deployment:

```python
delegate_task(
    goal="Deploy the merged feature to production",
    context=f"""
    PR merged: {pr_url}
    Deploy from main branch.
    Verify deployment health after rollout.
    """,
    toolsets=['terminal', 'file']
)
```

## GitHub PR Convention

- **Branch**: `release` or `release/<feature-name>`
- **Target**: `main`
- **PR description**: must include what was built, test results, coverage summary
- **Merge**: only the architect merges (after review approval)

## Pitfalls

- **Empty provider in agent profile** — an agent with `provider: ""` cannot make API calls. Check all profiles before delegating.
- **Agent can't use terminal** — subagents spawned via `delegate_task` CAN write files but CANNOT run terminal commands or `execute_code`. The agent must write a script, then the parent runs it: subagent `write_file("script.sh", ...)` → parent `terminal("bash script.sh")`.
- **Delegating without a spec** — agents need a clear written goal. Vague delegation produces off-target output.
- **Skipping review** — the architect's review is the quality gate. Never merge unreviewed PRs.
- **Parallel conflicts** — when delegating to multiple agents, ensure they don't touch overlapping files to avoid merge conflicts.
- **Nested delegation** — for this user, max_spawn_depth=1; children cannot delegate further. Keep delegation flat.

## Related Skills

- `github-pr-workflow` — Creating branches, PRs, managing the GitHub lifecycle
- `github-code-review` — Structured PR review with inline comments
- `writing-plans` — Creating implementation plans from requirements
- `subagent-driven-development` — Within-session task delegation with 2-stage review
- `test-driven-development` — TDD discipline for implementer agents
