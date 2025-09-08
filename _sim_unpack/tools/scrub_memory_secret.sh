#!/usr/bin/env bash
set -euo pipefail
QUIET="${QUIET:-1}"
LOG_DIR="logs/scrub"; mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/scrub_$(date +%Y%m%d-%H%M%S).log"
say(){ if (( QUIET==0 )); then echo "[$(basename "$0")] $*"; else printf '%s %s\n' "[$(date -Is)]" "$*" >>"$LOG"; fi; }
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; cd "$ROOT"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
BAD_PATH="memory/logs/system/github_sync_log.md"
export GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/echo

# ensure clean tree (caller already stashed)
git reset --hard >>"$LOG" 2>&1
git clean -fdx >>"$LOG" 2>&1 || true

# rewrite history to remove the file everywhere
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f \
  --index-filter 'git rm -r --cached --ignore-unmatch memory/logs/system/github_sync_log.md' \
  --prune-empty -- "$BRANCH" >>"$LOG" 2>&1

# clean up rewrite refs
git for-each-ref --format="%(refname)" refs/original/ | xargs -r -n1 git update-ref -d >>"$LOG" 2>&1 || true
git reflog expire --expire=now --all >>"$LOG" 2>&1 || true
git gc --prune=now --aggressive >>"$LOG" 2>&1 || true

# push cleaned history (use PAT URL if present)
PUSH_URL="$(cat config/GITHUB_MEMORY_REPO_URL.txt 2>/dev/null || echo "")"
if [ -n "$PUSH_URL" ]; then
  git push "$PUSH_URL" "+$BRANCH:$BRANCH" --force-with-lease >>"$LOG" 2>&1 || echo "[warn] push failed (see $LOG)"
else
  git push origin "+$BRANCH:$BRANCH" --force-with-lease >>"$LOG" 2>&1 || echo "[warn] push failed (see $LOG)"
fi

echo "[scrub] done; log: $LOG"
