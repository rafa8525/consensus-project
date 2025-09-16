#!/bin/bash
# start_github_sync.sh
# Safe launcher for github_sync.py with logging and heartbeat tracking

PROJECT_DIR="$HOME/consensus-project"
LOG_FILE="$PROJECT_DIR/memory/logs/system/github_sync_launcher.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] 🚀 Launching GitHub sync agent..." | tee -a "$LOG_FILE"

# Kill any stale sync processes
pkill -f github_sync.py 2>/dev/null || true

# Start fresh sync in background, detached from console
nohup python3 "$PROJECT_DIR/github_sync.py" >>"$LOG_FILE" 2>&1 &
PID=$!

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ✅ github_sync.py started (pid=$PID)" | tee -a "$LOG_FILE"
