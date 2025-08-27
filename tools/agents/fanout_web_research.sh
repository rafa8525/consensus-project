#!/usr/bin/env bash
set -euo pipefail

# --- config ---
readonly SCRIPT_NAME="$(basename "$0")"
readonly MAX_WORKERS="${MAX_WORKERS:-4}"
readonly CONNECT_TIMEOUT="${CONNECT_TIMEOUT:-8}"
readonly MAX_TIME="${MAX_TIME:-20}"
readonly MAX_RETRIES="${MAX_RETRIES:-1}"
readonly RETRY_DELAY="${RETRY_DELAY:-1}"
readonly USER_AGENT="ConsensusHarvester/1.0"
readonly DRY_RUN="${DRY_RUN:-0}"
readonly QUIET="${QUIET:-1}"   # default quiet to avoid console flood

# --- helpers ---
log() {
  if [[ ${QUIET} -eq 0 ]]; then
    echo "[$SCRIPT_NAME] $*" >&2
  else
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$SCRIPT_NAME] $*" >&2
  fi
}
die() { log "ERROR: $*"; exit 2; }

# --- root + csv ---
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT" || die "Cannot change to project root: $ROOT"
CSV="${1:-csv/55_Agents___Support_Sites.csv}"
DATE_DIR="memory/web_research/$(date +%F)"
OUT_RAW="$DATE_DIR/raw"
OUT_META="$DATE_DIR/meta"
TARGETS_CSV="$DATE_DIR/targets.csv"
SUMMARY_CSV="$DATE_DIR/summary.csv"

# quiet mode redirect (after DATE_DIR is known)
if [[ ${QUIET} -eq 1 ]]; then
  mkdir -p "$DATE_DIR" 2>/dev/null || true
  LOG_FILE="$DATE_DIR/fanout.log"
  exec >>"$LOG_FILE" 2>&1
fi

# --- csv validation ---
if [[ ! -f "$CSV" ]]; then
  log "CSV not found: $CSV"
  log "Try: cp /mnt/data/55_Agents___Support_Sites.csv $CSV"
  log "Or run: $0 /path/to/your.csv"
  log "cwd: $(pwd)"
  die "CSV file missing"
fi
if [[ ! -s "$CSV" ]]; then
  die "CSV exists but is empty: $CSV"
fi

# --- prep outputs ---
mkdir -p "$OUT_RAW" "$OUT_META"
log "Starting web research crawl"
log "CSV: $CSV ($(wc -l < "$CSV") lines)"
log "OUT: $DATE_DIR"
log "Workers: $MAX_WORKERS"
log "Dry run: $([[ $DRY_RUN -eq 1 ]] && echo YES || echo NO)"

# --- URL normalization for a few common roots (non-destructive) ---
normalize_url() {
  local url="$1"
  case "$url" in
    https://azure.microsoft.com|https://azure.microsoft.com/)
      echo "https://learn.microsoft.com/azure/" ;;
    https://learn.microsoft.com|https://learn.microsoft.com/)
      echo "https://learn.microsoft.com/" ;;
    *) echo "$url" ;;
  esac
}

# --- extract agent,url pairs (robust) ---
{
  echo "agent,url"
  tail -n +2 "$CSV" | tr -d '\r' | while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    agent="$(echo "$line" | cut -d, -f1 | sed 's/^[[:space:]"]*//; s/[[:space:]"]*$//')"
    url="$(echo "$line" | grep -oE 'https?://[^[:space:],"\047]+' | head -n1 | sed 's/["\047]*$//')"
    [[ -n "$agent" && -n "$url" ]] || continue
    url="$(normalize_url "$url")"
    printf '%s,%s\n' "$agent" "$url"
  done
} > "$TARGETS_CSV"
total_targets=$(tail -n +2 "$TARGETS_CSV" | wc -l | tr -d ' ')
log "Extracted $total_targets agent,url pairs"
[[ $total_targets -gt 0 ]] || die "No valid agent,url pairs found"

# --- fetcher ---
fetch_url() {
  local agent="$1" url="$2"
  local safe_agent="$(echo "$agent" | sed 's/[^A-Za-z0-9._-]/_/g')"
  local raw_file="$OUT_RAW/${safe_agent}.html"
  local meta_file="$OUT_META/${safe_agent}.meta"
  local attempt=0 max_attempts=$((MAX_RETRIES + 1))
  local status_code="" status_line="" title=""

  if [[ -f "$meta_file" && -f "$raw_file" ]]; then
    echo "[$agent] cached"
    return 0
  fi

  while [[ $attempt -lt $max_attempts ]]; do
    attempt=$((attempt + 1))
    if curl -fsSL --compressed \
       --connect-timeout "$CONNECT_TIMEOUT" \
       --max-time "$MAX_TIME" \
       --retry 2 --retry-delay 1 --retry-all-errors \
       -A "$USER_AGENT" \
       -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
       --write-out "HTTPSTATUS:%{http_code}\n" \
       "$url" > "${raw_file}.tmp" 2>/dev/null; then
      status_line="$(tail -n1 "${raw_file}.tmp")"
      status_code="$(echo "$status_line" | sed 's/HTTPSTATUS://')"
      head -n -1 "${raw_file}.tmp" > "$raw_file"
      rm -f "${raw_file}.tmp"
      title="$(grep -oiE '<title[^>]*>[^<]*</title>' "$raw_file" 2>/dev/null \
             | head -n1 | sed -e 's/<[^>]*>//g' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
             | tr -cd '[:print:][:space:]' | tr '\n\r\t' ' ' | cut -c1-150)"
      break
    else
      if [[ $attempt -eq $max_attempts ]]; then
        status_code="$(curl -s -o /dev/null -w "%{http_code}" \
          --connect-timeout "$CONNECT_TIMEOUT" --max-time "$MAX_TIME" \
          -A "$USER_AGENT" -I "$url" 2>/dev/null || echo 000)"
        echo "<!-- fetch failed after $MAX_RETRIES retries -->" > "$raw_file"
        status_line="HTTP/1.1 $status_code Connection Failed"
      else
        sleep $((RETRY_DELAY * attempt))
      fi
    fi
  done

  cat > "$meta_file" <<EOF
agent=$agent
url=$url
status_line=$status_line
status_code=$status_code
title=$title
EOF
  rm -f "${raw_file}.tmp" 2>/dev/null || true
  echo "[$agent] $status_code $url"
}
export -f fetch_url
export OUT_RAW OUT_META CONNECT_TIMEOUT MAX_TIME USER_AGENT MAX_RETRIES RETRY_DELAY

# --- dry run ---
if [[ $DRY_RUN -eq 1 ]]; then
  log "DRY RUN:"
  tail -n +2 "$TARGETS_CSV" | while IFS=, read -r a u; do echo "  [$a] $u"; done
  exit 0
fi

# --- parallel fetch (no console spam when QUIET=1) ---
log "Fetching $total_targets URLs with $MAX_WORKERS workers..."
tail -n +2 "$TARGETS_CSV" \
| xargs -P"$MAX_WORKERS" -I{} bash -c '
  agent=$(echo "{}" | cut -d, -f1)
  url=$(echo "{}" | cut -d, -f2-)
  fetch_url "$agent" "$url"
'

# --- summary (race-safe) ---
log "Generating summary..."
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
} > "$SUMMARY_CSV"

success_count="$(awk -F, 'NR>1 && $3 ~ /^[12][0-9][0-9]$/ {c++} END{print c+0}' "$SUMMARY_CSV")"
total_processed="$(tail -n +2 "$SUMMARY_CSV" | wc -l | tr -d ' ')"
log "Complete: processed=$total_processed success=$success_count"
log "  Raw:     $OUT_RAW/"
log "  Meta:    $OUT_META/"
log "  Summary: $SUMMARY_CSV"
[[ $success_count -gt 0 ]] || exit 1
