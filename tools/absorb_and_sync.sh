#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

git config --global --add safe.directory "$(pwd)"
git fetch origin
git checkout -q v1.1-dev || true
git pull --ff-only

# rotate giant volatile log if present (kept ignored)
if [ -f memory/logs/heartbeat/full_memory_absorption.log ]; then
  mkdir -p memory/logs/heartbeat/archive
  ts=$(date -u +%Y%m%d_%H%M%S)
  mv memory/logs/heartbeat/full_memory_absorption.log "memory/logs/heartbeat/archive/full_memory_absorption_${ts}.log" || true
  : > memory/logs/heartbeat/full_memory_absorption.log || true
fi

git add -A memory
if git diff --cached --quiet; then
  echo "No memory/ changes to sync."
else
  git commit -m "Auto-sync memory ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
  git push
fi

# verify + log proof
mkdir -p memory/logs/github_sync
out="$(tools/verify_memory_tree.sh || echo VERIFY_FAIL)"
{
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $(git rev-parse --short HEAD)"
  echo "$out"
} >> memory/logs/github_sync/sync.log || true
echo "$out"
