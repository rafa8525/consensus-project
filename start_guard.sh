#!/bin/bash
# start_guard.sh
# Launches mcl_guard.py safely in the background
# Will NOT close your console

GUARD="mcl_guard.py"
LOG_DIR="memory/logs/system"
mkdir -p "$LOG_DIR"

echo "[$(date +%Y-%m-%dT%H:%M:%S)] Starting $GUARD..." | tee -a "$LOG_DIR/start_guard.log"

# Run the guard in the background, immune to console close
nohup python3 "$GUARD" >> "$LOG_DIR/mcl_guard.out" 2>&1 &

echo "[$(date +%Y-%m-%dT%H:%M:%S)] $GUARD launched in background." | tee -a "$LOG_DIR/start_guard.log"
