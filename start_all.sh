#!/bin/bash
# start_all.sh
# Unified launcher for Consensus Project
# Safely launches Master Control, Voice Guard, and GitHub Sync

PROJECT_DIR="$HOME/consensus-project"
LOG_FILE="$PROJECT_DIR/memory/logs/system/start_all.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] 🚀 Launching all core services..." | tee -a "$LOG_FILE"

# Kill stale processes
pkill -f master_control_loop.py 2>/dev/null || true
pkill -f voice_guard.py 2>/dev/null || true
pkill -f github_sync.py 2>/dev/null || true

# Start Master Control Loop
nohup python3 "$PROJECT_DIR/master_control_loop.py" >>"$LOG_FILE" 2>&1 &
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ✅ master_control_loop.py started (pid=$!)" | tee -a "$LOG_FILE"

# Start Voice Guard
nohup python3 "$PROJECT_DIR/voice_guard.py" >>"$LOG_FILE" 2>&1 &
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ✅ voice_guard.py started (pid=$!)" | tee -a "$LOG_FILE"

# Start GitHub Sync
nohup python3 "$PROJECT_DIR/github_sync.py" >>"$LOG_FILE" 2>&1 &
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ✅ github_sync.py started (pid=$!)" | tee -a "$LOG_FILE"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] 🎯 All services launched successfully." | tee -a "$LOG_FILE"
