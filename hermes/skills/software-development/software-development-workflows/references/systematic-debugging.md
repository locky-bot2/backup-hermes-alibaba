# Systematic Debugging — Full 4-Phase Methodology

**The Iron Law:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

## Phase 1: Root Cause Investigation

Before attempting any fix:
1. **Read error messages carefully** — line numbers, file paths, error codes
2. **Reproduce consistently** — can you trigger it reliably every time?
3. **Check recent changes** — `git log --oneline -10`, `git diff`
4. **Gather evidence in multi-component systems** — add diagnostic instrumentation at component boundaries
5. **Trace data flow** — where does the bad value originate? Trace upstream

```bash
# Recent commits
git log --oneline -10
# Uncommitted changes
git diff
# Specific file history
git log -p --follow src/problematic_file.py | head -100
# Find function references
search_files("function_name(", path="src/", file_glob="*.py")
```

## Phase 2: Pattern Analysis

1. Find working examples in the same codebase
2. Compare against references — read completely, don't skim
3. Identify differences between working and broken
4. Understand dependencies

## Phase 3: Hypothesis and Testing

1. Form a single hypothesis: "I think X is the root cause because Y"
2. Test minimally — one variable at a time
3. If it doesn't work, form NEW hypothesis — don't add more fixes
4. If you don't understand, say so and research more

## Phase 4: Implementation

1. Create failing test case first (use TDD)
2. Implement single fix — ONE change at a time
3. Verify fix and no regressions — `pytest tests/ -q`
4. **Rule of Three:** If 3+ fixes failed → STOP and question the architecture

## Red Flags

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "One more fix attempt" (after 2+ failures)
- Each fix reveals a new problem in a different place

## With delegate_task

For complex multi-component debugging, dispatch investigation subagents:
```python
delegate_task(
    goal="Investigate why test fails",
    context="Follow systematic debugging: read errors, reproduce, trace flow",
    toolsets=['terminal', 'file']
)
```

## When Terminal/execute_code Are Blocked

1. Use file-only tools first (read_file, search_files, web_extract)
2. Form high-confidence hypothesis from config files, logs, and SQLite DBs
3. Give user exact commands to run from their terminal
4. Prefer delegation with `terminal` toolset