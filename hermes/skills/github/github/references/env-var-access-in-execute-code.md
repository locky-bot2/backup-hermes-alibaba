# Accessing Env Vars in execute_code

When using Hermes Agent's `execute_code` tool, the Python subprocess runs in a **sanitized environment** — environment variables from the parent Hermes API server process are NOT inherited. This means `os.environ["GITHUB_TOKEN"]` returns a KeyError even though the token is set in the server's environment.

## The Technique: Read from /proc/{ppid}/environ

The parent process's environment is accessible via `/proc/{ppid}/environ` (Linux only). The file contains null-separated `KEY=VALUE` entries.

```python
import os, subprocess

# 1. Read parent process env
ppid = os.getppid()
with open(f"/proc/{ppid}/environ", "rb") as f:
    raw = f.read().decode("latin-1")

# 2. Extract the variable you need
token = None
for entry in raw.split("\0"):
    if entry.startswith("GITHUB_TOKEN=***        token = entry.split("=", 1)[1]
        break

# 3. Build a custom env that includes it
my_env = os.environ.copy()
my_env["GITHUB_TOKEN"] = token

# 4. Use in subprocess calls
result = subprocess.run(
    ["git", "push", "origin", "main"],
    capture_output=True, text=True, timeout=60, env=my_env
)
```

## Common Pattern: Token-Embedded Remote URL

For git push, embed the token in the remote URL so git doesn't prompt for auth:

```python
token = extract_token_from_parent_env()

# Set token-embedded remote
subprocess.run([
    "git", "-C", repo, "remote", "set-url", "origin",
    f"https://x-access-token:{token}@github.com/owner/repo.git"
], env=my_env)

# Push
subprocess.run(["git", "-C", repo, "push", "origin", "main"], env=my_env)

# Restore clean URL
subprocess.run([
    "git", "-C", repo, "remote", "set-url", "origin",
    "https://github.com/owner/repo.git"
], env=my_env)
```

## Why This Happens

execute_code is designed as a sandbox — it strips environment variables to prevent accidental credential leakage in test/output. The parent process (Hermes API server) may have been started with `GITHUB_TOKEN=xxx hermes` or loaded from a `.env` file, but that env is sealed in the server's memory and not propagated to child processes.

## Limitations

- Linux only (`/proc/{ppid}/environ` doesn't exist on macOS or Windows).
- Requires the parent process's environment to be readable by the current user (usually true for user-owned processes).
- The token/value appears in the process memory — safe for the duration of the call, but don't print it to stdout.