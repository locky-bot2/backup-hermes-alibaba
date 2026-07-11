---
name: hermes-vps-migration
description: Complete lifecycle management for Hermes Agent on a VPS — initial backup setup, weekly auto-backup cron, credential management, and migration restore.
tags: [vps, backup, migration, devops, cron, github]
related_skills: [research/arxiv, hermes-agent]
---

# Hermes VPS Lifecycle Management

Use when setting up a Hermes Agent backup system, configuring weekly auto-backup cron jobs, or migrating to a new VPS.

This skill covers the full lifecycle: initial backup setup, weekly automated backups, credential/auth management for cron jobs, and migration to a new host.

---

## 1. Initial Backup Setup

### 1.1 Create the GitHub repo and push

Create the repo on GitHub first. Without the `gh` CLI, use the GitHub API:

```bash
# Requires a GITHUB_TOKEN with 'repo' scope
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/user/repos \
  -d '{"name":"hermes-backup","description":"Auto-backup of Hermes Agent VPS","private":false}'
```

Or from the browser: create a new repo at https://github.com/new (no README, no .gitignore, no license — the backup script pushes the first commit).

Then clone and set up the backup project:

```bash
# Clone to the home directory (not /opt/data — choose a path that exists on your VPS)
git clone https://github.com/YOUR_USER/hermes-backup.git ~/hermes-backup
cd ~/hermes-backup

### 1.2 Auth setup

The **GITHUB_TOKEN** lives in the parent Hermes process environment. Extract it when needed:

```python
import subprocess
r = subprocess.run(["cat", "/proc/<HERMES_PID>/environ"], capture_output=True, text=True)
lines = r.stdout.split('\0')
for l in lines:
    if l.startswith("GITHUB_TOKEN=***        token = l.split("=", 1)[1]
```

Set up git credential store so cron jobs can push without interactive auth:

```bash
git config --global credential.helper store
git config --global user.name "Your Name"
git config --global user.email "your-email@users.noreply.github.com"
```

Write the credential file (~/.git-credentials) with the token-based URL:
`https://USERNAME:TOKEN@github.com/YOUR_USER/backup-repo.git`

Set file permissions to 600.

### 1.3 .gitignore essentials

Exclude runtime artifacts that change constantly and don't need backing up:

```
# State DB (runtime, regenerated)
state.db
state.db-shm
state.db-wal

# User home (shell history, local config)
home/

# Secrets
.env
.env.*
auth.json
credentials.json
*.token
secrets/

# Cache and runtime
logs/
cache/
.cache/
tmp/
*.log
*.pid
*.lock

# Build artifacts
node_modules/
.npm/
.pnpm-store/
__pycache__/
*.pyc
.venv/
venv/
bin/

# User-excluded projects (e.g. weather-app/)
weather-app/
```

Pitfall: Adding state.db to .gitignore only prevents tracking NEW files. If state.db was already tracked, run `git rm --cached state.db` to stop tracking it.

### 1.4 First push

```bash
git add -A
git commit -m "Initial backup: Hermes VPS"
git push origin main
```

---

## 2. Weekly Auto-Backup via Cron

### 2.1 Write the backup script

Create `~/.hermes/scripts/hermes-backup.sh`:

```bash
#!/bin/bash
set -e
# IMPORTANT: Must match where the backup repo is cloned
# Common locations: ~/hermes-backup, /opt/data, /home/admin/hermes-backup
REPO_DIR="$HOME/hermes-backup"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M UTC")

cd "$REPO_DIR"
git add -A

if git diff --cached --quiet; then
  echo "[$TIMESTAMP] No changes to back up. Skipping commit."
  exit 0
fi

CURRENT_TIME=$(date +"%Y-%m-%d_%H-%M")
git commit -m "Auto-backup: $CURRENT_TIME UTC"
git push origin main

echo "[$TIMESTAMP] Backup complete - $(git rev-parse --short HEAD)"
```

Make executable: `chmod +x ~/.hermes/scripts/hermes-backup.sh`

**Script path resolution:** The cron system resolves relative script paths; test the actual path if it fails. Three reliable approaches, in order of preference:

1. **Absolute path** (most robust): Place the script anywhere and use an absolute path: `script='/opt/data/scripts/hermes-backup.sh'` — no ambiguity.
2. **Known-good relative path**: Place in `~/scripts/` and reference by filename: `script='hermes-backup.sh'`.
3. **~/.hermes/scripts/**: Also works — sync a copy there for consistency: `cp ~/scripts/hermes-backup.sh ~/.hermes/scripts/`

If `last_status: error` with `Script not found: PATH`, that PATH tells you exactly where the cron is looking — copy the script there. Don't guess.

A ready-to-use copy of this script is available as `templates/backup-script.sh` under this skill.

### 2.2 Create the cron job

Use `no_agent=True` for zero LLM cost — the script runs directly:

```
cronjob action=create
       name='Hermes VPS Weekly Backup'
       schedule='0 0 * * 0'           # Sunday 00:00 UTC = 8am Taiwan time
       script='hermes-backup.sh'
       no_agent=True
       deliver='telegram:CHAT_ID'      # or omit for auto-delivery to current chat
```

#### Delivery semantics (no_agent=True):

- **Non-empty stdout** -> delivered verbatim as the message
- **Empty stdout** -> silent (nothing sent) — design your script to stay quiet when there's nothing to report
- **Non-zero exit / timeout** -> error alert sent (can't fail silently)

### 2.3 Test before recurring

Best practice for cron jobs:

1. Create a test job with `repeat=1 schedule='1m'` so it fires quickly
2. Wait 30-60s for the scheduler tick, or use `cronjob action=run job_id=...` to force immediate execution
3. Check delivery via `cronjob action=list` (look at `last_status`)
4. Remove the test job with `cronjob action=remove job_id=...`
5. Then create the recurring schedule

---

## 3. Credential Management for Cron Jobs

### 3.1 Where tokens live

- The GITHUB_TOKEN is set in the Hermes container/systemd environment — accessible from `/proc/<PID>/environ`
- For the cron job to push to GitHub, the token must be stored in git credential store (`~/.git-credentials`)
- On restore to a new VPS, the token must be re-configured in the environment AND in the credential store

### 3.2 PAT → GITHUB_TOKEN extraction (recommended for no_agent scripts)

`no_agent=True` scripts run in a bare shell that may not inherit git credential helpers. The most reliable approach: have the backup script extract the PAT from `~/.git-credentials` at runtime and export it as `GITHUB_TOKEN`.

Git-credentials format: `https://USERNAME:TOKEN@github.com`

Extract with `sed`:

```bash
if [ -f "$HOME/.git-credentials" ]; then
  TOKEN=$(sed -n 's|https://[^:]*:\(.*\)@github.com|\1|p' "$HOME/.git-credentials")
  if [ -n "$TOKEN" ]; then
    export GITHUB_TOKEN="$TOKEN"
  fi
fi
```

This makes `$GITHUB_TOKEN` available to `git push` and any subprocesses, regardless of credential helper state.

### 3.3 What credentials each cron needs

| Cron type | Auth needed | How to provide |
|-----------|-------------|----------------|
| Git backup (no_agent=True) | GITHUB_TOKEN | git credential store (`~/.git-credentials`) |
| Agent-based cron (arXiv search, etc.) | Provider API keys | Already in config.yaml or .env — cron inherits the hermes env |

Cron jobs with `no_agent=True` run as a shell script — they only have access to what the script itself sets up. They do NOT inherit Hermes environment variables.

Cron jobs with `no_agent=False` (default, agent-driven) run inside a full Hermes session and have access to all configured providers, gateway channels, and tools.

---

## 4. Migration to a New VPS

### 4.1 Restore from GitHub

```bash
cd /opt/data
git clone https://github.com/YOUR_USER/backup-repo.git .

# Install Hermes
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | sh
```

### 4.2 Restore credentials

The following are **not** in the GitHub backup and must be re-configured:

| Credential | Where to set it |
|------------|----------------|
| GITHUB_TOKEN | Environment variable + `~/.git-credentials` |
| OPENROUTER_API_KEY / provider keys | `.env` file at repo root |
| TELEGRAM_BOT_TOKEN | `.env` + reconnect gateway |
| Any other API keys | `.env` file |

### 4.3 Reconnect gateways

Telegram gateways need the TELEGRAM_BOT_TOKEN and TELEGRAM_ALLOWED_USERS to be set in `.env`. After Hermes starts, run:

```bash
hermes gateway add telegram
```

(Or use the Hermes dashboard to add the gateway.)

### 4.4 Verify migration

```bash
ls -la /opt/data/profiles/     # Agent profiles present?
hermes config show              # Config loaded?
hermes skills list              # All skills there?
hermes cron list                # Cron jobs restored?
```

The cron jobs from `cron/jobs.json` will be loaded once Hermes starts. Verify they're active with `cronjob action=list`.

---

## 5. Pitfalls

- **state.db is tracked**: If you already committed state.db before adding it to .gitignore, you must `git rm --cached state.db` (and the -shm / -wal variants) to stop tracking it
- **Token scope**: The GITHUB_TOKEN needs `repo` scope for pushing to private repos
- **First cron run delay**: A `schedule='1m'` test job may not fire immediately — the scheduler runs on a tick (~30-60s). Force-run with `cronjob action=run job_id=...` if needed
- **Cron context isolation**: Agent-driven cron jobs (no_agent=False) have NO memory, NO conversation history, and NO current context — the prompt must be fully self-contained
- **Time zone**: Taiwan is UTC+8. Schedule in UTC. Saturday 8am Taiwan = `0 0 * * 6` (midnight UTC Saturday). Sunday 8am Taiwan = `0 0 * * 0` (midnight UTC Sunday)
- **no_agent script path resolution**: The cron system resolves relative `script='name.sh'` paths — if it errors `Script not found: /some/path/name.sh`, that path tells you exactly where it's looking. Don't fight it: copy the script there. Absolute paths (`script='/opt/data/scripts/name.sh'`) are explicitly supported and eliminate ambiguity.