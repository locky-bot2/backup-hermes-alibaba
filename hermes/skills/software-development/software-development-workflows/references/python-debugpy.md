# Python Debugger (pdb + debugpy + remote-pdb)

## Quick Selection

| Tool | When |
|------|------|
| `breakpoint()` + pdb | Local, interactive, simplest |
| `python -m pdb` | Launch script under pdb with no source edits |
| `debugpy` | Remote/headless/attach to running process (DAP) |
| `remote-pdb` | Terminal-friendly alternative — get (Pdb) via netcat |

## pdb Quick Reference

Inside `(Pdb)` prompt: `n` (next), `s` (step in), `r` (return), `c` (continue), `w` (where), `l`/`ll` (list), `p`/`pp` (print), `!stmt` (execute), `interact` (full REPL), `q` (quit).

## Recipes

```bash
# Local breakpoint — add breakpoint() in source, run normally
# Remove before commit: rg -n 'breakpoint\(\)' --type py

# Launch script under pdb (no source edits)
python -m pdb path/to/script.py arg1 arg2

# pytest with pdb (disables xdist)
python -m pytest tests/foo_test.py::test_bar --pdb -p no:xdist

# Post-mortem on exception
python -m pdb -c continue script.py  # catches crash

# remote-pdb (cleanest for agents)
pip install remote-pdb
# In code: from remote_pdb import set_trace; set_trace(host="127.0.0.1", port=4444)
# Terminal: nc 127.0.0.1 4444

# debugpy — listen and wait for DAP client
pip install debugpy
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client script.py
```

## Pitfalls
- pdb under pytest-xdist silently hangs — use `-p no:xdist`
- `breakpoint()` in CI hangs — never commit it
- `PYTHONBREAKPOINT=0` disables all breakpoints
- pdb doesn't follow multiprocessing forks
- asyncio: pdb works, `await` inside pdb needs Python 3.13+