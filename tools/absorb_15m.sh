#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

LOCK="memory/logs/sanity/absorb_15m.lock"
mkdir -p "$(dirname "$LOCK")"
exec 9>"$LOCK"

if command -v flock >/dev/null 2>&1; then
  # single-run guard (releases when script exits)
  if ! flock -n 9; then
    echo "absorb already running; skipping."
    exit 0
  fi
else
  # fallback: timestamp guard (~14 min)
  if [ -f "$LOCK" ] && find "$LOCK" -mmin -14 | grep -q .; then
    echo "absorb already running recently; skipping."
    exit 0
  fi
fi

date -u +"%Y-%m-%dT%H:%M:%SZ" > "$LOCK"

# Absorb + index
python3 tools/absorb_memory.py || true

# Git sync + verify (pushes to v1.1-dev)
./tools/absorb_and_sync.sh
