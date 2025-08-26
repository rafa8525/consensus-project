#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

. tools/lib/sync.sh

LOCK=/tmp/publish_memory.lock
LOG="$ROOT/logs/absorb/absorb_guard.log"
URL="$(cat config/GITHUB_MEMORY_REPO_URL.txt)"
mkdir -p "$(dirname "$LOG")"

{
  echo "[$(date -Is)] publish start"

  exec 8>"$LOCK"
  if ! flock -n 8; then
    echo "[skip] another publish/absorb running"; exit 0
  fi

  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  export GIT_TERMINAL_PROMPT=0

  git clone --quiet --depth=1 "$URL" "$TMP/repo"

  mkdir -p "$TMP/repo/memory"
  sync_memory_safe "$ROOT/memory" "$TMP/repo/memory"

  cd "$TMP/repo"
  if git diff --quiet && git diff --cached --quiet; then
    echo "[skip] no changes to publish"
  else
    git add -A memory
    git -c user.name=autosync -c user.email=autosync@local commit -qm "memory: auto-publish $(date -Is)"
    git push --quiet
    echo "[ok] pushed"
  fi

  echo "[$(date -Is)] publish done"
} >> "$LOG" 2>&1
