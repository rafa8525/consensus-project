#!/usr/bin/env bash
set -euo pipefail
REPO="$HOME/consensus-project"
cd "$REPO"
git fetch --quiet origin v1.1-dev
git show origin/v1.1-dev:agents/run_acs_cycle.py > agents/run_acs_cycle.py
chmod +x agents/run_acs_cycle.py
status=0
for agent in ACS-02 ACS-03 ACS-04 ACS-05; do
  python3 agents/run_acs_cycle.py "$agent" || status=$?
done
exit "$status"
