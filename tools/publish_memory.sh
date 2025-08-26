#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
. tools/lib/sync.sh

LOCK=/tmp/publish_memory.lock
LOG="$ROOT/logs/absorb/publish.log"
mkdir -p "$(dirname "$LOG")"
: > "$LOG"   # truncate each run (avoid stale errors)

echo "[$(date -Is)] publish start" >> "$LOG"
exec 8>"$LOCK"
if ! flock -n 8; then
  echo "[skip] another publish/absorb running" >> "$LOG"; exit 0
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
URL="$(cat config/GITHUB_MEMORY_REPO_URL.txt)"
export GIT_TERMINAL_PROMPT=0

git_retry() {
  local tries="${2:-3}" i=1
  while :; do
    if eval "$1"; then return 0; fi
    if (( i>=tries )); then return 1; fi
    echo "[retry $i] $1" >> "$LOG"
    sleep $((i*3)); i=$((i+1))
  done
}

git_retry "git -c pack.threads=1 clone --quiet --depth=1 \"$URL\" \"$TMP/repo\"" 3 || {
  echo "[error] clone failed" >> "$LOG"; exit 1; }

mkdir -p "$TMP/repo/memory"
sync_memory_safe "$ROOT/memory" "$TMP/repo/memory" >> "$LOG" 2>&1 || true

(
  cd "$TMP/repo"
  git add -A memory
  if git diff --quiet && git diff --cached --quiet; then
    echo "[skip] no changes to publish" >> "$LOG"
  else
    git -c user.name=autosync -c user.email=autosync@local commit -qm "memory: auto-publish $(date -Is)"
    git_retry "git -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=30 -c pack.threads=1 -c http.maxRequests=2 push --quiet" 3 \
      && echo "[ok] pushed" >> "$LOG" || { echo "[error] push failed" >> "$LOG"; exit 1; }
  fi
)

echo "[$(date -Is)] publish done" >> "$LOG"
