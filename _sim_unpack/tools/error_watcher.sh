#!/usr/bin/env bash
set -euo pipefail
out="logs/reports/errors_to_route.txt"
mkdir -p "$(dirname "$out")"
: > "$out"

today_hb="logs/scheduler/$(date +%F)_heartbeat_status.log"
have_hb="0"; [ -s "$today_hb" ] && have_hb="1"

tmp="$(mktemp)"
# Only today’s files; prune archives & our own report folder; ignore hidden paths
find logs -type d \( -path 'logs/archive' -o -path 'logs/reports' -o -path 'logs/.git' \) -prune -o \
     -type f -mtime 0 \( -name '*.log' -o -name '*.txt' \) -print0 \
| xargs -0 grep -Pin --binary-files=without-match \
  '\b(error|failed|fatal|exception|traceback)\b|bash\\r|clone failed|loose object|vanished|missing heartbeat|no follow-up action|no data received|no module named|unexpected keyword argument' \
| awk -F: '{sub(/^[[:space:]]+/,"",$0); print $0}' > "$tmp" || true

# If we saw a heartbeat today, suppress stale “Missing heartbeat” lines.
if [ "$have_hb" = "1" ]; then
  grep -vi 'missing heartbeat' "$tmp" > "$tmp.filtered" || true
  mv "$tmp.filtered" "$tmp"
fi

awk '!seen[$0]++' "$tmp" | head -n 200 > "$out"
rm -f "$tmp"
echo "[error_watcher] wrote $(wc -l < "$out") line(s) to $out"
