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

set +e
SYNC_OUTPUT="$(python3 "$TMP_SYNC")"
SYNC_RC=$?
set -e

echo "ACS-01 branch sync rc=$SYNC_RC"
echo "$SYNC_OUTPUT"

# Always run the supervisor so a blocked/failed synchronization is recorded in
# authoritative ACS-01 state instead of turning into a silent scheduler exit.
PYTHONPATH="$REPO" python3 -m agents.supervisor
