# OpenAI Codex — Full Reference

CLI binary: `codex` (npm install -g @openai/codex)

## Prerequisites
- `npm install -g @openai/codex`
- Auth: `OPENAI_API_KEY` or Codex OAuth (`hermes auth add openai-codex`)
- Must run inside a git repository
- Always use `pty=true` in terminal calls — Codex is an interactive app

## Key CLI Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |
| `--sandbox danger-full-access` | No sandbox; useful when bubblewrap breaks |

## One-Shot Tasks

```bash
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)

# Scratch work (needs git repo)
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode

```bash
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Monitor:
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
# Send input if Codex asks a question:
process(action="submit", session_id="<id>", data="yes")
```

## Parallel Issue Fixing with Worktrees

```bash
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main
terminal(command="codex --yolo exec 'Fix issue #78'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99'", workdir="/tmp/issue-99", background=true, pty=true)
```

## PR Reviews

```bash
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42
codex review --base origin/main
```

## Gateway Caveat

In service context (Telegram, API server), bubblewrap/user-namespace may fail:
```bash
codex exec --sandbox danger-full-access "<task>"
```

## Pitfalls
- Always `pty=true` — Codex hangs without
- Git repo required — use `mktemp -d && git init` for scratch
- `exec` for one-shots — `codex exec "prompt"` runs and exits
- `--full-auto` for building
- Background for long tasks with `process` monitoring
- Don't interfere — let it work, only monitor with poll/log