#!/usr/bin/env bash
# Absorb + Sync (with daily status snapshot)
# - Rotates the giant heartbeat log
# - Publishes a 14-day absorb status snapshot to memory/logs/absorb/status.txt
# - Stages memory/, commits only if there are changes, and pushes to v1.1-dev
# - Uses a lock to avoid overlapping runs

set -euo pipefail

# Acquire a non-blocking lock so AM/PM jobs never overlap
LOCK_FILE="/tmp/absorb_and_sync.lock"
exec 9>"$LOCK_FILE" || true
if ! flock -n 9; then
  echo "[absorb_and_sync] Another instance is running; exiting."
  exit 0
fi

# Go to repo root
cd "$(git rev-parse --show-toplevel)"

# Ensure Git will operate in this directory (PythonAnywhere safety)
git config --global --add safe.directory "$(pwd)" || true

ts="$(date -u +%Y%m%dT%H%M%SZ)"

# --- Rotate + compress giant volatile log (archive dir is gitignored) ---
mkdir -p memory/logs/heartbeat/archive
if [[ -f memory/logs/heartbeat/full_memory_absorption.log ]]; then
  mv memory/logs/heartbeat/full_memory_absorption.log \
     "memory/logs/heartbeat/archive/full_memory_absorption_${ts}.log" || true
  gzip -9 "memory/logs/heartbeat/archive/full_memory_absorption_${ts}.log" 2>/dev/null || true
  # Start a fresh log file
  : > memory/logs/heartbeat/full_memory_absorption.log || true
fi

# --- Publish absorb status snapshot (so you can SEE AM/PM results) ---
mkdir -p memory/logs/absorb
python3 tools/absorb_status_report.py 14 > memory/logs/absorb/status.txt || true

# --- Stage memory only (includes status.txt) ---
git add -A memory

# --- Commit only if there are changes, then push directly to v1.1-dev ---
if git diff --cached --quiet; then
  echo "[absorb_and_sync] No memory/ changes to sync."
else
  git commit -m "Auto-sync memory ($(date -u +%Y-%m-%dT%H:%M:%SZ))" || true
  git push origin HEAD:v1.1-dev
fi

# --- Verify & log proof (optional; keeps a small log you can inspect) ---
mkdir -p memory/logs/github_sync
out="$({ tools/verify_memory_tree.sh || echo VERIFY_FAIL; } 2>&1 || true)"
{
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $(git rev-parse --short HEAD)"
  echo "$out"
} > memory/logs/github_sync/sync.log || true
echo "[absorb_and_sync] Wrote memory/logs/github_sync/sync.log"

echo "[absorb_and_sync] Done at ${ts}"
