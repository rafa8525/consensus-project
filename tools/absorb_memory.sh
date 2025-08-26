#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
. tools/lib/sync.sh

LOG="$ROOT/logs/absorb/absorb.log"
mkdir -p "$(dirname "$LOG")"
: > "$LOG"   # truncate each run

echo "[$(date -Is)] absorb start" >> "$LOG"

CACHE_DIR="$ROOT/.cache/github_memory_repo"
URL="$(cat config/GITHUB_MEMORY_REPO_URL.txt)"
export GIT_TERMINAL_PROMPT=0
mkdir -p "$CACHE_DIR"

git_retry() {
  local tries="${2:-3}" i=1
  while :; do
    if eval "$1"; then return 0; fi
    if (( i>=tries )); then return 1; fi
    echo "[retry $i] $1" >> "$LOG"
    sleep $((i*3)); i=$((i+1))
  done
}

if [ ! -d "$CACHE_DIR/.git" ]; then
  git_retry "git -c pack.threads=1 clone --quiet --depth=1 \"$URL\" \"$CACHE_DIR\"" 3 \
    || { echo "[error] clone failed" >> "$LOG"; exit 1; }
else
  git -C "$CACHE_DIR" remote set-url origin "$URL" || true
  git_retry "git -C \"$CACHE_DIR\" -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=30 -c pack.threads=1 -c http.maxRequests=2 fetch --quiet --prune origin" 3 \
    || { echo "[warn] fetch failed; continuing with last cached data" >> "$LOG"; }
  DEFBR="$(git -C "$CACHE_DIR" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || echo origin/main)"
  DEFBR="${DEFBR#origin/}"
  git -C "$CACHE_DIR" reset --hard "origin/$DEFBR" --quiet || true
fi

mkdir -p "$ROOT/memory"
sync_memory_safe "$CACHE_DIR/memory" "$ROOT/memory" >> "$LOG" 2>&1 || true

echo "[$(date -Is)] absorb done" >> "$LOG"
