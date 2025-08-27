#!/usr/bin/env bash
set -euo pipefail
DATE_DIR="memory/web_research/$(date +%F)"
OUT_META="$DATE_DIR/meta"
SUMMARY="$DATE_DIR/summary.csv"
[ -d "$OUT_META" ] || { echo "Meta dir not found: $OUT_META" >&2; exit 1; }
mkdir -p "$DATE_DIR"
{
  echo "agent,url,status_code,title"
  find "$OUT_META" -type f -name "*.meta" 2>/dev/null | sort | while read -r m; do
    [[ -s "$m" ]] || continue
    agent="$(grep -m1 '^agent=' "$m" | cut -d= -f2-)"
    url="$(grep -m1 '^url=' "$m" | cut -d= -f2-)"
    code="$(grep -m1 '^status_code=' "$m" | cut -d= -f2-)"
    title="$(grep -m1 '^title=' "$m" | cut -d= -f2- | tr -d '\r\n')"
    title="${title//\"/\"\"}"
    printf '%s,"%s",%s,"%s"\n' "${agent:-unknown}" "${url:-unknown}" "${code:-000}" "${title:-}"
  done
} > "$SUMMARY"
echo "[$(date '+%H:%M:%S')] Summary written: $SUMMARY ($(tail -n +2 "$SUMMARY" | wc -l) rows)"
