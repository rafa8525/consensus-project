#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
STAMP="logs/scheduler/pm_once_$(date +%F).stamp"
mkdir -p logs/scheduler
if [ -f "$STAMP" ]; then
  echo "[follow-on] already ran PM today"; exit 0
fi
: > "$STAMP"
WINDOW=pm CONSENSUS_REGISTRY=CONSENSUS_REGISTRY.v2a.yaml /usr/bin/python3 tools/consensus_dispatcher.py >/dev/null 2>&1 || true
