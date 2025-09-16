#!/bin/bash
# start_guard.sh
# Safe launcher for mcl_guard.py with logging and heartbeat tracking

PROJECT_DIR="$HOME/consensus-project"
LOG_FILE="$PROJECT_DIR/memory/logs/system/mcl_guard_launcher.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] 🚀 Launching MCL Guard..." | tee -a "$LOG_FILE"

# Kill any stale guard processes
pkill -f mcl_guard.py 2>/dev/null || true

# Start fresh guard in background, detached from console
nohup python3 "$PROJECT_DIR/mcl_guard.py" >>"$LOG_FILE" 2>&1 &

PID=$!
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ✅ mcl_guard.py started (pid=$PID)" | tee -a "$LOG_FILE"
