# Gateway Diagnostics

Systematic root-cause analysis when the messaging gateway is unresponsive, silent, or crash-looping.

## Quick Triage

| Symptom | Likely cause | Quick fix |
|---------|-------------|-----------|
| Platform says "connected" but no response for hours | Model/provider stuck; gateway hung on a bad turn | Restart gateway (`systemctl --user restart hermes-gateway` or kill PID) |
| Model returns garbled/refusal text (Chinese error, "I cannot", empty) | Provider issue — model down, rate-limited, or producing bad output | Switch model (`hermes model` or edit `config.yaml`) |
| Gateway process dead (no PID) | s6 auto-restart should fire in seconds | Check `systemctl --user status hermes-gateway`; if crash-looping, check logs for OOM or import error |

## Full Diagnosis Workflow

### 1. Check Gateway State File

`gateway_state.json` in Hermes home:
```json
{
  "pid": 7204,
  "gateway_state": "running",
  "platforms": {
    "telegram": {
      "state": "connected",
      "error_code": null,
      "updated_at": "..."     // stale timestamp → hung process
    }
  }
}
```

Key checks:
- `gateway_state` = `"running"`
- Platform state = `"connected"` with no errors
- `updated_at` recent — hours-old with alive PID = hung process

### 2. Verify Process Is Alive

```python
import os
try:
    os.kill(pid, 0)
    print("PID alive")
except OSError:
    print("PID dead — s6 should auto-restart")
```

List Hermes processes via `/proc` to see s6 supervision hierarchy. Gateway PID alive ≠ healthy — it can be stuck on a model call.

### 3. Check Gateway Logs

s6-supervised gateways write to `~/.hermes/logs/gateways/default/current`. Look for:
- Restart frequency (crash loop if every few minutes)
- "Stream interrupted by network error" — transient provider issues
- "Iteration budget exhausted" — excessive tool calls
- Last entry age — silent for hours with alive PID = hung

### 4. Query Sessions for Affected Platform

```python
import sqlite3
conn = sqlite3.connect("~/.hermes/state.db")
c = conn.cursor()
c.execute("""
    SELECT id, title, source, started_at, ended_at, message_count
    FROM sessions WHERE source = 'telegram' ORDER BY started_at DESC LIMIT 5
""")
```

No `ended_at` = session still active (waiting on model). Recent session with few messages = user sent message but got no response.

### 5. Trace the Last Conversation

Pull all messages from the latest active session and look for:
- Assistant response empty or refusal ("I cannot provide...", Chinese error)
- Tool results that failed or timed out
- Excessive tool calls before bad answer

### 6. Root Cause Analysis

| Finding | Root Cause | Action |
|---------|-----------|--------|
| Model gives broken/refusal responses | Provider issue | Switch model/provider; check OpenRouter status |
| PID alive but state/logs stale for hours | Process hung on model call | Kill PID; s6 restarts |
| Gateway crash loop (restarting every few min) | Config error, missing env var | `hermes doctor --fix` |
| Platform disconnected with error | Invalid token, revoked access | Re-authenticate (`hermes gateway setup`) |
| Gateway running but no platform connected | Platform not configured | Check `platform_toolsets` in config and .env |

## Pitfalls

- **"Connected" ≠ "responsive"** — correlate with log age and session state, don't trust state flags alone
- **Stale state file** — cross-check PID liveness and log timestamps
- **s6 hides crash-to-restart** — check log timestamps for gaps; PID may briefly reference old process
- **Model failures look like gateway failures** — trace the last conversation's messages before concluding the gateway itself is broken
- **`.env` is unreadable** by Hermes tooling; verify Telegram bot token via `hermes gateway setup`

## Reference: Real Example

See `references/telegram-model-failure-example.md` in this skill directory for a complete reproduction of a Telegram gateway hung after model refusal (deepseek/deepseek-v4-flash on OpenRouter, Jun 2026).