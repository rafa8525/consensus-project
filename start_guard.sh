#!/bin/bash
# start_guard.sh
# Launch absorb_guard in a persistent loop with safety logging

cd ~/consensus-project || exit 1

while true; do
  echo "[start_guard] Running absorb_guard.py at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  python3 absorb_guard.py
  echo "[start_guard] Sleeping 30m before next run..."
  sleep 1800
done
