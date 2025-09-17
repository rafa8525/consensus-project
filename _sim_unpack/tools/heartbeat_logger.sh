#!/usr/bin/env bash
set -euo pipefail
ts="$(date -Is)"
mkdir -p logs/scheduler
echo "[$ts] heartbeat ok" >> logs/scheduler/$(date +%F)_heartbeat_status.log
