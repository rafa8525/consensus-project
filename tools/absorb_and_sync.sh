#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# Safety + freshness
git config --global --add safe.directory "$(pwd)"
git fetch origin

# Rebase our current HEAD onto remote v1.1-dev so push fast-forwards
git rebase origin/v1.1-dev || true

# Rotate the giant volatile log if it exists (still ignored by git)
if [ -f memory/logs/heartbeat/full_memory_absorption.log ]; then
  mkdir -p memory/logs/heartbeat/archive
  ts=$(date -u +%Y%m%d_%H%M%S)
  mv memory/logs/heartbeat/full_memory_absorption.log "memory/logs/heartbeat/archive/full_memory_absorption_${ts}.log" || true
  : > memory/logs/heartbeat/full_memory_absorption.log || true
fi

# Stage memory only
git add -A memory

# Commit only if there are staged changes
if git diff --cached --quiet; then
  echo "No memory/ changes to sync."
else
  git commit -m "Auto-sync memory ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
  git push origin HEAD:v1.1-dev
fi

# Verify + log proof
mkdir -p memory/logs/github_sync
out="$(tools/verify_memory_tree.sh || echo VERIFY_FAIL)"
{
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $(git rev-parse --short HEAD)"
  echo "$out"
} >> memory/logs/github_sync/sync.log || true
echo "$out"
