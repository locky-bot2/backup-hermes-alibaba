# Test-Driven Development — Full Methodology

**The Iron Law:** NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.

## RED — Write Failing Test

Requirements:
- One behavior per test
- Clear descriptive name ("and" in name? Split it)
- Real code, not mocks (unless unavoidable)
- Name describes behavior, not implementation

```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        nonlocal attempts; attempts += 1
        if attempts < 3: raise Exception('fail')
        return 'success'
    result = retry_operation(operation)
    assert result == 'success'
    assert attempts == 3
```

## Verify RED — Watch It Fail (mandatory)

```bash
pytest tests/test_feature.py::test_specific_behavior -v
```

Confirm: fails for expected reason (feature missing), not errors from typos.

## GREEN — Minimal Code

Write the simplest code to pass. Nothing more. Cheating is OK:
- Hardcode return values
- Copy-paste
- Duplicate code

## Verify GREEN

```bash
pytest tests/test_feature.py::test_specific_behavior -v
pytest tests/ -q   # All tests — check regressions
```

## REFACTOR — Clean Up

Only after green. Remove duplication, improve names, extract helpers. Keep tests green throughout. If tests fail during refactor → undo, take smaller steps.

## Repeat

Next failing test for next behavior. One cycle at a time.

## Common Rationalizations (ALL are traps)

- "Too simple to test" — simple code breaks, test takes 30 seconds
- "I'll test after" — tests passing immediately prove nothing
- "Already manually tested" — ad-hoc ≠ systematic, no record
- "Deleting X hours is wasteful" — sunk cost fallacy
- "Keep as reference" — you'll adapt it, that's testing after

## Red Flags — Delete Code and Restart

- Code before test
- Test after implementation
- Test passes immediately on first run
- "Just this once"

## When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write the wished-for API, write assertion first |
| Test too complicated | Design too complicated, simplify the interface |
| Must mock everything | Code too coupled, use dependency injection |

## With delegate_task

```python
delegate_task(
    goal="Implement [feature] using strict TDD",
    context="Follow TDD: write failing test FIRST, verify it fails, implement, verify passes",
    toolsets=['terminal', 'file']
)
```