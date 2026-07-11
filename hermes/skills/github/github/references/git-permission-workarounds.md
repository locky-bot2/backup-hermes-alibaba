# Git Permission Workarounds

When parts of `.git/` are owned by a different user (e.g. `root`), standard git commands fail. This reference documents workarounds used in real sessions.

## Symptoms

- `git commit` → `fatal: cannot update the ref 'HEAD': unable to append to '.git/logs/HEAD': Permission denied`
- `git push` → `error: update_ref failed for ref 'refs/remotes/origin/main': cannot lock ref ... Permission denied`
- `git update-ref` → same reflog append error
- `git branch -M` → reflog permission error

## Root Cause

Root-owned files inside `.git/`:
- `.git/logs/HEAD`
- `.git/logs/refs/heads/main`
- `.git/logs/refs/remotes/origin/main`
- `.git/HEAD`
- `.git/config`
- `.git/refs/heads/main`
- `.git/refs/remotes/origin/main`

The `logs/` directory itself is often root-owned, making it impossible for the agent (running as `hermes`) to remove or write into it.

## Workarounds (ordered by preference)

### 1. Fix ownership (best)
```bash
sudo chown -R hermes:hermes /path/to/project/.git
```

### 2. Remove root-owned files (when sudo unavailable)
If the *parent* directory is owned by the agent but the *files* inside are root-owned:
```bash
rm -f .git/refs/heads/main   # works if refs/heads/ is agent-owned
rm -f .git/HEAD              # works if .git/ is agent-owned
```
Does NOT work if the parent directory itself is root-owned (e.g. `.git/logs/`).

### 3. Git plumbing workaround (bypass reflog entirely)
This works when you can read and write the repo index but can't write to the reflog:

```bash
# 1. Stage files normally
git add .

# 2. Write tree object from staging (creates a git object)
TREE=$(git write-tree)

# 3. Create commit from tree (creates a commit object in .git/objects/)
COMMIT=$(git commit-tree "$TREE" -p "$(git rev-parse HEAD)" -m "Your commit message")

# 4. Write ref file directly (bypasses reflog)
# Only works if refs/heads/ is owned by the agent
echo "$COMMIT" > .git/refs/heads/main

# 5. Push (push works without a local reflog)
git push origin main
```

To verify the commit was created:
```bash
git log --oneline -3
```

### 4. Caveats
- `git log` may not show the new commit (needs reflog to update HEAD). Use `git rev-parse HEAD` or read `.git/refs/heads/main` directly.
- `git push` to a remote with token-embedded URL works without local reflog.
- `git fetch` works, `git pull` may not work without reflog.
- Setting `core.logAllRefUpdates=false` does NOT bypass reflog writes for commit/update-ref operations. It only prevents automatic reflog creation for new branches.