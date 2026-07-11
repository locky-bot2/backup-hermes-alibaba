# Code Simplification — Parallel 3-Agent Cleanup

**Core principle:** Three narrow reviewers beat one broad reviewer. Run concurrently.

## Phase 1 — Capture the diff

```bash
git diff                          # uncommitted changes
git diff HEAD                     # +staged
git diff HEAD~1                   # last commit
git diff main...HEAD              # branch changes
```

## Phase 2 — Launch Three Reviewers (parallel via batch mode)

### Reviewer 1 — Code Reuse
Check for: new functions duplicating existing; hand-rolled logic that a utility already does; missing calls to existing helpers.

### Reviewer 2 — Code Quality
Check for: redundant state, parameter sprawl, copy-paste-with-variation, leaky abstractions, stringly-typed code.

### Reviewer 3 — Efficiency
Check for: unnecessary work (redundant computation, N+1), missed concurrency, hot-path bloat, TOCTOU, memory leaks.

## Phase 3 — Aggregate and Apply

1. Merge findings, dedup overlapping
2. Discard false positives
3. Resolve conflicts: correctness > focus > readability > micro-perf
4. Apply with patch/write_file
5. Verify tests still pass
6. Summarize changes

## Pitfalls
- Don't fan out wider than ~3
- Give WHOLE diff to each reviewer
- Reviewers must provide file:line evidence
- Apply ≠ rewrite — scope edits to diff-touched code
- Large diffs blow context — scope down before delegating