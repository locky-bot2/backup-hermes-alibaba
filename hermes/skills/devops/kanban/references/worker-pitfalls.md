# Kanban Worker — Full Reference

> Load this via `skill_view("kanban", "references/worker-pitfalls.md")` for worker guidance.

## Workspace Handling

| Kind | Behavior | How to work |
|------|----------|-------------|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely |
| `dir:<path>` | Shared persistent dir | Treat like long-lived state |
| `worktree` | Git worktree at resolved path | Commit work here |

## Good Summary + Metadata Shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14, "tests_passed": 14,
        "decisions": ["user_id primary, IP fallback"],
    },
)
```

**Research task:**
```python
kanban_complete(
    summary="3 libraries reviewed; vLLM wins on throughput",
    metadata={"recommendation": "vLLM", "benchmarks": {"vllm": 1.0, "sglang": 0.87}},
)
```

**Review task (block for human):**
```python
kanban_comment(body="review-required handoff: {\"changed_files\": [...], \"tests_run\": 14}")
kanban_block(reason="review-required: rate limiter shipped — needs eyes before merging")
```

## Claiming Cards You Created

Only list ids you captured from a successful `kanban_create` return value:
```python
c1 = kanban_create(title="fix SQL injection", assignee="security-worker")
kanban_complete(summary="Done", created_cards=[c1["task_id"]])
```

NEVER invent ids from prose, paste from earlier runs, or claim cards another worker created.

## Block Reasons That Get Answered Fast

Bad: `"stuck"` — no context. Good: `"Rate limit key choice: IP or user_id?"`

Leave longer context as a `kanban_comment()` — the block message appears in dashboards.

## Heartbeats Worth Sending

Good: `"epoch 12/50, loss 0.31"`, `"processed 1.2M/2.4M rows"`.
Bad: `"still working"`, empty notes, sub-second intervals.

## Retry Scenarios

- `outcome: "timed_out"` → chunk the work
- `outcome: "crashed"` → OOM/segfault, reduce memory
- `outcome: "spawn_failed"` → profile config issue
- `outcome: "reclaimed"` → operator archived it; check status

## Board Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `kanban_create` returns "board not found" | Board never initialized | `hermes kanban init` |
| Cards stay in `todo` | Dispatcher not running or wrong assignee | Check logs, verify profiles |
| `kanban_create` hangs | Approval system blocking execute_code | Use file tools for diagnosis |

## Tenant Isolation

If `$HERMES_TENANT` is set, prefix memory entries with tenant: `business-a: Acme is our biggest customer`