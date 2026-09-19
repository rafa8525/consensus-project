#!/usr/bin/env python3
"""PythonAnywhere -> GitHub operational health bridge.

Publishes logs/system/pythonanywhere_health.json to origin/main without merging
or rebasing the live PythonAnywhere branch. No secrets or file contents are
included in the snapshot.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path.home() / "consensus-project"
OUT = REPO / "logs" / "system" / "pythonanywhere_health.json"
EXPECTED_HEALTH_MARKER = "run_pythonanywhere_health_bridge.sh"
CRITICAL_PATHS = [
    REPO / "agents",
    REPO / "memory",
    REPO / "logs",
    REPO / "requirements.txt",
]

def run(cmd, cwd=REPO, timeout=30):
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True,
                           timeout=timeout, check=False)
        return {"ok": p.returncode == 0, "returncode": p.returncode,
                "stdout": p.stdout.strip()[-2000:],
                "stderr": p.stderr.strip()[-2000:]}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__}

def path_meta(path):
    try:
        st = path.stat()
        return {"path": str(path.relative_to(REPO)), "exists": True,
                "is_dir": path.is_dir(), "size": st.st_size,
                "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()}
    except FileNotFoundError:
        return {"path": str(path.relative_to(REPO)), "exists": False}

def pythonanywhere_schedule():
    token = os.environ.get("API_TOKEN")
    username = os.environ.get("USER")
    if not token or not username:
        return {"available": False, "reason": "API_TOKEN or USER unavailable",
                "health_task": {"found": False, "enabled": False}}

    try:
        import requests
        url = f"https://www.pythonanywhere.com/api/v0/user/{username}/schedule/"
        r = requests.get(url, headers={"Authorization": f"Token {token}"}, timeout=20)
        if r.status_code != 200:
            return {"available": False, "http_status": r.status_code,
                    "health_task": {"found": False, "enabled": False}}

        sanitized = []
        matches = []
        for task in r.json():
            command = str(task.get("command") or "")
            description = str(task.get("description") or "")
            is_health = EXPECTED_HEALTH_MARKER in command or "pythonanywhere health" in description.lower()
            item = {"id": task.get("id"), "enabled": task.get("enabled"),
                    "interval": task.get("interval"), "hour": task.get("hour"),
                    "minute": task.get("minute"), "description": description,
                    "is_health_task": is_health}
            sanitized.append(item)
            if is_health:
                matches.append(item)

        enabled_matches = [x for x in matches if x.get("enabled") is True]
        return {"available": True, "tasks": sanitized,
                "health_task": {"found": bool(matches),
                                "enabled": bool(enabled_matches),
                                "matching_task_ids": [x.get("id") for x in matches]}}
    except Exception as exc:
        return {"available": False, "reason": type(exc).__name__,
                "health_task": {"found": False, "enabled": False}}

git_status = run(["git", "status", "--porcelain=v1", "--untracked-files=no"])
status_text = git_status.get("stdout", "")
conflict = any(line[:2] in {"DD","AU","UD","UA","DU","AA","UU"} for line in status_text.splitlines())

snapshot = {
    "schema_version": 3,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "source": "pythonanywhere",
    "active_branch": run(["git", "branch", "--show-current"]).get("stdout", ""),
    "critical_paths": [path_meta(p) for p in CRITICAL_PATHS],
    "git": {
        "status": git_status,
        "unresolved_merge_conflict": conflict,
        "last_commit": run(["git", "log", "-1", "--format=%H|%cI|%s"]),
        "origin_reachable": run(["git", "ls-remote", "--exit-code", "origin", "HEAD"]),
    },
    "pythonanywhere_schedule": pythonanywhere_schedule(),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")

fetch = run(["git", "fetch", "origin", "main"], timeout=60)
if not fetch.get("ok"):
    raise SystemExit("Health snapshot written locally, but fetching origin/main failed")

with tempfile.TemporaryDirectory(prefix="acs-health-") as td:
    worktree = Path(td) / "main"
    add = run(["git", "worktree", "add", "--detach", str(worktree), "origin/main"], timeout=60)
    if not add.get("ok"):
        raise SystemExit("Could not create isolated main worktree")
    try:
        target = worktree / "logs" / "system" / "pythonanywhere_health.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(OUT, target)
        if not run(["git", "add", "-f", "--", "logs/system/pythonanywhere_health.json"], cwd=worktree).get("ok"):
            raise SystemExit("Could not stage health snapshot")
        diff = run(["git", "diff", "--cached", "--quiet"], cwd=worktree)
        if diff.get("returncode") == 0:
            print("Health snapshot unchanged")
        else:
            if not run(["git", "commit", "-m", "Update PythonAnywhere health snapshot"], cwd=worktree).get("ok"):
                raise SystemExit("Could not commit health snapshot")
            if not run(["git", "push", "origin", "HEAD:main"], cwd=worktree, timeout=60).get("ok"):
                raise SystemExit("Health snapshot committed, but GitHub push failed")
    finally:
        run(["git", "worktree", "remove", "--force", str(worktree)], timeout=30)

print("logs/system/pythonanywhere_health.json")
