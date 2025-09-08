#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

TIME_OF_DAY="${1:-16:00}"                     # e.g. "16:00"
TZ_NAME="${2:-America/Los_Angeles}"           # e.g. "America/Los_Angeles"
CMD="${3:-bash tools/absorb_memory.sh}"       # command to run at that local time

SLOG="logs/scheduler/schedule_absorb.log"
mkdir -p "$(dirname "$SLOG")"

now_utc="$(date -u +%s)"

# Build a local-time timestamp for today at TIME_OF_DAY in TZ_NAME, then convert to epoch
local_target_today="$(TZ="$TZ_NAME" date -d "today $TIME_OF_DAY" +"%Y-%m-%d %H:%M:%S %z")"
target_utc="$(date -d "$local_target_today" +%s 2>/dev/null || echo 0)"

# If today’s time already passed, schedule for tomorrow
if [ "$target_utc" -le "$now_utc" ]; then
  local_target_today="$(TZ="$TZ_NAME" date -d "tomorrow $TIME_OF_DAY" +"%Y-%m-%d %H:%M:%S %z")"
  target_utc="$(date -d "$local_target_today" +%s)"
fi

delta="$((target_utc - now_utc))"
if [ "$delta" -le 0 ]; then
  echo "[$(date -Is)] schedule_absorb: computed non-positive delay; aborting." >> "$SLOG"
  exit 1
fi

# Lock so we don't schedule duplicates for the same day/time
LOCK="/tmp/schedule_absorb_${TIME_OF_DAY//[: ]/_}.lock"
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "[$(date -Is)] schedule_absorb: another schedule in progress; exiting." >> "$SLOG"
  exit 0
fi

# Log plan and fire off a quiet background job
echo "[$(date -Is)] will run '$CMD' at $local_target_today (in ${delta}s)" >> "$SLOG"
nohup bash -lc "sleep $delta; $CMD >> logs/absorb/absorb.log 2>&1" >/dev/null 2>&1 &
pid=$!
echo "[$(date -Is)] scheduled pid=$pid" >> "$SLOG"
echo "scheduled: $local_target_today (pid=$pid)"
