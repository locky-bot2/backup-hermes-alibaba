#!/bin/bash
# Hermes Alibaba VPS Backup Script
# Backs up config, profiles, skills, sessions, cron, memories to GitHub
# Runs via cron job - no_agent=True

set -e
REPO_DIR="/home/admin/backup-hermes-alibaba"
HERMES_HOME="$HOME/.hermes"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M UTC")

echo "[$TIMESTAMP] Starting Hermes backup..."

# Clean and recreate hermes directory in repo
rm -rf "$REPO_DIR/hermes"
mkdir -p "$REPO_DIR/hermes"

# Copy config and SOUL
cp "$HERMES_HOME/config.yaml" "$REPO_DIR/config.yaml" 2>/dev/null || true
cp "$HERMES_HOME/SOUL.md" "$REPO_DIR/SOUL.md" 2>/dev/null || true

# Copy main hermes content (exclude large/cache dirs)
for item in "$HERMES_HOME"/*; do
    name=$(basename "$item")
    case "$name" in
        .env|auth.json|auth.lock|.hermes|audio_cache|image_cache|cache|logs|sandboxes|hooks|pairing|node_modules|venv|.venv|hermes-agent)
            continue ;;
        *.db-shm|*.db-wal)
            continue ;;
    esac
    cp -r "$item" "$REPO_DIR/hermes/" 2>/dev/null || true
done

# Also copy explicit files at root level
cp "$HERMES_HOME/gateway_state.json" "$REPO_DIR/" 2>/dev/null || true
cp "$HERMES_HOME/channel_directory.json" "$REPO_DIR/" 2>/dev/null || true
cp "$HERMES_HOME/workspace-sessions.json" "$REPO_DIR/" 2>/dev/null || true

# Source GITHUB_TOKEN from bashrc
source "$HOME/.bashrc" 2>/dev/null || true

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
git -c user.email="ash@hermes.local" -c user.name="Ash (Auto-Backup)" \
  commit -m "Auto-backup: $CURRENT_TIME UTC

Hermes VPS backup - $(hostname)
Includes: config, profiles, skills, cron, memories, state, sessions"
git push origin main

echo "[$TIMESTAMP] Backup complete - $(git rev-parse --short HEAD)"
