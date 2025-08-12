#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# Prevent overlaps (10-min lock)
LOCK="memory/logs/sanity/absorb_15m.lock"
mkdir -p "$(dirname "$LOCK")"
if [ -f "$LOCK" ] && find "$LOCK" -mmin -10 | grep -q .; then
  echo "absorb already running recently; skipping."
  exit 0
fi
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$LOCK"

# Absorb + index
python3 tools/absorb_memory.py || true

# Git sync + verify (pushes to v1.1-dev)
./tools/absorb_and_sync.sh
