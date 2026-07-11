#!/bin/bash
# Hermes Alibaba VPS Backup Script
# Backs up config, profiles, skills, sessions, cron, memories to GitHub
# Runs via cron job - no_agent=True

set -e
REPO_DIR="/home/admin/backup-hermes-alibaba"
HERMES_HOME="$HOME/.hermes"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M UTC")

echo "[$TIMESTAMP] Starting Hermes backup..."

# Sync files to repo (exclude secrets and large caches)
rsync -a --delete \
  --exclude=".env" \
  --exclude="auth.json" \
  --exclude="auth.lock" \
  --exclude=".hermes/" \
  --exclude="audio_cache/" \
  --exclude="image_cache/" \
  --exclude="cache/" \
  --exclude="logs/" \
  --exclude="sandboxes/" \
  --exclude="hooks/" \
  --exclude="pairing/" \
  --exclude=".skills_prompt_snapshot.json" \
  --exclude=".update_check" \
  --exclude=".clean_shutdown" \
  --exclude=".hermes_history" \
  --exclude="*.db-shm" \
  --exclude="*.db-wal" \
  --exclude="node_modules/" \
  "$HERMES_HOME/" "$REPO_DIR/hermes/"

# Copy config and auth (without secrets)
cp "$HERMES_HOME/config.yaml" "$REPO_DIR/config.yaml" 2>/dev/null || true

# Copy backup script itself
cp "$REPO_DIR/backup.sh" "$REPO_DIR/scripts/backup.sh" 2>/dev/null || true

# Source token from bashrc
source "$HOME/.bashrc"

cd "$REPO_DIR"

# Add all changes
git add -A

# Check if there's anything to commit
if git diff --cached --quiet; then
  echo "[$TIMESTAMP] No changes to back up. Skipping commit."
  exit 0
fi

# Commit and push
CURRENT_TIME=$(date +"%Y-%m-%d_%H-%M-%S")
git commit -m "Auto-backup: $CURRENT_TIME UTC

Hermes VPS backup - $(hostname)
Includes: config, profiles, skills, cron, memories, state, sessions"
git push origin main

echo "[$TIMESTAMP] Backup complete - $(git rev-parse --short HEAD)"
