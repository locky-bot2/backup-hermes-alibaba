---
name: hermes-agent-restore-backup
description: Restore Hermes Agent configuration from a backup repository, including subagent profiles, sessions, memories, and database files.
version: 1.2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [backup, restore, devops, configuration, migration]
    related_skills: [hermes-agent]
---

# Restore Hermes Agent Configuration

Restore Hermes Agent configuration from a backup repository, including subagent profiles, sessions, memories, and database files.

## When to Use

Use this skill whenever restoring a Hermes Agent instance from a backup repository (e.g., from GitHub, local backup, or archived data).

## Overview

Hermes Agent configuration is stored in `~/.hermes/` and includes:
- Main `config.yaml`
- Subagent profiles in `~/.hermes/profiles/`
- Sessions, memories, cron jobs
- Database files (kanban.db, response_store.db)
- Gateway state, scripts, and caches

## Prerequisites

- Access to the backup repository
- Hermes Agent installed and configured
- Proper file permissions on `~/.hermes/`

## Steps

### 1. Clone or Access the Backup

```bash
# If from GitHub
git clone <backup-repo-url> <destination>

# Verify the backup contains expected files
ls -la <backup-path>
```

Expected backup contents:
- `config.yaml` - Main configuration
- `profiles/` - Subagent profiles directory
- `sessions/` - Chat session history
- `memories/` - User memories (USER.md, MEMORY.md)
- `cron/` - Scheduled jobs
- `scripts/` - Custom scripts
- Database files: `kanban.db`, `response_store.db`, etc.
- State files: `gateway_state.json`, `channel_directory.json`

### 2. Backup Current Configuration (Optional but Recommended)

```bash
mkdir -p ~/.hermes_restore_backup
cp ~/.hermes/config.yaml ~/.hermes_restore_backup/
```

### 3. Restore Main Configuration

```bash
cp <backup-path>/config.yaml ~/.hermes/config.yaml
```

### 4. Restore Subagent Profiles

```bash
mkdir -p ~/.hermes/profiles
cp -r <backup-path>/profiles/* ~/.hermes/profiles/
```

Verify profiles were restored:
```bash
ls -la ~/.hermes/profiles/
```

Each profile directory should contain:
- `config.yaml` - Profile-specific configuration
- `skills/` - Profile-specific skills (if any)

### 5. Restore Supporting Data

```bash
cp -r <backup-path>/sessions/* ~/.hermes/sessions/
cp -r <backup-path>/memories/* ~/.hermes/memories/
cp -r <backup-path>/cron/* ~/.hermes/cron/
cp -r <backup-path>/scripts/* ~/.hermes/scripts/
```

### 6. Restore Database Files

```bash
cp <backup-path>/kanban.db ~/.hermes/
cp <backup-path>/response_store.db ~/.hermes/
cp <backup-path>/response_store.db-shm ~/.hermes/
cp <backup-path>/response_store.db-wal ~/.hermes/
cp <backup-path>/kanban.db-shm ~/.hermes/ 2>/dev/null || true
cp <backup-path>/kanban.db-wal ~/.hermes/ 2>/dev/null || true
```

### 7. Restore State and Cache Files

```bash
cp <backup-path>/gateway_state.json ~/.hermes/
cp <backup-path>/channel_directory.json ~/.hermes/
cp <backup-path>/workspace-sessions.json ~/.hermes/
cp <backup-path>/models_dev_cache.json ~/.hermes/
```

### 8. Verify Restoration

```bash
# Check profiles
ls -la ~/.hermes/profiles/

# Check sessions
ls -la ~/.hermes/sessions/ | head -10

# Check memories
ls -la ~/.hermes/memories/

# Verify profile config
cat ~/.hermes/profiles/<profile-name>/config.yaml
```

### 9. Validate Profile Provider Configs

Each profile must have a non-empty `provider:` field in its config.yaml to function. Empty provider breaks delegation silently:

```bash
for p in ~/.hermes/profiles/*/config.yaml; do
  name=$(basename "$(dirname "$p")")
  provider=$(grep -E '^provider:' "$p" | sed 's/^provider: *//')
  [ -z "$provider" ] && echo "⚠️  $name: provider is EMPTY — fix before using" || echo "✅ $name: $provider"
done
```

Fix an empty provider by setting it in the profile's config.yaml:
```bash
hermes config set --profile <name> provider openrouter
# or edit directly:
sed -i 's/^provider: ""/provider: openrouter/' ~/.hermes/profiles/<name>/config.yaml
```

### 10. Diff-Based Completeness Check

After restoring, use `diff` to confirm every backup file has a counterpart in ~/.hermes/:

```bash
cd <backup-path>
diff <(find . -type f -not -path './.git/*' | sed 's|^\./||' | sort) \
     <(cd ~/.hermes && find . -type f -not -path './hermes-agent/*' -not -path './logs/*' \
       -not -path './sandboxes/*' -not -path './cache/*' | sed 's|^\./||' | sort) \
     | grep '^<' | grep -v '\.git/'
```

Remaining `^<` lines show items in the backup not yet present in ~/.hermes/. Filter out expected HOME directory files (`.bash_logout`, `.bashrc`, `.profile`) that were captured as artifacts of a whole-home-directory backup.

### 11. Reconnect Messaging Platforms

The backup does **not** contain `.env` credentials (API keys, bot tokens). After restoring files, every messaging platform (Telegram, Discord, etc.) will be disconnected.

**Critical: Gateway allows no users by default.** Even after connecting Telegram, the gateway denies all inbound messages unless you either:
- Set `TELEGRAM_ALLOWED_USERS` to your Telegram user ID (comma-separated for multiple)
- Or set `GATEWAY_ALLOW_ALL_USERS=true` in `.env` (open access — not recommended)

Without either, the gateway log shows `No user allowlists configured. All unauthorized users will be denied` — meaning Telegram connects successfully but every "hi" you send gets silently ignored.

**For Telegram:**

```bash
# 1. Set bot token (get it from @BotFather on Telegram)
sed -i 's|^# TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=your_token_here|' ~/.hermes/.env

# 2. Set allowed users (comma-separated user IDs)
sed -i 's|^# TELEGRAM_ALLOWED_USERS=.*|TELEGRAM_ALLOWED_USERS=your_user_id|' ~/.hermes/.env

# 3. Install gateway as service (first time only)
hermes gateway install

# 4. Start gateway
hermes gateway start

# 5. Verify connection
sleep 3 && grep "telegram" ~/.hermes/logs/gateway.log | tail -3
```

Expected log output: `✓ telegram connected`

**For other platforms**, set the relevant env vars in `.env` and restart the gateway.

If the gateway was already running and you're just updating credentials, use `hermes gateway restart` instead of install+start.

### 12. Run Doctor to Clean Stale Config

Backups from older Hermes versions or from different provider setups often leave stale root-level config keys. Run the auto-fixer:

```bash
hermes doctor --fix
```

This catches issues like:
- `provider:` and `base_url:` sitting at the root level instead of under `model:`
- Other schema migrations between config versions

### 13. Verify Cron Jobs Work After Restore

Cron jobs often reference scripts or repo paths that may not exist on the new machine.

**For script-based cron jobs (`no_agent: True`):**

```bash
# List all cron jobs and check their scripts
hermes cron list

# For each job with a "script:" field, verify the script exists
# and any paths it references are valid on the new machine:
ls -la ~/.hermes/scripts/hermes-backup.sh   # Example

# If the script pushes to a git repo, verify the clone exists:
ls -la /path/to/repo/.git
```

**For LLM-driven cron jobs:**

```bash
# Trigger a manual test run (the cron job runs in the background)
hermes cron list
# Use the cronjob tool with action='run' to test a specific job

# Check the run completed:
ls -lt ~/.hermes/cron/output/<job-id>/ | head -5
```

Example: a backup script may reference `REPO_DIR="/opt/data"` but the actual clone lives at `/home/admin/hermes-backup`. Always verify paths after restore.

### 14. Verify `hermes` Command Is on PATH

After restoring files, confirm the `hermes` CLI is findable. The Hermes installer places the wrapper at `~/.local/bin/hermes`, but PATH inclusion may depend on shell type:

```bash
# Test in a fresh non-login shell (matches SSH → immediate command scenario)
bash -c 'which hermes' 2>/dev/null
```

If not found, check which profile files add `~/.local/bin`:

```bash
grep -rn ".local/bin" ~/.profile ~/.bashrc ~/.bash_profile 2>/dev/null
```

- **`~/.profile`** — only sourced by login shells (fresh SSH). Not available in tmux panes, subshells, or `ssh host command` invocations.
- **`~/.bashrc`** — sourced by every interactive non-login shell. **This is the reliable place.**

If `.local/bin` is only in `~/.profile`, add it to `~/.bashrc` too:

```bash
cat >> ~/.bashrc << 'EOF'

# Add local bin to PATH for hermes command
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
EOF
```

Then verify from any shell type:

```bash
bash -c 'source ~/.bashrc && hermes --version'
```

### 15. Set Up Ongoing Backup to GitHub

After restoring, set up recurring backups so the next restore has fresher data. This creates a **new** backup repository (not the one you restored from).

**Prerequisites:** GitHub Personal Access Token with `repo` scope. The token may be:
- In `~/.bashrc` as `export GITHUB_TOKEN=...`
- In `~/.git-credentials` as `https://user:TOKEN@github.com`
- Provided manually

**Steps:**

```bash
# 1. Create the repo via GitHub API
curl -s -X POST https://api.github.com/user/repos \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d '{
    "name": "backup-hermes-<hostname>",
    "description": "Auto-backup of Hermes Agent on <hostname>",
    "private": false,
    "auto_init": true
  }'

# 2. Clone it locally
git clone https://$GITHUB_TOKEN@github.com/<user>/backup-hermes-<hostname>.git \
  /home/admin/backup-hermes-<hostname>

# 3. Write a backup script (no_agent mode)
cat > /home/admin/backup-hermes-<hostname>/backup.sh << 'SCRIPT'
#!/bin/bash
set -e
REPO_DIR="/home/admin/backup-hermes-<hostname>"
HERMES_HOME="$HOME/.hermes"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M UTC")
echo "[$TIMESTAMP] Starting Hermes backup..."

rm -rf "$REPO_DIR/hermes"
mkdir -p "$REPO_DIR/hermes"

cp "$HERMES_HOME/config.yaml" "$REPO_DIR/config.yaml" 2>/dev/null || true
cp "$HERMES_HOME/SOUL.md" "$REPO_DIR/SOUL.md" 2>/dev/null || true

for item in "$HERMES_HOME"/*; do
    name=$(basename "$item")
    case "$name" in
        .env|auth.json|auth.lock|.hermes|audio_cache|image_cache|cache|logs|sandboxes|hooks|pairing|node_modules|venv|.venv|hermes-agent|lsp)
            continue ;;
        *.db-shm|*.db-wal) continue ;;
    esac
    cp -r "$item" "$REPO_DIR/hermes/" 2>/dev/null || true
done

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
SCRIPT
chmod +x /home/admin/backup-hermes-<hostname>/backup.sh

# 4. Copy to ~/.hermes/scripts/ for cron access
cp /home/admin/backup-hermes-<hostname>/backup.sh ~/.hermes/scripts/backup.sh

# 5. Create git-credentials file so the cron script can push
echo "https://<user>:$GITHUB_TOKEN@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# 6. Push initial backup
cd /home/admin/backup-hermes-<hostname>
./backup.sh

# 7. Create a cron job for weekly backup
# Use the cronjob tool with:
#   action='create'
#   schedule='0 0 * * 0'  (weekly Sunday midnight)
#   script='backup.sh'
#   no_agent=True
#   workdir='/home/admin/backup-hermes-<hostname>'
#   deliver='telegram:<chat_id>'
```

**Important:** The backup script excludes secrets (`.env`, `auth.json`) and large caches. To restore from this backup later:
1. Clone the repo
2. Copy `config.yaml` to `~/.hermes/`
3. Copy `hermes/` contents to `~/.hermes/`
4. Manually re-set `.env` credentials
5. Follow all post-restore steps in this skill

### 16. Send Test Message from Each Platform

After reconnecting each messaging platform, send a test message to confirm the full round-trip works (message → LLM → response):

```bash
# Check gateway status
hermes gateway status

# Watch live logs while you send a test message
tail -f ~/.hermes/logs/gateway.log | grep "inbound message\|response ready"
```

Expected log pattern:
```
inbound message: platform=telegram user=YourName chat=12345 msg='hi'
response ready: platform=telegram chat=12345 time=5.5s response=20 chars
```

If the gateway shows `✓ telegram connected` but test messages get no response, check:
1. `TELEGRAM_ALLOWED_USERS` is set correctly in `.env`
2. The `.env` was reloaded (run `hermes gateway restart`)
3. The LLM provider config is valid (run `hermes doctor`)

## Pitfalls and Solutions

### Missing Profiles Directory

If `~/.hermes/profiles/` doesn't exist, create it first:
```bash
mkdir -p ~/.hermes/profiles
```

### Database File Extensions

Database files may have `.db`, `.db-shm`, `.db-wal` extensions. Copy all parts of each database.

### Cron Output Directory

The cron output directory (`cron/output/`) may be missing from some backups. If restored jobs reference it, create it:
```bash
mkdir -p ~/.hermes/cron/output
```

### Profile Skills

Some profiles have skills in their subdirectories. Restore these too:
```bash
cp -r <backup-path>/profiles/<profile>/skills ~/.hermes/profiles/<profile>/
```

### Permission Issues

After restore, ensure proper permissions:
```bash
chmod -R 755 ~/.hermes/
```

### .env Credentials Not in Backup

By design, `.env` files (API keys, bot tokens) are **never** included in the backup repository. After restore, every messaging platform that relies on credentials will be disconnected. See **Step 11** for the Telegram reconnection procedure.

Other common credentials to re-set:
```
TELEGRAM_BOT_TOKEN=...          # From @BotFather
TELEGRAM_ALLOWED_USERS=...      # Your user ID
GATEWAY_ALLOW_ALL_USERS=...     # Only if you want open access
```

### Mixed Backup Content (HOME Files)

Backup repos often contain HOME directory dotfiles (`.bash_logout`, `.bashrc`, `.profile`, `.gitignore`) mixed into the root because the backup was taken with `tar -czf` of the whole `~/` directory. Recognize these as non-Hermes artifacts:

```bash
# Before restore, identify HOME files in the backup root:
ls -la <backup-path>/ | grep -E '^\.(bash|profile|gitignore|git)'
```

Copy them to `~/` if restoring a full environment, otherwise skip them. They are not Hermes config files and do not belong in `~/.hermes/`.

### Empty Provider in Profile Config

After restoring profiles, always check that every profile has a non-empty `provider:` field. The backup skill's verification step (Step 9) provides a one-liner for this. An empty `provider: ""` causes the profile to silently fall back or fail during delegation — no obvious error message, just a hung agent.

Fix: either set a provider via `hermes config set --profile <name> provider <provider>` or edit the profile's config.yaml directly.

### Vendor-Prefixed Model Names with Direct Providers

Backups made while using an aggregator provider (e.g., OpenRouter with `deepseek/deepseek-v4-flash`) will have vendor-prefixed model names. If you switch to the direct API (e.g., `provider: deepseek`), the vendor prefix must be dropped:

| Provider type | Example model | Correct for... |
|--------------|---------------|----------------|
| Aggregator (OpenRouter) | `deepseek/deepseek-v4-flash` | openrouter |
| Direct API | `deepseek-v4-flash` | deepseek, anthropic, openai |

The prefix `deepseek/` is an OpenRouter routing convention — direct DeepSeek API rejects it. After restoring config from an OpenRouter-era backup and switching to `provider: deepseek`:

```bash
# Run doctor --fix to catch stale keys
hermes doctor --fix

# Then manually strip the vendor prefix:
sed -i 's|  default: deepseek/|  default: |' ~/.hermes/config.yaml
# Also fix each profile:
for p in ~/.hermes/profiles/*/config.yaml; do
  sed -i 's|^model: deepseek/|model: |' "$p"
done
```

Same pattern applies when switching any aggregator-prefixed model to its native provider: `anthropic/claude-sonnet-4` → `claude-sonnet-4` for `provider: anthropic`, `openai/gpt-4o` → `gpt-4o` for `provider: openai`, etc.

### Backup Script Path Mismatch After Restore

Backup scripts (especially `no_agent: True` cron jobs) often reference absolute paths that don't exist on the new machine. Example: `hermes-backup.sh` has `REPO_DIR="/opt/data"` but the git repo clone lives at `/home/admin/hermes-backup`.

Always check script paths after restore:

```bash
# For each script-based cron job, review the script
cat ~/.hermes/scripts/hermes-backup.sh

# Look for hardcoded paths (REPO_DIR, cd /path, etc.)
# Update them to match the new VPS layout
```

The backup repo may have been cloned to a different location on the new machine. Update the script's paths, don't move the repo. The script should reference where the repo actually lives.

### Skill Restructuring Between Hermes Versions

Older Hermes backups may have skills organized under different paths than the current version. Common restructurings found in real backups:

| Old path | Current path(s) |
|----------|----------------|
| `github/github/` | `github/github-auth/`, `github/github-pr-workflow/`, `github/github-code-review/`, etc. |
| `autonomous-ai-agents/autonomous-coding-agents/` | `autonomous-ai-agents/claude-code/`, `codex/`, `opencode/` |

Restoring these restructured skills alongside their current counterparts creates duplicate but non-conflicting skill paths. Both are loadable. No harm done, but be aware the old path may reference outdated APIs or workflows. Prefer the current skill paths when both exist.

## References

- [Backup Structure Reference](references/backup-structure.md) — Expected backup layout with file descriptions and sizes
- Hermes Agent documentation: https://hermes-agent.nousresearch.com/docs
- Profile system: `~/.hermes/profiles/`
