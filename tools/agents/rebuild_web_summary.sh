#!/usr/bin/env bash
set -euo pipefail
DATE_DIR="memory/web_research/$(date +%F)"
OUT_META="$DATE_DIR/meta"
SUMMARY="$DATE_DIR/summary.csv"
mkdir -p "$DATE_DIR"
{
  echo "agent,url,status_code,title"
  for m in "$OUT_META"/*.meta; do
    [ -s "$m" ] || continue
    agent=$(grep -m1 '^agent=' "$m" | cut -d= -f2-)
    url=$(grep -m1 '^url=' "$m" | cut -d= -f2-)
    code=$(grep -m1 '^status_code=' "$m" | cut -d= -f2-)
    title=$(grep -m1 '^title=' "$m" | cut -d= -f2- | tr -d '\r\n')
    title=${title//\"/\"\"}
    printf '%s,"%s",%s,"%s"\n' "$agent" "$url" "$code" "$title"
  done
} > "$SUMMARY"
echo "[summary] wrote $SUMMARY"
