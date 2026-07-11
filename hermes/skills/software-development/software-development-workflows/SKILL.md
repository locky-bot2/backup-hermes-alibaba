---
name: software-development-workflows
description: Software development methodology — systematic debugging, test-driven development, pre-commit code review, code simplification via parallel agents, Python debugging (pdb/debugpy), and Node.js inspect debugging.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, tdd, code-review, testing, python-debugging, node-debugging, methodology]
    related_skills: [github, spike, plan]
---

# Software Development Workflows

Complete development methodology umbrella covering debugging, testing, code review, code simplification, and language-specific debugger tools.

## Table of Contents

1. **[Systematic Debugging](#1-systematic-debugging)** — 4-phase root cause investigation
2. **[Test-Driven Development](#2-test-driven-development)** — RED-GREEN-REFACTOR cycle
3. **[Pre-Commit Code Review](#3-pre-commit-code-review)** — Verification pipeline with independent reviewer
4. **[Code Simplification](#4-code-simplification)** — Parallel 3-agent cleanup
5. **[Python Debugger](#5-python-debugger)** — pdb, debugpy, remote-pdb
6. **[Node.js Debugger](#6-nodejs-debugger)** — node inspect, CDP, heap snapshots
7. **[Web App Integration Testing](#7-web-app-integration-testing)** — vitest + happy-dom patterns
8. **[Web QA Testing](#8-web-qa-testing-dogfood)** — browser-based exploratory QA
9. **[Spike / Feasibility Testing](#9-spike--feasibility-testing)** — throwaway experiments

---

## 1. Systematic Debugging

See `references/systematic-debugging.md` for the full 4-phase process.

**The Iron Law:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

### Four Phases

| Phase | Activity | Success |
|-------|----------|---------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

### Debugging Checklist

- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Root cause hypothesis formed before fixing

### Red Flags (STOP and return to Phase 1)

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- 3+ fix attempts failed → question the architecture

### When Terminal/execute_code Are Blocked

Use file-only tools (read_file, search_files) for diagnosis. Give the user exact commands to run.

---

## 2. Test-Driven Development

See `references/test-driven-development.md` for the full methodology.

**The Iron Law:** NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.

### RED-GREEN-REFACTOR Cycle

**RED** — Write one minimal failing test:
```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        nonlocal attempts; attempts += 1
        if attempts < 3: raise Exception('fail')
        return 'success'
    assert retry_operation(operation) == 'success'
    assert attempts == 3
```

**Verify RED** — Watch it fail, confirm failure reason is "feature missing"
**GREEN** — Minimal code to pass (cheating OK: hardcode, copy-paste)
**Verify GREEN** — Run ALL tests, check no regressions
**REFACTOR** — Clean up, keep tests green throughout

### Common Rationalizations (all traps)

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Test takes 30 seconds |
| "I'll test after" | Tests passing immediately prove nothing |
| "Already manually tested" | Ad-hoc ≠ systematic, no record |
| "Deleting X hours is wasteful" | Sunk cost fallacy |
| "TDD is dogmatic, I'm pragmatic" | TDD IS pragmatic — finds bugs before commit |

---

## 3. Pre-Commit Code Review

See `references/requesting-code-review.md` for the full verification pipeline.

**Core principle:** No agent should verify its own work. Fresh context finds what you miss.

### Pipeline

1. **Get the diff** — `git diff --cached` or `git diff main...HEAD`
2. **Static security scan** — grep for hardcoded secrets, SQL injection, eval/exec
3. **Baseline tests** — run tests before + after changes to find regressions
4. **Self-review checklist** — no debug prints, no leaked secrets, input validation
5. **Independent reviewer subagent** — `delegate_task` with ONLY the diff
6. **Evaluate results** — pass → commit; fail → auto-fix loop
7. **Auto-fix** (max 2 cycles) — spawn fix-only subagent, re-verify
8. **Commit** — `git add -A && git commit -m "[verified] <description>"`

### Review Output Format

```
## Code Review Summary
### Critical — src/auth.py:45 — SQL injection
### Warnings — src/models/user.py:23 — Plaintext password
### Suggestions — src/utils/helpers.py:8 — Duplicated logic
### Looks Good — Clean middleware, good test coverage
```

---

## 4. Code Simplification

See `references/simplify-code.md` for the full workflow.

**Core principle:** Three narrow reviewers beat one broad reviewer. Run concurrently.

### Three Reviewers (parallel)

| Reviewer | Focus | What they check |
|----------|-------|-----------------|
| **Code Reuse** | Duplicate functionality | Existing utilities, helpers to use instead |
| **Code Quality** | Redundant state, parameter sprawl, copy-paste, leaky abstractions |
| **Efficiency** | N+1 patterns, missed concurrency, hot-path bloat, TOCTOU |

### Process

1. **Phase 1** — Capture the diff (`git diff` or `git diff HEAD~1`)
2. **Phase 2** — Launch 3 reviewers via `delegate_task` batch mode
3. **Phase 3** — Aggregate, dedupe, discard false positives, apply fixes, verify with tests

**Pitfalls:** Don't fan out wider than 3. Give WHOLE diff to each. Apply ≠ rewrite. Respect project conventions.

---

## 5. Python Debugger

See `references/python-debugpy.md` for full pdb + debugpy reference.

| Tool | When |
|------|------|
| `breakpoint()` + pdb | Local, interactive, simplest |
| `python -m pdb` | Launch script under pdb with no source edits |
| `debugpy` | Remote / headless / attach to running process (DAP) |
| `remote-pdb` | Terminal-friendly alternative to debugpy's DAP |

### Quick Recipes

```bash
# Local breakpoint — add to source, run normally
breakpoint()  # remove before commit!
rg -n 'breakpoint\(\)' --type py  # pre-commit check

# Launch script under pdb
python -m pdb path/to/script.py arg1 arg2

# pytest with pdb
python -m pytest tests/foo_test.py::test_bar --pdb -p no:xdist

# remote-pdb (cleanest for agents)
pip install remote-pdb
# In code:
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)
# Terminal:
nc 127.0.0.1 4444  # get (Pdb) prompt
```

**Pitfalls:** pytest-xdist + pdb silently hangs. `PYTHONBREAKPOINT=0` disables all breakpoints. pdb doesn't follow multiprocessing forks.

---

## 6. Node.js Debugger

See `references/node-inspect-debugger.md` for full reference.

| Tool | When |
|------|------|
| `node inspect` | Built-in, zero install, CLI REPL |
| CDP via `chrome-remote-interface` | Scriptable automation, heap/cpu profiles |

### Quick Recipes

```bash
# Launch paused on first line
node inspect path/to/script.js
node --inspect-brk $(which tsx) path/to/script.ts

# Attach to running process
kill -SIGUSR1 <pid>
node inspect -p <pid>

# Debug commands at (debug) prompt:
# sb('file.js', 42) — set breakpoint
# sb('functionName') — break on function entry
# bt — backtrace
# repl — evaluate JS in current scope
# c, n, s, o — continue, next, step, out

# Heap snapshot via CDP
node --inspect-brk=9229 target.js &
node /tmp/cdp-debug.js  # uses chrome-remote-interface
```

**Pitfalls:** Breakpoints hit emitted JS, not `.ts`. `--inspect` vs `--inspect-brk`. Port collisions (default 9229). Child processes need their own `--inspect`. Always bind to 127.0.0.1.

---

## 7. Web App Integration Testing

See `references/vitest-happy-dom-setup.md` and `references/dom-rendering-helpers.md` for vitest + happy-dom setup and rendering helpers. Also `references/api-mocking-patterns.md` for fetch mocking, `references/server-http-testing.md` and `references/server-inline-testing.md` for server testing.

**Key layers:**

| Layer | What It Tests | Tool |
|-------|--------------|------|
| Server HTTP | Route handling, status codes, MIME types | Node `http` module |
| DOM Rendering | Data → HTML elements, template output | `happy-dom` in vitest |
| State Management | View transitions (empty→loading→dashboard→error) | `happy-dom` in vitest |
| Async Data Flow | Fetch calls → loading state → render/error | Mocked fetch + vitest |

**Port conflicts:** Use `server.listen(0)` (random port) to avoid "address in use" in parallel test runs. Kill child processes in `afterAll`.

---

## 8. Web QA Testing (Dogfood)

See `references/issue-taxonomy.md` for issue severity/category taxonomy, and `templates/dogfood-report-template.md` for the report format.

**5-phase workflow:** Plan → Explore → Collect Evidence → Categorize → Report.

Use the browser toolset to navigate, interact, and capture issues:
```bash
browser_navigate(url="https://example.com")
browser_snapshot()
browser_console(clear=true)           # JS errors after every action
browser_vision(question="Describe layout issues", annotate=true)
```

Always check console after navigation and after every significant interaction. Silent JS errors are high-value findings.

---

## 9. Spike / Feasibility Testing

See `references/spike-methodology.md` for the full workflow.

**Use spikes for:** validating feasibility before committing to a real build — POCs, comparisons, surfacing unknowns.

**Core loop:** `decompose → research → build → verdict`

| Outcome | Meaning |
|---------|---------|
| VALIDATED | Core question answered yes, with evidence |
| PARTIAL | Works under constraints X, Y, Z |
| INVALIDATED | Doesn't work — this is a successful spike |

**Directory layout:** `spikes/NNN-descriptive-name/README.md` per spike.

**Key rule:** Spikes are disposable by design. Throw them away once they've paid their debt.