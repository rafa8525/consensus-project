#!/usr/bin/env bash
set -euo pipefail

# ACS-01 launcher: a failed branch sync MUST cause a failed scheduler exit.
# Still run the supervisor after a sync failure to record child diagnostics.
REPO="${CONSENSUS_REPO_ROOT:-$HOME/consensus-project}"
BRANCH="v1.1-dev"
REMOTE="origin/$BRANCH"
TMP_SYNC="$(mktemp)"
trap 'rm -f "$TMP_SYNC"' EXIT

cd "$REPO"

SYNC_RC=0
if ! git fetch --quiet origin "$BRANCH"; then
    echo "ACS-01 branch sync: git fetch failed" >&2
    SYNC_RC=3
elif ! git show "$REMOTE:agents/safe_sync_live_branch.py" > "$TMP_SYNC"; then
    echo "ACS-01 branch sync: cannot load remote sync engine" >&2
    SYNC_RC=3
else
    set +e
    python3 "$TMP_SYNC"
    SYNC_RC=$?
    set -e
fi

echo "ACS-01 branch sync rc=$SYNC_RC"

set +e
PYTHONPATH="$REPO" python3 -m agents.supervisor
SUPERVISOR_RC=$?
set -e
echo "ACS-01 supervisor rc=$SUPERVISOR_RC"

# Sync failure is never masked by a healthy-looking supervisor run.
if (( SYNC_RC != 0 )); then
    exit "$SYNC_RC"
fi
exit "$SUPERVISOR_RC"
