# Claude Code — Full Reference

CLI binary: `claude` (npm install -g @anthropic-ai/claude-code)

## Prerequisites
- `npm install -g @anthropic-ai/claude-code`
- Auth: `claude` (browser OAuth) or `ANTHROPIC_API_KEY`
- Console auth: `claude auth login --console`
- Health: `claude doctor`, version: `claude --version`

## Key CLI Flags

| Flag | Effect |
|------|--------|
| `-p "query"` | Print mode — non-interactive, exits when done |
| `-c, --continue` | Resume most recent conversation in this dir |
| `-r, --resume <id>` | Resume specific session |
| `--fork-session` | Create new session ID when resuming |
| `--output-format json\|stream-json` | Structured output |
| `--max-turns <n>` | Limit agentic loops (print mode only) |
| `--model sonnet\|opus\|haiku` | Model selection |
| `--effort low\|medium\|high\|max` | Reasoning depth |
| `--allowedTools <tools>` | Whitelist specific tools |
| `--bare` | Skip hooks, plugins, CLAUDE.md, OAuth (fastest startup) |
| `--dangerously-skip-permissions` | Auto-approve ALL tool use |
| `--json-schema <schema>` | Force structured JSON output |
| `--max-budget-usd <n>` | Cap API spend in dollars |
| `--fallback-model <model>` | Auto-fallback when default overloaded |
| `--append-system-prompt <text>` | Add to system prompt |
| `--verbose` | Full turn-by-turn output |

## Print Mode Deep Dive

```bash
# Basic
claude -p 'Add error handling to API calls' --allowedTools 'Read,Edit' --max-turns 10

# Structured JSON output
claude -p 'Analyze auth.py' --output-format json --max-turns 5

# Piped input
cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1
git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1

# Resume session
claude -p 'Continue' --resume <session-id> --max-turns 5
claude -p 'Continue' --continue --max-turns 1

# Bare mode for CI
claude --bare -p 'Run all tests and report' --allowedTools 'Read,Bash' --max-turns 10
```

## Settings Hierarchy

1. CLI flags override everything
2. `.claude/settings.local.json` (personal, gitignored)
3. `.claude/settings.json` (shared, git-tracked)
4. `~/.claude/settings.json` (user global)

## Memory Files (CLAUDE.md)

1. `~/.claude/CLAUDE.md` — global
2. `./CLAUDE.md` — project context (git-tracked)
3. `.claude/CLAUDE.local.md` — personal overrides (gitignored)
4. `.claude/rules/*.md` — modular rules directory

## Structured JSON Output

Returned with `--output-format json`:
```json
{
  "type": "result", "subtype": "success",
  "result": "analysis text...",
  "session_id": "uuid",
  "num_turns": 3,
  "total_cost_usd": 0.0787,
  "usage": { "input_tokens": 5, "output_tokens": 603, ... }
}
```

## TUI Slash Commands

| Command | Purpose |
|---------|---------|
| `/review` | Code review of current changes |
| `/security-review` | Security analysis |
| `/plan` | Plan mode for task planning |
| `/compact` | Compress context to save tokens |
| `/clear` | Wipe conversation history |
| `/context` | Visualize context usage (colored grid) |
| `/cost` | Token usage breakdown |
| `/model` | Switch models mid-session |
| `/effort` | Set reasoning effort |
| `/init` | Create CLAUDE.md |
| `/memory` | Edit CLAUDE.md |
| `/exit` or `Ctrl+D` | End session |

## Cost & Performance Tips

- `--max-turns` prevents runaway loops (start with 5-10)
- `--effort low` for simple tasks (faster, cheaper)
- `--bare` for CI to skip plugin/hook discovery
- `--allowedTools` restricts to what's needed
- `/compact` in interactive when context is large
- Context degradation above 70% — compact proactively
- `--model haiku` for cheap tasks, `--model opus` for complex work
- `--fallback-model haiku` in print mode for overload handling

## Pitfalls

- Interactive mode REQUIRES tmux — print mode preferred
- `--dangerously-skip-permissions` dialog defaults to "No, exit"
- `--max-budget-usd` minimum ~$0.05
- `--max-turns` is print-mode only
- Session resumption requires same directory
- Context degradation is real above 70% usage
- Don't use `--dangerously-skip-permissions` if you can use `--allowedTools` instead