# Node.js Inspect Debugger

## Quick Selection

| Tool | When |
|------|------|
| `node inspect` | Built-in, zero install, CLI REPL |
| CDP via chrome-remote-interface | Scriptable automation, heap/cpu profiles |

## node inspect REPL

```bash
node inspect path/to/script.js
node --inspect-brk $(which tsx) path/to/script.ts
```

| Command | Action |
|---------|--------|
| `c` / `cont` | continue |
| `n` / `next` | step over |
| `s` / `step` | step into |
| `sb('file.js', 42)` | set breakpoint |
| `sb('functionName')` | break on function entry |
| `bt` | backtrace |
| `list(5)` | show source lines |
| `repl` | evaluate JS in current scope |
| `watch('expr')` | auto-evaluate on pause |
| `.exit` | quit |

## Attach to Running Process

```bash
kill -SIGUSR1 <pid>
node inspect -p <pid>

# Start with inspector from beginning
node --inspect script.js           # keep running
node --inspect-brk script.js       # pause on first line
```

## Programmatic CDP (scripting)

```bash
npm i -g chrome-remote-interface
node --inspect-brk=9229 target.js &
node /tmp/cdp-debug.js
```

Driver script pattern: connect to 9229, enable Debugger, set breakpoints via `Debugger.setBreakpointByUrl`, evaluate expressions via `Debugger.evaluateOnCallFrame`.

## Heap Snapshots & CPU Profiles

Use the CDP driver with `HeapProfiler.takeHeapSnapshot` or `Profiler.start`/`stop`.

## Debugging Hermes TUI

```bash
# Find TUI Node PID
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)
kill -SIGUSR1 "$TUI_PID"
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'
node inspect ws://127.0.0.1:9229/<uuid>
```

## Pitfalls
- Breakpoints hit emitted JS, not `.ts` (use dist/ paths or sourcemaps-aware clients)
- `--inspect` vs `--inspect-brk` — use `-brk` if you need breakpoints before code runs
- Port collisions — default 9229, use `--inspect=0` for random port
- Child processes need their own `--inspect`
- Always bind to 127.0.0.1 — `--inspect=0.0.0.0` exposes arbitrary code execution
- `node inspect` requires pty=true in Hermes terminal