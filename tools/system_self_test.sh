#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
WARN="memory/logs/watchdog/weekly_alert_log.txt"; mkdir -p "$(dirname "$WARN")"
fail=0

# 1) Absorb recency (<20m)
last_ts=$(sed -n 's/^\[\([^]]*\)\].*/\1/p' memory/logs/heartbeat/memory_absorption_heartbeat.log | tail -1 || true)
if [[ -z "$last_ts" ]] || ! last_s=$(date -u -d "$last_ts" +%s 2>/dev/null); then
  echo "[$(date -u +%FT%TZ)] [WARN] heartbeat missing/unparsable" >> "$WARN"; fail=1
else
  now_s=$(date -u +%s); (( now_s - last_s < 1200 )) || { echo "[$(date -u +%FT%TZ)] [WARN] last absorb >20m" >> "$WARN"; fail=1; }
fi

# 2) Index exists
[[ -f memory/index/search_index.json ]] || { echo "[$(date -u +%FT%TZ)] [WARN] index missing" >> "$WARN"; fail=1; }

# 3) Remote push sanity (latest commit touches memory/ within 30m)
git fetch -q origin
read h when subj < <(git log -n 1 --date=unix --pretty=format:'%H %ad %s' origin/v1.1-dev -- memory || echo "")
if [[ -z "${when:-}" ]]; then
  echo "[$(date -u +%FT%TZ)] [WARN] no recent memory commit on origin" >> "$WARN"; fail=1
else
  now=$(date -u +%s); (( now - when < 1800 )) || { echo "[$(date -u +%FT%TZ)] [WARN] origin memory commit >30m" >> "$WARN"; fail=1; }
fi

# 4) Large-file guard (>95MB, outside ignored archive)
bad=$(find memory -type f -size +95M -not -path '*/heartbeat/archive/*' -print | head -1 || true)
[[ -z "$bad" ]] || { echo "[$(date -u +%FT%TZ)] [WARN] large file detected: $bad" >> "$WARN"; fail=1; }

# Result marker (for quick greps)
touch memory/logs/system/health_check_passed.timestamp
exit $fail
