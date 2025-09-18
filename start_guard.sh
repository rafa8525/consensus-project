#!/bin/bash
# start_guard.sh
# Launch absorb_guard.py in background and tail its log for monitoring

cd ~/consensus-project || exit 1

LOGFILE="memory/logs/system/absorb_guard.log"

echo "[start_guard] Launching absorb_guard.py at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Kill any old processes to avoid duplicates
pkill -f absorb_guard.py 2>/dev/null

# Ensure log file exists
mkdir -p "$(dirname "$LOGFILE")"
touch "$LOGFILE"

# Start the guard in the background, append logs
nohup python3 absorb_guard.py >> "$LOGFILE" 2>&1 &

# Give it a moment to start
sleep 2

# Tail the log in real time (follows background process)
echo "[start_guard] Now tailing $LOGFILE ..."
tail -f "$LOGFILE"
