#!/usr/bin/env bash
set -euo pipefail

# Durable ACS-01 launcher for the live PythonAnywhere v1.1-dev runtime.
#
# Goals:
# - keep the live branch current without rebasing or force-resetting;
# - preserve expected runtime-generated changes;
# - never overwrite genuine local source/config edits;
# - execute ACS-01, which in turn runs ACS-02 through ACS-05 and the bridge.

REPO="$HOME/consensus-project"
BRANCH="v1.1-dev"
REMOTE="origin/$BRANCH"

cd "$REPO"

git fetch --quiet origin "$BRANCH"

SYNC_RESULT="$(
python3 - <<'PY'
from pathlib import Path
import subprocess
import sys

repo = Path.home() / "consensus-project"
remote = "origin/v1.1-dev"

runtime_prefixes = (
    "memory/logs/",
    "memory/agents/",
    "memory/exports/",
)
runtime_files = {
    "memory/centralized_knowledge_base.txt",
    "memory/security_audit_schedule.txt",
}

def run(*args, check=False):
    p = subprocess.run(
        list(args),
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and p.returncode != 0:
        raise SystemExit(p.stderr.strip() or "command failed")
    return p

status = run("git", "status", "--porcelain=v1", "-uno", check=True)
meaningful = []

for raw in status.stdout.splitlines():
    if not raw:
        continue
    path = raw[3:].strip()
    if path in runtime_files or any(path.startswith(x) for x in runtime_prefixes):
        continue
    meaningful.append(path)

unsafe = []
safe_refresh = []

for path in meaningful:
    local = repo / path

    remote_blob = run("git", "show", f"{remote}:{path}")
    if remote_blob.returncode != 0:
        # If the path is absent remotely, do not touch it automatically.
        unsafe.append(path)
        continue

    remote_bytes = remote_blob.stdout.encode()

    if not local.exists():
        # Missing tracked source can be restored safely from HEAD before FF.
        safe_refresh.append(path)
        continue

    try:
        local_bytes = local.read_bytes()
    except OSError:
        unsafe.append(path)
        continue

    if local_bytes == remote_bytes:
        # File was already refreshed from origin while HEAD remained behind.
        safe_refresh.append(path)
    else:
        unsafe.append(path)

if unsafe:
    print("blocked:" + ",".join(unsafe))
    sys.exit(0)

for path in safe_refresh:
    p = run("git", "restore", "--source=HEAD", "--", path)
    if p.returncode != 0:
        print("blocked:restore_failed:" + path)
        sys.exit(0)

merge = run("git", "merge", "--ff-only", remote)
if merge.returncode != 0:
    print("blocked:ff_failed:" + merge.stderr.strip().replace("\n", " ")[:500])
    sys.exit(0)

print("synced")
PY
)"

echo "ACS-01 branch sync: $SYNC_RESULT"

# Never hide a blocked safe-sync condition. The supervisor still runs so the
# health system records the problem instead of silently skipping the cycle.
PYTHONPATH="$REPO" python3 -m agents.supervisor
