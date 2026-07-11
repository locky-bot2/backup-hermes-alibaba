---
name: kanban
description: Multi-profile, multi-agent work queue for Hermes. Covers the dispatcher-automated worker lifecycle, orchestration playbooks for task decomposition and routing, and worker pitfalls for Kanban card execution.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, routing, worker, collaboration]
    related_skills: [hermes-agent, subagent-delegation]
---

# Kanban — Multi-Profile Work Queue

Durable SQLite board for multi-profile / multi-worker collaboration. This umbrella covers both the **orchestrator** profile (task decomposition and routing) and the **worker** profile (card execution, handoffs, pitfalls).

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ Orchestrator (routing profile)                      │
│   • Decompose goals into task graphs                │
│   • Create cards with dependency links              │
│   • Route to right profiles via kanban_create       │
│   • NEVER do the work yourself                      │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ Kanban Board (SQLite)                                │
│   • Tasks, dependencies, comments, runs              │
│   • Dispatcher promotes todo→ready→claimed           │
│   • Profiles claim cards when they match             │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ Workers (dispatched profiles)                        │
│   • Claim card → orient (kanban_show over kanban_show)        │
│   • Work in isolated workspace                       │
│   • Complete or block with handoff summary           │
└─────────────────────────────────────────────────────┘
```

## Quick Setup

```bash
# Initialize the board (one-time)
hermes kanban init

# Verify dispatcher is running
grep "kanban dispatcher" ~/.hermes/logs/gateway.log

# List tasks
hermes kanban list
```

## For Orchestrators

See `references/orchestrator-playbook.md` for full decomposition patterns: discovering available profiles, creating task graphs (fan-out + fan-in, pipelines, parallel), dependency linking, goal-mode cards, recovery of stuck workers, and common pitfalls.

**Core rules:**
- Discover profiles before planning: `hermes profile list`
- Never execute the work yourself — create cards
- Split multi-lane requests before creating cards
- Create independent lanes as parallel cards
- Link only true data dependencies
- Use `goal_mode=True` for open-ended cards

## For Workers

See `references/worker-pitfalls.md` for: workspace handling (scratch/dir/worktree), good summary + metadata shapes, claim verification, heartbeats, retry diagnostics, block strategies, handoff patterns, and troubleshooting board failures.

**Core lifecycle (auto-injected via KANBAN_GUIDANCE):**
1. `kanban_show` — orient on the task
2. Work in `$HERMES_KANBAN_WORKSPACE`
3. Heartbeat progress periodically
4. `kanban_complete(summary=..., metadata=...)` or `kanban_block(reason=...)`

**Do NOT:**
- Call `delegate_task` instead of `kanban_create`
- Call `clarify` (no live user) — use `kanban_block` instead
- Modify files outside workspace
- Complete a task you didn't finish

## CLI Commands

```bash
hermes kanban init              # Initialize board
hermes kanban create <title>    # Create task
hermes kanban list              # List tasks
hermes kanban show <id>         # Show task details
hermes kanban comment <id>      # Add comment
hermes kanban complete <id>     # Complete task
hermes kanban block <id>        # Block task (needs human input)
hermes kanban unblock <id>      # Unblock task
hermes kanban archive <id>      # Archive completed task
hermes kanban tail <id>         # Live follow mode
hermes kanban reclaim <id>      # Abort worker, reset to ready
hermes kanban reassign <id> <profile>  # Switch profile
hermes kanban stats             # Board statistics
```

## Pitfalls

- **Inventing profile names that don't exist** — dispatcher silently fails
- **Bundling independent lanes into one card** — create separate cards
- **Over-linking because of wording** — "finally check X" may be parallel
- **Forgetting dependency links** — children start too early
- **Task state can change between dispatch and startup** — always `kanban_show` first
- **Workspace may have stale artifacts** — read comment thread before working
- **Don't rely on CLI when tools are available** — CLI may not exist in containerized backends