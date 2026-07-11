#!/bin/bash
# Hermes VPS Backup Script
# Drop into ~/.hermes/scripts/ as <filename>.sh, chmod +x, then reference
# by filename only in cronjob action=create (no_agent=True).
#
# Only commits when there are actual changes -> empty stdout = silent delivery.
# Non-zero exit -> error alert to Telegram.

set -e
REPO_DIR="/opt/data"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M UTC")

# Extract PAT from git-credentials -> GITHUB_TOKEN env var
# Makes auth available in bare cron shells that may not inherit cred helpers
if [ -f "$HOME/.git-credentials" ]; then
  TOKEN=$(sed -n 's|https://[^:]*:\([^@]*\)@github.com|\1|p' "$HOME/.git-credentials")
  if [ -n "$TOKEN" ]; then
    export GITHUB_TOKEN="$TOKEN"
  fi
fi

cd "$REPO_DIR"

# Stage all changes (respects .gitignore)
git add -A

# Bail if nothing changed
if git diff --cached --quiet; then
  echo "[$TIMESTAMP] No changes to back up. Skipping commit."
  exit 0
fi

# Commit and push
CURRENT_TIME=$(date +"%Y-%m-%d_%H-%M")
git commit -m "Auto-backup: $CURRENT_TIME UTC

Hermes VPS weekly backup - $(hostname)"
git push origin main

echo "[$TIMESTAMP] Backup complete - $(git rev-parse --short HEAD)"