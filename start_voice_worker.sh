#!/bin/bash
# start_voice_worker.sh
# Launches voice_worker.py safely in the background

WORKER="voice_worker.py"
LOG_DIR="memory/logs/system"
mkdir -p "$LOG_DIR"

echo "[$(date +%Y-%m-%dT%H:%M:%S)] Starting $WORKER..." | tee -a "$LOG_DIR/start_voice_worker.log"

nohup python3 "$WORKER" >> "$LOG_DIR/voice_worker.out" 2>&1 &

echo "[$(date +%Y-%m-%dT%H:%M:%S)] $WORKER launched in background." | tee -a "$LOG_DIR/start_voice_worker.log"
