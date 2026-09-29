#!/bin/bash
# start_master_control.sh
# Safe launcher for master_control_loop.py with logging
PROJECT_DIR="$HOME/consensus-project"
LOG_FILE="$PROJECT_DIR/memory/logs/system/master_control_launcher.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] 🚀 Launching Master Control Loop..." | tee -a "$LOG_FILE"

# Kill any stale processes
# MCL singleton lock safely rejects duplicate starts; do not kill a healthy MCL.

# Start fresh in background, detached from console
nohup python3 "$PROJECT_DIR/tools/master_control_loop.py" >>"$LOG_FILE" 2>&1 &

PID=$!
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ℹ️ master_control_loop.py launch requested (pid=$PID)" | tee -a "$LOG_FILE"
