# OpenCode — Full Reference

CLI binary: `opencode` (npm install -g opencode-ai@latest or `brew install anomalyco/tap/opencode`)

## Prerequisites
- `npm i -g opencode-ai@latest`
- Auth: `opencode auth login` or set provider env vars
- Verify: `opencode auth list`
- Git repo for code tasks (recommended)

## Key CLI Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `-c, --continue` | Continue the last session |
| `-s, --session <id>` | Continue a specific session |
| `--agent <name>` | Choose agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output |
| `-f, --file <path>` | Attach file to the message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |

## One-Shot Tasks

```bash
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")

# With context files
terminal(command="opencode run 'Review config security' -f config.yaml -f .env.example", workdir="~/project")

# Show thinking
terminal(command="opencode run 'Debug CI failures' --thinking", workdir="~/project")

# Force model
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

## Interactive Sessions (Background)

```bash
terminal(command="opencode", workdir="~/project", background=true, pty=true)
# Send prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow")
# Monitor
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
# Exit (Ctrl+C, NOT /exit!)
process(action="write", session_id="<id>", data="\x03")
```

## TUI Keybindings

| Key | Action |
|-----|--------|
| Enter | Submit message |
| Tab | Switch agents (build/plan) |
| Ctrl+P | Command palette |
| Ctrl+X L | Switch session |
| Ctrl+X M | Switch model |
| Ctrl+X N | New session |
| Ctrl+C | Exit |

## PR Review

```bash
opencode pr 42
```

## Session & Cost Management

```bash
opencode session list
opencode stats --days 7
```

## Pitfalls
- Interactive TUI requires `pty=true` — `opencode run` does NOT
- `/exit` is NOT valid — it opens agent selector. Use Ctrl+C
- PATH mismatch can select wrong binary: `which -a opencode`
- Enter may need to be pressed twice in TUI
- Don't share working directory across parallel sessions