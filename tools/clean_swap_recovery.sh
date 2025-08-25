#!/usr/bin/env bash
set -euo pipefail
MAIN_REPO="$HOME/consensus-project"
URL_FILE="$MAIN_REPO/config/GITHUB_MEMORY_REPO_URL.txt"
[[ -d "$MAIN_REPO" ]] || { echo "[error] repo dir not found"; exit 1; }
[[ -s "$URL_FILE" ]] || { echo "[error] missing $URL_FILE"; exit 1; }
URL="$(cat "$URL_FILE")"
export GIT_TERMINAL_PROMPT=0

CLEAN_DIR="${MAIN_REPO}.clean.$(date +%s)"
BACKUP_DIR="${MAIN_REPO}.backup.$(date +%s)"

echo "[$(date -Is)] fresh clone → $CLEAN_DIR"
git clone "$URL" "$CLEAN_DIR"

echo "[$(date -Is)] rsync working tree into clean (exclude metadata)"
rsync -a --delete \
  --exclude '.git' --exclude '.cache' --exclude 'memory/github_memory_repo' \
  --exclude 'logs' --exclude 'memory/logs' --exclude '*.log' \
  "$MAIN_REPO"/ "$CLEAN_DIR"/

echo "[$(date -Is)] atomic swap"
mv "$MAIN_REPO" "$BACKUP_DIR"
mv "$CLEAN_DIR" "$MAIN_REPO"
echo "[ok] swapped. Backup: $BACKUP_DIR"
