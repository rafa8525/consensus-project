#!/usr/bin/env bash
set -euo pipefail

# ---- Quiet logging (default on) ----
QUIET="${QUIET:-1}"
ts="$(date +%Y%m%d-%H%M%S)"
LOG_DIR="logs/restore"; mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/restore_$ts.log"
say(){ if (( QUIET==0 )); then echo "[$(basename "$0")] $*"; else printf '%s %s\n' "[$(date -Is)]" "$*" >>"$LOG"; fi; }

# ---- Setup & safety backup ----
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; cd "$ROOT"
tar -czf "backups/memory_pre_restore_$ts.tgz" memory 2>/dev/null || true
say "[backup] created backups/memory_pre_restore_$ts.tgz"

# ---- Non-interactive git + short timeouts ----
export GIT_TERMINAL_PROMPT=0
export GIT_ASKPASS=/bin/echo

timeout 20s git fetch origin --quiet || say "[warn] fetch failed; continuing with local history"

# ---- Choose restore source: origin/main first, otherwise last good commit ----
if git cat-file -e origin/main:memory >/dev/null 2>&1; then
  timeout 15s git checkout origin/main -- memory >>"$LOG" 2>&1 || say "[error] checkout from origin/main failed"
  SRC_DESC="origin/main"
else
  GOOD_COMMIT="$(git rev-list -n1 --before='2025-08-26 23:15:00' HEAD -- memory || true)"
  [ -z "${GOOD_COMMIT:-}" ] && GOOD_COMMIT="$(git log -n1 --format=%H -- memory || true)"
  [ -z "${GOOD_COMMIT:-}" ] && { echo "[restore] no historical memory/ found. See $LOG"; exit 1; }
  timeout 15s git checkout "$GOOD_COMMIT" -- memory >>"$LOG" 2>&1
  SRC_DESC="commit $GOOD_COMMIT"
fi

# ---- Commit only if there are changes ----
git add memory >>"$LOG" 2>&1
if ! git diff --cached --quiet; then
  git commit -m "memory: restore contents ($SRC_DESC $ts)" >>"$LOG" 2>&1 || true
fi

# ---- Push quietly if PAT URL file exists (reuses your memory PAT file) ----
PUSHED=0
if [ -s config/GITHUB_MEMORY_REPO_URL.txt ]; then
  PUSH_URL="$(cat config/GITHUB_MEMORY_REPO_URL.txt)"
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  timeout 25s git push "$PUSH_URL" "HEAD:$BRANCH" >>"$LOG" 2>&1 && PUSHED=1 || say "[warn] push failed (auth/network)"
else
  say "[info] config/GITHUB_MEMORY_REPO_URL.txt missing; skipped push"
fi

# ---- LFS blobs (best effort) ----
git lfs pull --include="memory/**" --exclude="" >>"$LOG" 2>&1 || true

# ---- Tiny summary only ----
COUNT="$(find memory -type f | wc -l | tr -d ' ')"
echo "[restore] done. files in memory/: $COUNT"
(( PUSHED==1 )) && echo "[restore] changes pushed." || echo "[restore] not pushed—local only."
echo "[restore] log: $LOG"
