#!/bin/bash
# start_voice_guard.sh
# Safely launches voice_guard.py in background
LOG="memory/logs/system/start_voice_guard.log"
TS=$(date +"%Y-%m-%dT%H:%M:%S")

mkdir -p "$(dirname "$LOG")"
echo "[$TS] Starting voice_guard.py..." >> "$LOG"
nohup python3 voice_guard.py >> memory/logs/system/voice_guard.out 2>&1 &
echo "[$TS] voice_guard.py launched in background." >> "$LOG"
