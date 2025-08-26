#!/usr/bin/env bash
set -euo pipefail

out="logs/reports/errors_to_route.txt"
mkdir -p "$(dirname "$out")"

# Start fresh
: > "$out"

# If we have a heartbeat for today, we’ll suppress the “missing heartbeat” noise
today_hb="logs/scheduler/$(date +%F)_heartbeat_status.log"
have_hb="0"
[ -s "$today_hb" ] && have_hb="1"

# Collect only lines from files modified today (mtime 0)
# and ignore archived/ancient digests
tmp="$(mktemp)"
find logs -type f -mtime 0 -not -path '*/\.*' \
  \( -name '*.log' -o -name '*.txt' \) -print0 \
| xargs -0 grep -EIn 'error|failed|fatal|bash\\r|clone failed|loose object|vanished|missing heartbeat|no follow-up action|no data received|no module named|unexpected keyword argument' \
| grep -v 'logs/archive/' \
| awk -F: '{sub(/^[[:space:]]+/,"",$0); print $0}' > "$tmp" || true

# If we saw a heartbeat today, drop any "Missing heartbeat" complaints
if [ "$have_hb" = "1" ]; then
  grep -vi 'missing heartbeat' "$tmp" > "$tmp.filtered" || true
  mv "$tmp.filtered" "$tmp"
fi

# De-duplicate, cap to 200 lines, and write out
awk '!seen[$0]++' "$tmp" | head -n 200 > "$out"
rm -f "$tmp"

echo "[error_watcher] wrote $(wc -l < "$out") line(s) to $out"
