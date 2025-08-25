#!/usr/bin/env bash
set -euo pipefail
LOCK=/tmp/absorb_memory.lock
LOG=logs/absorb/absorb_guard.log
REPO_DIR=.cache/github_memory_repo
TARGET_DIR=memory
URL_FILE=config/GITHUB_MEMORY_REPO_URL.txt

mkdir -p "$(dirname "$LOG")" "$REPO_DIR" "$TARGET_DIR" .cache

rsync_safe() {
  local src="$1" dest="$2"
  rsync -a --delete --exclude '.git' --delete-excluded \
        --ignore-errors --force --timeout=300 \
        "$src"/ "$dest"/ || rc=$?
  [[ ${rc:-0} -eq 24 || ${rc:-0} -eq 23 || ${rc:-0} -eq 0 ]]
}

{
  echo "[$(date -Is)] absorb start"
  exec 9>"$LOCK"
  if ! flock -n 9; then echo "[skip] another absorb/publish running"; exit 0; fi

  if [[ ! -s "$URL_FILE" ]]; then echo "[warn] $URL_FILE missing"; echo "[$(date -Is)] absorb done"; exit 0; fi
  URL="$(cat "$URL_FILE")"
  if [[ "$URL" == *"<owner>"* || "$URL" == *"<repo>"* ]]; then echo "[warn] placeholder URL"; echo "[$(date -Is)] absorb done"; exit 0; fi

  export GIT_TERMINAL_PROMPT=0
  if [[ ! -d "$REPO_DIR/.git" ]]; then
    git clone --quiet --depth=1 "$URL" "$REPO_DIR" || { echo "[error] clone failed"; exit 1; }
  else
    git -C "$REPO_DIR" fetch --quiet || true
    git -C "$REPO_DIR" reset --hard @{u} 2>/dev/null || git -C "$REPO_DIR" pull --quiet || true
  fi

  SRC="$REPO_DIR"; [[ -d "$REPO_DIR/memory" ]] && SRC="$REPO_DIR/memory"
  rsync_safe "$SRC" "$TARGET_DIR" || { echo "[error] rsync failed"; exit 1; }

  echo "[$(date -Is)] absorb done"
} >> "$LOG" 2>&1
