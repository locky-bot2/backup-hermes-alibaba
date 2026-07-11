# Subagent Delegation Patterns

Practical patterns for using `delegate_task` in Hermes, including the script-write-then-execute pattern and team-agent workflows.

## When to Use delegate_task

| Use it for | Don't use it for |
|------------|-----------------|
| Reasoning-heavy subtasks (debugging, code review, research) | Mechanical multi-step work → `execute_code` |
| Tasks that flood your context with intermediate data | Single tool call → just call the tool |
| Parallel independent workstreams | Tasks needing user interaction (subagents can't use `clarify`) |
| Team-agent workflows (Charmander/Squirtle/Pikachu) | Durable long-running work → `cronjob` or `terminal(background=true)` |

## Critical Constraint: Subagents Cannot Run Shell Commands

Subagents (leaf or orchestrator) CANNOT use `terminal` or `execute_code`. They can write files but not execute them.

### What Works
- `write_file`, `read_file`, `search_files`, `patch`
- `web_search`, `web_extract`
- `browser_navigate`, `browser_*`
- `skill_view`, `skills_list`

### What Does NOT Work
- `execute_code` (blocked for all subagents)
- Terminal/command execution (blocked)
- `delegate_task` (blocked for leaf subagents)
- `memory` (blocked)
- `clarify` (blocked)

### The Script-Write-Then-Execute Pattern

For tasks requiring shell execution (git push, npm build, deploy):

1. **Subagent writes a self-contained script** via `write_file` — bash/Python, fully idempotent
2. **Subagent returns the script path** in its summary
3. **Parent runs the script** via `execute_code` with `subprocess.run([...])` or terminal

```python
# Parent delegates
delegate_task(
    goal="Write deploy script for project at /path/to/project",
    context="... path, repo name, token location ...",
    toolsets=["file"]
)
# → Subagent writes /path/to/project/deploy.sh
# → Parent reads the file to verify, then runs: bash /path/to/project/deploy.sh
```

## Context is Everything

Subagents have **NO memory** of your conversation. Pass all relevant info via `context`:
- File paths (absolute preferred), error messages, stack traces
- Project structure, user preferences, constraints
- Previous attempts and what failed

## Verification Pattern

**Subagent summaries are self-reports, not verified facts.** Always verify:
- File writes → `read_file` to confirm content
- HTTP operations → fetch URL, check HTTP status
- Git operations → check `git status`, verify remote
- Test results → re-run tests after subagent returns

## Toolsets for Common Task Types

| Task | Toolsets | Reason |
|------|----------|--------|
| Code writing | `['file']` | Write files, no network |
| Research | `['web', 'file']` | Search + save to file |
| Testing | `['file']` | Read code, write tests |
| DevOps/Deploy | `['file', 'web']` | Write scripts (web for API calls) |
| Code review | `['file']` | Read files, write review |

## Team Agent Profiles

| Agent | Profile | Role |
|-------|---------|------|
| Charmander | Testing profile | Writes unit/integration tests |
| Squirtle | DevOps profile | Git, Docker, CI/CD, deployment |
| Pikachu | Coding profile | Writes application code |

### Delegation Rules
1. Delegate directly — skip "Ash presents to the team" loop
2. Fix provider config first — verify the profile's `config.yaml` has a `provider` field
3. One task per agent — delegate the most relevant profile
4. Verify after delegation — run tests after Charmander, check git after Squirtle

## Batch Delegation

```python
delegate_task(tasks=[
    {"goal": "Write tests for module X", "toolsets": ["file"]},
    {"goal": "Create Dockerfile for project Y", "toolsets": ["file", "web"]},
])
```

Max 3 concurrent tasks. Results returned together.

## Pitfalls

1. **Subagent writes script but can't run it** — parent MUST execute after delegation returns
2. **No GitHub token on fresh systems** — check for `GITHUB_TOKEN` or `gh` auth before delegating deploy work
3. **Per-profile provider config** — each profile needs its own `provider` field; not inherited from default
4. **Language/tone contamination** — pass language preferences explicitly in `context`
5. **Self-contained goals** — never reference "the file I mentioned earlier"; spell everything out
6. **Don't trust happy-path summaries** — always verify with file read, HTTP check, or test re-run

See `references/weather-app-deploy-session.md` in this skill directory for a real session walkthrough.