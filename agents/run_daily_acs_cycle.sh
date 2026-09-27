#!/usr/bin/env bash
set -euo pipefail

# Durable daily ACS runtime cycle.
# Each component must create its own runtime evidence; this script never
# fabricates timestamps or edits state files to make health appear green.

REPO="$HOME/consensus-project"
cd "$REPO"

git fetch --quiet origin v1.1-dev
for f in   agents/core/agent_base.py   agents/core/store.py   agents/supervisor.py   agents/researcher.py   agents/self_improver.py   agents/evaluator.py   agents/infrastructure_guardian.py   agents/continuity_guardian_agent.py
do
  mkdir -p "$(dirname "$f")"
  git show "origin/v1.1-dev:$f" > "$f"
done

export PYTHONPATH="$REPO"

# ACS-01 Orchestrator: supervisor writes memory/agents/state.json:last_supervisor_ts.
python3 -m agents.supervisor

# ACS-04 Infrastructure: its own structured status is execution evidence.
python3 agents/infrastructure_guardian.py --apply || rc=$?
if [[ ${rc:-0} -ge 2 ]]; then
  echo "ACS-04 infrastructure cycle critical (exit ${rc})" >&2
fi
unset rc

# ACS-05 Continuity: its own state/log is execution evidence.
python3 agents/continuity_guardian_agent.py --force || rc=$?
if [[ ${rc:-0} -ge 2 ]]; then
  echo "ACS-05 continuity cycle critical (exit ${rc})" >&2
fi

# Do not manufacture ACS-02/ACS-03 evidence here. Their independent scheduled
# jobs remain authoritative and the health bridge will flag them if stale.
bash agents/run_pythonanywhere_health_bridge.sh
