---
name: autonomous-coding-agents
description: Delegate coding to external autonomous coding CLIs — Claude Code, OpenAI Codex, and OpenCode. Covers PTY orchestration, tmux sessions, print mode, dialog handling, parallel worktrees, and PR review patterns.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding-agent, delegation, claude-code, codex, opencode, autonomous, orchestration]
    related_skills: [hermes-agent, subagent-delegation]
---

# Autonomous Coding Agents

Delegate coding tasks to external autonomous coding agent CLIs. This umbrella covers three agents and the shared orchestration patterns (PTY, tmux, print mode, dialog handling, parallel worktrees).

| Agent | CLI | Provider | Skill File |
|-------|-----|----------|------------|
| Claude Code | `claude` | Anthropic | `references/claude-code.md` |
| OpenAI Codex | `codex` | OpenAI | `references/codex.md` |
| OpenCode | `opencode` | OpenCode AI | `references/opencode.md` |

## Quick Start — Pick Your Mode

### Print Mode (preferred for one-shot tasks)

Runs a task without entering the interactive TUI. Clean, scriptable.

```bash
# Claude Code
claude -p 'Add error handling to API calls' --allowedTools 'Read,Edit' --max-turns 10

# Codex
codex exec 'Add dark mode toggle to settings'

# OpenCode
opencode run 'Add retry logic to API calls'
```

### Interactive PTY via tmux

For multi-turn iterative work (refactor → review → fix → test cycle):

```bash
# Start tmux session
tmux new-session -d -s coding-task -x 140 -y 40

# Launch agent inside
tmux send-keys -t coding-task 'cd /path/to/project && claude' Enter
# ... or codex, or opencode
```

## Shared Orchestration Patterns

### Dialog Handling (Claude Code)

When launching interactive Claude Code, two dialogs appear on first run:

1. **Workspace Trust** — default is `1. Yes` → send `Enter`
2. **Permissions Warning** (with `--dangerously-skip-permissions`) — default is WRONG (`1. No, exit`) → send `Down` then `Enter`

```bash
tmux send-keys -t session-name Enter                                 # trust dialog
tmux send-keys -t session-name Down && sleep 0.3 && tmux send-keys Enter  # permissions
```

### Background Long Tasks

```bash
terminal(command="codex exec --full-auto 'Refactor auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id — monitor with process(action="poll|log", session_id="<id>")
```

### Parallel Worktrees

For fixing multiple issues simultaneously:

```bash
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main
terminal(command="codex --yolo exec 'Fix issue #78'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99'", workdir="/tmp/issue-99", background=true, pty=true)
```

### PR Review Patterns

```bash
# Quick review (print mode)
git diff main...feature | claude -p 'Review this diff for bugs and security issues' --max-turns 1

# Codex temp clone
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42
codex review --base origin/main

# OpenCode PR review
opencode pr 42

# Batch PR reviews with worktrees
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'
terminal(command="codex exec 'Review PR #86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87'", workdir="~/project", background=true, pty=true)
```

## Per-Agent References

### Claude Code (`references/claude-code.md`)

- CLI flags: `-p`, `--max-turns`, `--output-format json`, `--json-schema`, `--model`, `--effort`, `--allowedTools`, `--bare`, `--dangerously-skip-permissions`
- Structured JSON output with session_id, cost tracking, token usage
- Stream-json mode for real-time output
- Session continuation (`--continue`, `--resume`, `--fork-session`)
- Custom subagents, MCP servers, hooks
- CLAUDE.md project context files
- TUI slash commands: `/review`, `/plan`, `/compact`, `/effort`, `/model`, `/init`
- Smart context management: monitor with `/context`, compact at >70%

### OpenAI Codex (`references/codex.md`)

- CLI flags: `exec`, `--full-auto`, `--yolo`, `--sandbox danger-full-access`
- Hermes gateway caveat: bubblewrap errors in service context
- Key tips: always use `pty=true`, git repo required, use `exec` for one-shots

### OpenCode (`references/opencode.md`)

- CLI flags: `run`, `-c` (continue), `--model`, `--agent`, `--format json`, `--thinking`
- Binary resolution: `which -a opencode` to find the right binary
- Key tips: `/exit` is NOT valid — use Ctrl+C or process kill
- Session management: `opencode session list`, `opencode stats`

## Rules for All Agents

1. **Prefer print mode** (`-p`, `exec`, `run`) for single tasks — cleaner, no dialog handling
2. **Use tmux for interactive multi-turn work** — only reliable way to orchestrate TUI agents
3. **Always set `workdir`** — keep the agent focused on the right project
4. **Set `--max-turns` in print mode** — prevents infinite loops
5. **Monitor background sessions** — use `process(action="poll"|"log")` or `tmux capture-pane`
6. **Clean up tmux sessions** — `tmux kill-session -t <name>` when done
7. **Use `--allowedTools`** — restrict capabilities to what the task needs
8. **Verify results** — check git diff, run tests after the agent completes
9. **Use worktrees for parallel work** — avoid git conflicts between concurrent agents
10. **Monitor context health** — compact when usage exceeds 70%

## Pitfalls

- Interactive mode requires tmux — `pty=true` alone isn't enough for multi-turn
- Claude Code's `--dangerously-skip-permissions` dialog defaults to "No, exit" — must navigate
- Codex needs a git repo — use `mktemp -d && git init` for scratch work
- OpenCode `/exit` opens agent selector instead of exiting — use Ctrl+C
- Parallel agents in the same working directory cause git conflicts — use worktrees
- Print mode `--max-turns` is print-mode only for Claude; ignored in interactive
- Session resumption requires same working directory
- Background tmux sessions persist after task completion — always clean up