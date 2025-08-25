#!/usr/bin/env bash
set -euo pipefail
out="logs/reports/errors_to_route.txt"
mkdir -p "$(dirname "$out")"
: > "$out"
# Pull obvious errors from recent logs (adjust patterns/paths as needed)
grep -REIi 'error|failed|fatal|bash\\r|clone failed|loose object|vanished' \
  logs 2>/dev/null | awk -F: '{sub(/^[[:space:]]+/,"",$0); print $0}' | head -n 200 >> "$out" || true
# De-duplicate
awk '!seen[$0]++' "$out" > "$out.tmp" && mv "$out.tmp" "$out"
echo "[error_watcher] wrote $(wc -l < "$out") line(s) to $out"
