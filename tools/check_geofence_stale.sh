#!/usr/bin/env bash
set -euo pipefail
LOGDIR="memory/logs/geofencing"
WARN="memory/logs/watchdog/weekly_alert_log.txt"
mkdir -p "$(dirname "$WARN")" "$LOGDIR"
today=$(date -u +%F)
f="$LOGDIR/heartbeat_${today}.md"
if [[ ! -f "$f" ]]; then
  echo "[$(date -u +%FT%TZ)] [WARN] geofencing heartbeat missing" >> "$WARN"; exit 0
fi
last_ts=$(tail -1 "$f" | sed -n 's/^\[\([^]]*\)\].*/\1/p')
[[ -z "$last_ts" ]] && { echo "[$(date -u +%FT%TZ)] [WARN] geofencing heartbeat unparsable" >> "$WARN"; exit 0; }
now_s=$(date -u +%s); last_s=$(date -u -d "$last_ts" +%s)
(( now_s - last_s < 1800 )) || echo "[$(date -u +%FT%TZ)] [WARN] geofencing heartbeat stale (>30m)" >> "$WARN"
