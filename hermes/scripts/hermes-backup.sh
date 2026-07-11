#!/bin/bash
# Hermes VPS Backup Script
# Backs up all config, skills, profiles, and state to GitHub
# Runs via cron job - no_agent=True

set -e
REPO_DIR="/home/admin/hermes-backup"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M UTC")

# Extract PAT from git-credentials and export as GITHUB_TOKEN env var
# Format: https://username:TOKEN@github.com
if [ -f "$HOME/.git-credentials" ]; then
  TOKEN=$(sed -n 's|https://[^:]*:\([^@]*\)@github.com|\1|p' "$HOME/.git-credentials")
  if [ -n "$TOKEN" ]; then
    export GITHUB_TOKEN="$TOKEN"
    echo "[$TIMESTAMP] GITHUB_TOKEN set from git-credentials"
  fi
fi

cd "$REPO_DIR"

# Step 1: Add all changes (respects .gitignore)
git add -A

# Step 2: Check if there's anything to commit
if git diff --cached --quiet; then
  echo "[$TIMESTAMP] No changes to back up. Skipping commit."
  exit 0
fi

# Step 3: Commit and push
CURRENT_TIME=$(date +"%Y-%m-%d_%H-%M")
git commit -m "Auto-backup: $CURRENT_TIME UTC

Hermes VPS weekly backup - $(hostname)
Includes: config, profiles, skills, cron, memories, plugins, webui-mvp"
git push origin main

echo "[$TIMESTAMP] Backup complete - $(git rev-parse --short HEAD)"