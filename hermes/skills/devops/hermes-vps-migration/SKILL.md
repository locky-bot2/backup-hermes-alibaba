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

The **GITHUB_TOKEN** must be available to the backup script. Three source options, in order of preference:

**Option A — .bashrc export (recommended for this VPS)**

The simplest approach: add an export to the user's `.bashrc` so every shell session has it:

```bash
echo 'export GITHUB_TOKEN="ghp_...your_token..."' >> ~/.bashrc
source ~/.bashrc
```

This is the user's preferred approach. Works because the cron `no_agent=True` scripts can source it: `source "$HOME/.bashrc"` at the top of the backup script. Simplest to maintain and doesn't require special file formats.

**Option B — git-credentials store (traditional)**

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

### Named Backup Repo Convention

When creating a second backup repo for a different environment (e.g., a new VPS), use the pattern `backup-<environment>` to distinguish repos:

| Repo | Purpose |
|------|---------|
| `locky-bot2/hermes-backup` | Original VPS (legacy) |
| `locky-bot2/backup-hermes-alibaba` | Alibaba VPS |

Inside each repo, use a `hermes/` subdirectory to hold `~/.hermes/` contents, keeping root-level files minimal:

```
backup-hermes-alibaba/
├── config.yaml          # Root-level for quick reference
├── SOUL.md              # Agent persona
├── backup.sh            # Backup script
├── .gitignore           # Excludes node_modules, *.db-shm, secrets
├── README.md            # What this backup contains
└── hermes/              # Full ~/.hermes/ contents
    ├── profiles/
    ├── skills/
    ├── cron/
    ├── memories/
    ├── sessions/
    └── ...
```

This keeps the repo root scannable and the bulk content organized.

### Backup Script for Systems Without rsync

If the target VPS doesn't have `rsync` (common on minimal Linux images), use `cp -r` with a case-statement exclusion pattern instead:

```bash
#!/bin/bash
set -e
REPO_DIR="/home/admin/backup-hermes-alibaba"
HERMES_HOME="$HOME/.hermes"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M UTC")

echo "[$TIMESTAMP] Starting Hermes backup..."

# Clean and recreate hermes directory in repo
rm -rf "$REPO_DIR/hermes"
mkdir -p "$REPO_DIR/hermes"

# Copy root-level files
cp "$HERMES_HOME/config.yaml" "$REPO_DIR/config.yaml" 2>/dev/null || true

# Copy hermes content, excluding large/cache dirs via case statement
for item in "$HERMES_HOME"/*; do
    name=$(basename "$item")
    case "$name" in
        .env|auth.json|auth.lock|.hermes|audio_cache|image_cache|cache|logs|sandboxes|hooks|pairing|node_modules|venv|.venv|hermes-agent|lsp)
            continue ;;
        *.db-shm|*.db-wal)
            continue ;;
    esac
    cp -r "$item" "$REPO_DIR/hermes/" 2>/dev/null || true
done

# Source GITHUB_TOKEN from bashrc
source "$HOME/.bashrc" 2>/dev/null || true

cd "$REPO_DIR"
git add -A

if git diff --cached --quiet; then
  echo "[$TIMESTAMP] No changes to back up. Skipping commit."
  exit 0
fi

CURRENT_TIME=$(date +"%Y-%m-%d_%H-%M-%S")
git -c user.email="ash@hermes.local" -c user.name="Ash (Auto-Backup)" \
  commit -m "Auto-backup: $CURRENT_TIME UTC"
git push origin main

echo "[$TIMESTAMP] Backup complete - $(git rev-parse --short HEAD)"
```

The case-statement pattern is key — it skips large volatile directories (`node_modules`, `lsp`, `cache`) that bloat the repo and change constantly. Pair with a `.gitignore` that mirrors the same exclusions as a safety net.

To also copy this script to `~/.hermes/scripts/` so the cron system can find it:
```bash
cp /path/to/repo/backup.sh ~/.hermes/scripts/backup.sh
chmod +x ~/.hermes/scripts/backup.sh
```

This lets the cron job reference `script='backup.sh'` (resolved relative to `~/.hermes/scripts/`) while the actual script lives in the repo it manages — a useful separation of concerns.

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

### 2.4 Using `workdir` for script-based cron jobs

For script-based cron jobs (`no_agent=True`), the `workdir` parameter pins the working directory AND makes the cron system load `AGENTS.md` / `CLAUDE.md` from that directory. This eliminates path-guessing issues with script resolution:

```bash
cronjob action=create
       name='Hermes Weekly Backup'
       schedule='0 0 * * 0'
       script='backup.sh'
       no_agent=True
       workdir='/home/admin/backup-hermes-alibaba'
       deliver='telegram:CHAT_ID'
```

With `workdir` set:
- The script runs from that directory (so relative repo paths in the script just work)
- The cron system doesn't need to resolve the script path — it runs it from the workdir
- If the script is at `$workdir/backup.sh`, explicitly set `script='backup.sh'` to match

Note: `workdir` must be an absolute path that exists. Jobs with `workdir` run sequentially (not parallel) to keep per-job directories isolated.

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

---\n\n## 5. Running Supplementary Web UIs (Hermes Workspace, etc.)

You may want to run third-party web UIs (like Hermes Workspace from outsourc-e) alongside the Hermes agent on the same VPS. These connect to Hermes via its API server and dashboard endpoints.

### 5.1 Enable the Gateway API Server

The gateway must expose its API server for external UIs to connect. Add to `~/.hermes/.env`:

```env
API_SERVER_ENABLED=true
API_SERVER_KEY=<your-secret-key>    # optional but recommended for auth
```

Then restart the gateway: `hermes gateway run --replace` (or `kill` the old process and start fresh).

Verify: `curl http://127.0.0.1:8642/health` returns `{"status":"ok","platform":"hermes-agent"}`

### 5.2 Dashboard Ports

The built-in dashboard (`hermes dashboard`) typically runs on port 9120. If proxied through nginx (e.g., behind a hostname-based proxy on 9119), note the correct URL — the workspace needs it.

### 5.3 Hermes Workspace Setup

**Attach mode** (hermes-agent already installed):

```bash
git clone https://github.com/outsourc-e/hermes-workspace.git ~/hermes-workspace
cd ~/hermes-workspace
pnpm install
cp .env.example .env
```

**Env vars** — the workspace runtime reads `CLAUDE_*` vars (not `HERMES_*` despite the README examples):

```env
# Required: gateway endpoint
CLAUDE_API_URL=http://127.0.0.1:8642

# Recommended: dashboard for sessions/skills/config
CLAUDE_DASHBOARD_URL=http://127.0.0.1:9119

# Only if API_SERVER_KEY is set on the gateway
CLAUDE_API_TOKEN=<same-value-as-api-server-key>

# Also set HERMES_* equivalents (the README uses these for onboarding probe)
HERMES_API_URL=http://127.0.0.1:8642
HERMES_DASHBOARD_URL=http://127.0.0.1:9119
HERMES_API_TOKEN=<same-value-as-api-server-key>
```

**Pitfall:** Set BOTH `CLAUDE_*` AND `HERMES_*` vars. The onboarding flow probes `HERMES_*`, but the runtime SSR server reads `CLAUDE_*`. Missing either causes blank pages or missing features.

**Pitfall — nginx Host header blocking:** If the dashboard is proxied through nginx (e.g. `:9119 → :9120`) and nginx has a `default_server return 444` catch-all, the workspace's internal fetch to `127.0.0.1:9119` gets blocked. Fix: point `CLAUDE_DASHBOARD_URL` directly at the dashboard backend (`http://127.0.0.1:9120`), bypassing nginx.

**Pitfall — blank page / CJS→ESM interop:** HTML loads but page stays blank with console error about `use-sync-external-store/shim` not exporting `useSyncExternalStore`. Fix: add `'use-sync-external-store/shim'` and `'use-sync-external-store/shim/with-selector'` to `optimizeDeps.include` in `vite.config.ts`, clear `.vite/` cache, restart with `--force`. See `references/workspace-tanstack-cjs-interop.md` for full details.

**Start:**

```bash
# Dev mode (Vite HMR) — restart after any .env change
NODE_OPTIONS="--max-old-space-size=800" npx vite dev --host 0.0.0.0 --port 3000

# Production preview (after pnpm build)
NODE_OPTIONS="--max-old-space-size=800" npx vite preview --host 0.0.0.0 --port 3000
```

### 5.4 Low-RAM VPS Workarounds

On VPS with ≤2GB RAM, Vite's esbuild dependency optimizer gets OOM-killed. Symptoms:
- Dev server starts but crashes with `Error: The service was stopped` from esbuild
- `vite build` fails silently (exit code 130/143)
- Preview server returns 500 Internal Server Error (no dist output)

**Fix — add swap:** See [`references/vps-swap-setup.md`](references/vps-swap-setup.md) for the complete setup. Quick reference:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

2GB swap (roughly 1:1 with physical RAM) is the sweet spot — enough for esbuild spikes without thrashing.

**Additional mitigations:**

| Technique | When | How |
|-----------|------|-----|
| Limit Node heap | Always on low-RAM | `NODE_OPTIONS="--max-old-space-size=800"` prefix |
| Build before dev | First-time setup | `pnpm build` creates dep cache; subsequent `pnpm dev` reuses it |
| Swap + Node limit | Combined | Both together reliably prevent esbuild OOM on 1.8GB RAM VPS |
| Skip dep optimization | Last resort | Not supported via CLI — need to edit `vite.config.ts` `optimizeDeps` |

### 5.5 Gateway Systemd Management

If the gateway is a systemd user service (common on VPS setups), manage it explicitly when stopping/restarting:

```bash
systemctl --user stop hermes-gateway    # Prevent auto-restart during maintenance
systemctl --user start hermes-gateway   # Re-enable
systemctl --user status hermes-gateway  # Check state
```

**Pitfall:** `kill -9 PID` on a systemd-managed gateway triggers auto-restart loop (`activating (auto-restart) (Result: exit-code)`). Always use `systemctl --user stop hermes-gateway` first, then start fresh.

---

## 6. Pitfalls

- **state.db is tracked**: If you already committed state.db before adding it to .gitignore, you must `git rm --cached state.db` (and the -shm / -wal variants) to stop tracking it
- **Token scope**: The GITHUB_TOKEN needs `repo` scope for pushing to private repos
- **First cron run delay**: A `schedule='1m'` test job may not fire immediately — the scheduler runs on a tick (~30-60s). Force-run with `cronjob action=run job_id=...` if needed
- **Cron context isolation**: Agent-driven cron jobs (no_agent=False) have NO memory, NO conversation history, and NO current context — the prompt must be fully self-contained
- **Time zone**: Taiwan is UTC+8. Schedule in UTC. Saturday 8am Taiwan = `0 0 * * 6` (midnight UTC Saturday). Sunday 8am Taiwan = `0 0 * * 0` (midnight UTC Sunday)
- **no_agent script path resolution**: The cron system resolves relative `script='name.sh'` paths — if it errors `Script not found: /some/path/name.sh`, that path tells you exactly where it's looking. Don't fight it: copy the script there. Absolute paths (`script='/opt/data/scripts/name.sh'`) are explicitly supported and eliminate ambiguity.