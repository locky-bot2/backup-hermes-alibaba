# Kanban Orchestrator — Full Playbook

> Load this via `skill_view("kanban", "references/orchestrator-playbook.md")` for complete decomposition guidance.

## Step 0: Discover Available Profiles

```bash
hermes profile list
```

Cache the result for the conversation. Do NOT invent profile names — dispatcher silently drops unknown assignees.

## When to Create Kanban Tasks (vs. just working)

1. Multiple specialists needed
2. Work should survive crash/restart
3. User might want to interject
4. Multiple subtasks can run in parallel
5. Review/iteration is expected
6. Audit trail matters

If none apply → use `delegate_task` or answer directly.

## Anti-Temptation Rules

- Do NOT execute the work yourself
- For every concrete task → create a Kanban card
- Split multi-lane requests before creating cards
- Run independent lanes in parallel
- Never create dependent work as independent ready cards — use `parents=[]`
- If no specialist fits → ask the user

## Decomposition Playbook

### Step 1 — Understand the goal
### Step 2 — Sketch the task graph
### Step 3 — Create tasks and link

```python
t1 = kanban_create(title="research: cost", assignee="<profile>", body="...", ...)[\"task_id\"]
t2 = kanban_create(title="research: perf", assignee="<profile>", body="...", ...)[\"task_id\"]
t3 = kanban_create(title="synthesize", assignee="<profile>", body="...", parents=[t1, t2])[\"task_id\"]
```

### Step 4 — Complete your own task
### Step 5 — Report back to user

## Common Patterns

- **Fan-out + fan-in**: N research cards, one synthesis with all as parents
- **Parallel impl + validation**: Implementer + explorer in parallel, review depends on both
- **Pipeline with gates**: planner → implementer → reviewer
- **Same-profile queue**: N tasks, same profile, no deps = serialized processing
- **Human-in-the-loop**: `kanban_block()` waits for input

## Goal-Mode Cards (persistent workers)

Pass `goal_mode=True` to `kanban_create` for open-ended cards where one turn rarely finishes.

```python
kanban_create(
    title="Translate docs to French",
    body="Acceptance: every page translated, no English left.",
    assignee="<profile>",
    goal_mode=True,
    goal_max_turns=15,
)
```

## Recovering Stuck Workers

| Action | Command | Effect |
|--------|---------|--------|
| Reclaim | `hermes kanban reclaim <id>` | Abort + reset to ready |
| Reassign | `hermes kanban reassign <id> <new-profile> --reclaim` | Switch profile |
| Change model | `hermes -p <profile> model` | Edit config, then reclaim |

## Pitfalls

- Inventing profile names → dispatcher silently drops
- Bundling independent lanes into one card
- Over-linking because of wording
- Forgetting dependency links
- Argument order for kanban_link: `parent_id` first, `child_id` second
- `kanban_create` returns error "board not found" → run `hermes kanban init`
- Cards stay in `todo` forever → dispatcher not running or no matching profiles