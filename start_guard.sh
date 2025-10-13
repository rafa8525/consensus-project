#!/bin/bash
# start_guard.sh
# Enhanced launcher for absorb_guard.py
# - Auto-kills old process before launch
# - Archives previous log with UTC timestamp
# - Auto-restarts if absorb_guard.py crashes
# - Displays live log output

cd ~/consensus-project || exit 1

LOGDIR="memory/logs/system"
LOGFILE="$LOGDIR/absorb_guard.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H-%M-%SZ")
ARCHIVE_LOG="$LOGDIR/absorb_guard_$TIMESTAMP.log"

echo "[start_guard] ===== Starting absorb_guard at $TIMESTAMP (UTC) ====="

# --- Stop any old instances ---
if pgrep -f absorb_guard.py >/dev/null; then
    echo "[start_guard] Old instance detected — stopping it..."
    pkill -f absorb_guard.py
    sleep 2
fi

# --- Prepare log directory ---
mkdir -p "$LOGDIR"

# --- Rotate old log ---
if [ -f "$LOGFILE" ]; then
    mv "$LOGFILE" "$ARCHIVE_LOG"
    echo "[start_guard] Previous log archived -> $ARCHIVE_LOG"
fi

# --- Start new instance ---
touch "$LOGFILE"
nohup python3 absorb_guard.py >> "$LOGFILE" 2>&1 &
sleep 3

# --- Verify launch ---
if pgrep -f absorb_guard.py >/dev/null; then
    echo "[start_guard] absorb_guard.py is now running."
else
    echo "[start_guard] ❌ Failed to start absorb_guard.py."
    exit 1
fi

# --- Background restart monitor ---
(
    while true; do
        if ! pgrep -f absorb_guard.py >/dev/null; then
            echo "[start_guard] ⚠️ absorb_guard.py stopped unexpectedly. Restarting..."
            nohup python3 absorb_guard.py >> "$LOGFILE" 2>&1 &
            sleep 3
            if pgrep -f absorb_guard.py >/dev/null; then
                echo "[start_guard] ✅ Restart successful at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
            else
                echo "[start_guard] ❌ Restart failed."
            fi
        fi
        sleep 60
    done
) &

# --- Live tail for monitoring ---
echo "[start_guard] Now tailing $LOGFILE ..."
tail -f "$LOGFILE"
