#!/usr/bin/env bash
set -euo pipefail

# --- config ---
readonly SCRIPT_NAME="$(basename "$0")"
readonly MAX_WORKERS="${MAX_WORKERS:-6}"
readonly CONNECT_TIMEOUT="${CONNECT_TIMEOUT:-5}"
readonly MAX_TIME="${MAX_TIME:-15}"
readonly MAX_RETRIES="${MAX_RETRIES:-2}"
readonly RETRY_DELAY="${RETRY_DELAY:-2}"
readonly USER_AGENT="ConsensusHarvester/1.0"
readonly DRY_RUN="${DRY_RUN:-0}"

# --- helpers ---
log() { echo "[$SCRIPT_NAME] $*" >&2; }
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
# --- extract agent,url pairs ---
{
  echo "agent,url"
  tail -n +2 "$CSV" | sed 's/\r$//' | while IFS=, read -r agent rest; do
    agent="$(echo "$agent" | sed 's/^[[:space:]"]*//; s/[[:space:]"]*$//')"
    url="$(echo "$rest" | grep -oE 'https?://[^[:space:],"\047]+' | head -n1 | sed 's/["\047]*$//')"
    [[ -n "$agent" && -n "$url" ]] && printf '%s,%s\n' "$agent" "$url"
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
       -A "$USER_AGENT" \
       --write-out "HTTPSTATUS:%{http_code}\n" \
       "$url" > "${raw_file}.tmp" 2>/dev/null; then
      status_line="$(tail -n1 "${raw_file}.tmp")"
      status_code="$(echo "$status_line" | sed 's/HTTPSTATUS://')"
      head -n -1 "${raw_file}.tmp" > "$raw_file"
      rm -f "${raw_file}.tmp"
      title="$(grep -oiE '<title[^>]*>[^<]*</title>' "$raw_file" 2>/dev/null \
             | head -n1 | sed -e 's/<[^>]*>//g' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
             | tr -d '\n\r' | cut -c1-200)"
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
# --- parallel fetch ---
log "Fetching $total_targets URLs with $MAX_WORKERS workers..."
tail -n +2 "$TARGETS_CSV" \
| xargs -n1 -P"$MAX_WORKERS" -I{} bash -c '
  agent=$(echo "{}" | cut -d, -f1)
  url=$(echo "{}" | cut -d, -f2-)
  fetch_url "$agent" "$url"
'
# --- summary ---
log "Generating summary..."
{
  echo "agent,url,status_code,title"
  for m in "$OUT_META"/*.meta; do
    [[ -s "$m" ]] || continue
    unset agent url status_line status_code title
    # shellcheck disable=SC1090
    source "$m" 2>/dev/null || continue
    title_escaped="$(echo "${title:-}" | sed 's/"/"""/g')"
    printf '%s,%s,%s,"%s"\n' "${agent:-unknown}" "${url:-unknown}" "${status_code:-000}" "$title_escaped"
  done
} > "$SUMMARY_CSV"

success_count="$(awk -F, 'NR>1 && $3 ~ /^[12][0-9][0-9]$/ {c++} END{print c+0}' "$SUMMARY_CSV")"
total_processed="$(tail -n +2 "$SUMMARY_CSV" | wc -l | tr -d ' ')"

log "Complete: processed=$total_processed success=$success_count"
log "  Raw:     $OUT_RAW/"
log "  Meta:    $OUT_META/"
log "  Summary: $SUMMARY_CSV"
[[ $success_count -gt 0 ]] || exit 1
