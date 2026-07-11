# Pre-Commit Code Verification

Automated verification pipeline before code lands. **No agent should verify its own work.**

## Pipeline

### Step 1 — Get the diff

```bash
git diff --cached  # staged changes
# If empty: git diff, then git diff HEAD~1 HEAD
```

### Step 2 — Static security scan

```bash
# Hardcoded secrets
git diff --cached | grep "^+" | grep -iE "(api_key|secret|password|token)\s*=\s*['\"][^'\"]{6,}['\"]"
# Shell injection
git diff --cached | grep "^+" | grep -E "os\.system\(|subprocess.*shell=True"
# Dangerous eval/exec
git diff --cached | grep "^+" | grep -E "\beval\(|\bexec\("
```

### Step 3 — Baseline tests

Capture failure count BEFORE changes (stash, run, pop). Only NEW failures block commit.

```bash
python -m pytest --tb=no -q 2>&1 | tail -5
which ruff && ruff check . 2>&1 | tail -10
which mypy && mypy . --ignore-missing-imports 2>&1 | tail -10
```

### Step 4 — Self-review checklist

- [ ] No hardcoded secrets
- [ ] Input validation on user data
- [ ] SQL uses parameterized queries
- [ ] No debug print/console.log left
- [ ] New code has tests

### Step 5 — Independent reviewer subagent

```python
delegate_task(
    goal="Independent code review. Return ONLY JSON verdict.",
    context="You have no context about how changes were made. Fail-closed: security_concerns non-empty → passed=false",
    toolsets=["terminal"]
)
```

Returns: `{"passed": bool, "security_concerns": [], "logic_errors": [], "suggestions": [], "summary": "..."}`

### Steps 6-8 — Evaluate → Auto-fix (max 2 cycles) → Commit

```bash
git add -A && git commit -m "[verified] <description>"
```

## Pitfalls
- Empty diff → nothing to verify
- Large diff (>15k chars) → split by file
- Auto-fix introduces new issues → counts as new failure
- No test framework found → skip regression check, reviewer still runs