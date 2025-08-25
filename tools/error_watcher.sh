#!/usr/bin/env bash
set -euo pipefail
out="logs/reports/errors_to_route.txt"
mkdir -p "$(dirname "$out")"
: > "$out"
grep -REIi 'error|failed|fatal|bash\\r|clone failed|loose object|vanished|missing heartbeat|no follow-up action|no data received|no module named|unexpected keyword argument' \
  logs 2>/dev/null | awk -F: '{sub(/^[[:space:]]+/,"",$0); print $0}' | head -n 200 >> "$out" || true
awk '!seen[$0]++' "$out" > "$out.tmp" && mv "$out.tmp" "$out"
echo "[error_watcher] wrote $(wc -l < "$out") line(s) to $out"
