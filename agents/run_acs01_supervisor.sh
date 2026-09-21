#!/usr/bin/env bash
set -euo pipefail

# Durable ACS-01 launcher for the live PythonAnywhere v1.1-dev runtime.
# It never merges/rebases branches. It refreshes only the two ACS-01 runtime
# files from origin/v1.1-dev, then executes the Supervisor in place.

REPO="$HOME/consensus-project"
cd "$REPO"

git fetch --quiet origin v1.1-dev
git show origin/v1.1-dev:agents/core/agent_base.py > agents/core/agent_base.py
git show origin/v1.1-dev:agents/supervisor.py > agents/supervisor.py
git show origin/v1.1-dev:agents/self_improver.py > agents/self_improver.py

PYTHONPATH="$REPO" python3 -m agents.supervisor
