#!/usr/bin/env bash
set -euo pipefail

LOG="memory/logs/heartbeat/memory_absorption_heartbeat.log"
WARN="memory/logs/watchdog/weekly_alert_log.txt"
mkdir -p "$(dirname "$WARN")"

if [[ ! -f "$LOG" ]]; then
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [WARN] absorption log missing" >> "$WARN"
  exit 0
fi

last_ts=$(tail -1 "$LOG" | sed -n 's/^\[\([^]]*\)\].*/\1/p')
[[ -z "${last_ts:-}" ]] && exit 0

now_s=$(date -u +%s)
last_s=$(date -u -d "$last_ts" +%s)

# Alert if older than 20 minutes (1200 seconds)
if (( now_s - last_s >= 1200 )); then
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [WARN] absorption stale (last=$last_ts)" >> "$WARN"
fi
