#!/usr/bin/env bash
set -euo pipefail
OUT="logs/reports/errors_to_route.txt"
mkdir -p "$(dirname "$OUT")"

# Grep common failure signatures across your logs (project + memory)
PAT='(error|fatal|failed|exception|segmentation fault|No such file or directory|denied|corrupt|clone failed|requested URL returned error|bash\\r|should have been pointers|rsync warning: some files vanished)'
{
  grep -RinEI "$PAT" logs 2>/dev/null || true
  grep -RinEI "$PAT" memory/logs 2>/dev/null || true
  # Non-zero rc lines from JSON-like logs (a rough but effective pass)
  grep -RinE '"rc"[^0-9]*[1-9]' memory/logs 2>/dev/null || true
} \
| sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//' \
| awk 'NF' \
| sort -u \
| tail -n 200 > "$OUT"

if [[ ! -s "$OUT" ]]; then
  echo "[info] no_errors_detected" > "$OUT"
fi

echo "$OUT"
