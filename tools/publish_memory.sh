#!/usr/bin/env bash
set -euo pipefail
LOCK=/tmp/publish_memory.lock
LOG=logs/absorb/absorb_guard.log
URL=$(cat config/GITHUB_MEMORY_REPO_URL.txt 2>/dev/null || echo "")
mkdir -p "$(dirname "$LOG")"

rsync_safe() {
  local src="$1" dest="$2"
  rsync -a --delete --exclude '.git' --delete-excluded \
        --ignore-errors --force --timeout=300 \
        "$src"/ "$dest"/ || rc=$?
  [[ ${rc:-0} -eq 24 || ${rc:-0} -eq 23 || ${rc:-0} -eq 0 ]]
}

{
  echo "[$(date -Is)] publish start"
  exec 8>"$LOCK"
  if ! flock -n 8; then echo "[skip] another publish/absorb running"; exit 0; fi
  [[ -z "$URL" ]] && { echo "[error] missing URL"; exit 1; }

  export GIT_TERMINAL_PROMPT=0
  TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
  git clone --quiet --depth=1 "$URL" "$TMP/repo" || { echo "[error] clone failed"; exit 1; }
  mkdir -p "$TMP/repo/memory"
  rsync_safe "memory" "$TMP/repo/memory" || { echo "[error] rsync failed"; exit 1; }

  cd "$TMP/repo"
  if git status --porcelain | grep -q .; then
    git config user.name autosync
    git config user.email autosync@local
    git add -A
    git commit -qm "memory: auto-publish $(date -Is)"
    git push --quiet && echo "[ok] pushed" || { echo "[error] push failed"; exit 1; }
  else
    echo "[skip] no changes to publish"
  fi
  echo "[$(date -Is)] publish done"
} >> "$LOG" 2>&1
