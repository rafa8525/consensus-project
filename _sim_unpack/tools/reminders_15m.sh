#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

LOCK="memory/logs/sanity/reminders_15m.lock"
mkdir -p "$(dirname "$LOCK")"; exec 9>"$LOCK"
if command -v flock >/dev/null 2>&1; then
  flock -n 9 || { echo "reminders runner busy"; exit 0; }
fi

python3 tools/reminder_runner.py || true
./tools/absorb_and_sync.sh
