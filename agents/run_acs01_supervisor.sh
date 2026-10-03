#!/usr/bin/env bash
set -euo pipefail

# Durable ACS-01 launcher for the live PythonAnywhere v1.1-dev runtime.
#
# One canonical synchronization engine owns branch repair:
#   agents/safe_sync_live_branch.py
#
# The launcher fetches that engine directly from origin before running it, so
# branch self-healing still works even when the local checkout is behind.

REPO="$HOME/consensus-project"
BRANCH="v1.1-dev"
REMOTE="origin/$BRANCH"
TMP_SYNC="$(mktemp)"
trap 'rm -f "$TMP_SYNC"' EXIT

cd "$REPO"

git fetch --quiet origin "$BRANCH"
git show "$REMOTE:agents/safe_sync_live_branch.py" > "$TMP_SYNC"

python3 "$TMP_SYNC"

# The branch is now current, so execute the checked-in supervisor.
PYTHONPATH="$REPO" python3 -m agents.supervisor
