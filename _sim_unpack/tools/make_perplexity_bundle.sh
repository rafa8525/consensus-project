#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
bash tools/error_watcher.sh >/dev/null 2>&1 || true
if [ ! -s logs/reports/errors_to_route.txt ]; then
  echo "[perplexity] no errors today — skipping bundle"
  exit 0
fi
ts="$(date -Is)"; out="logs/reports/perplexity_prompt_${ts}.txt"
{
  echo "Context for Consensus Project (branch v1.1-dev) — NEED TARGETED ADVICE"
  echo
  echo "1) Current registry (CONSENSUS_REGISTRY.v2a.yaml):"
  sed -n '1,200p' CONSENSUS_REGISTRY.v2a.yaml
  echo
  echo "2) Latest dispatcher results (AM & PM):"
  if [ "${CONSENSUS_DEPTH:-0}" = "0" ]; then
    timeout 45s bash -lc 'WINDOW=am CONSENSUS_REGISTRY=CONSENSUS_REGISTRY.v2a.yaml /usr/bin/python3 tools/consensus_dispatcher.py' || echo "[bundle] AM dispatcher timed out"
    timeout 45s bash -lc 'WINDOW=pm CONSENSUS_REGISTRY=CONSENSUS_REGISTRY.v2a.yaml /usr/bin/python3 tools/consensus_dispatcher.py' || echo "[bundle] PM dispatcher timed out"
  else
    echo "[bundle] Skipping nested dispatcher (depth=${CONSENSUS_DEPTH})"
  fi
  echo
  echo "3) Today’s heartbeats:"
  tail -n 30 logs/scheduler/$(date +%F)_heartbeat_status.log 2>/dev/null || true
  echo
  echo "4) Fresh errors (today):"
  sed -n '1,200p' logs/reports/errors_to_route.txt
  echo
  echo "5) LFS state:"
  git lfs ls-files || true
  echo
  echo "ASK: Pinpoint remediation for any nonzero RCs or recurring errors; suggest minimal changes only."
} > "$out"
echo "[perplexity] wrote $out"
