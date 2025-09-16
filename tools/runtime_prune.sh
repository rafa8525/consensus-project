#!/bin/bash
# tools/runtime_prune.sh
# Safe runtime log pruning for Consensus Project
# Will NOT close your console.

PRUNE_LOG="memory/logs/system/runtime_prune.log"
TS=$(date +"%Y-%m-%dT%H:%M:%S")

mkdir -p "$(dirname "$PRUNE_LOG")"

echo "[$TS] 🧹 Runtime prune started..." >> "$PRUNE_LOG"

# 1. Delete compressed rotated logs older than 14 days
find memory/logs -type f -name "*.gz" -mtime +14 -print -delete >> "$PRUNE_LOG" 2>&1

# 2. Truncate any huge log files (>50 MB) instead of deleting
find memory/logs -type f -size +50M | while read -r f; do
  echo "[$TS] ⚠️ Truncating oversized log: $f" >> "$PRUNE_LOG"
  : > "$f"
done

echo "[$TS] ✅ Runtime prune finished." >> "$PRUNE_LOG"
