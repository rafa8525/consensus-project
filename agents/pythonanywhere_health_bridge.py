#!/usr/bin/env python3
"""
PythonAnywhere -> GitHub health bridge for Rafael's AI Consensus System.

Creates:
    logs/system/pythonanywhere_health.json

The snapshot contains operational metadata only. It does NOT copy file contents,
API tokens, environment variables, passwords, or Git credentials.

Publishing is isolated from the live PythonAnywhere branch: the script creates a
temporary worktree based on origin/main, copies only the health JSON into it,
commits that one file, and pushes that detached main-based commit to origin/main.
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

CRITICAL_PATHS = [
    REPO / "agents",
    REPO / "memory",
    REPO / "logs",
    REPO / "requirements.txt",
    REPO / "pyproject.toml",
]

def run(cmd, cwd=REPO, timeout=30):
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": p.stdout.strip()[-2000:],
            "stderr": p.stderr.strip()[-2000:],
        }
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__}

def path_meta(path: Path):
    try:
        st = path.stat()
        return {
            "path": str(path.relative_to(REPO)),
            "exists": True,
            "is_dir": path.is_dir(),
            "size": st.st_size,
            "mtime_utc": datetime.fromtimestamp(
                st.st_mtime, timezone.utc
            ).isoformat(),
        }
    except FileNotFoundError:
        return {"path": str(path.relative_to(REPO)), "exists": False}

def pythonanywhere_schedule():
    token = os.environ.get("API_TOKEN")
    username = os.environ.get("USER")
    if not token or not username:
        return {"available": False, "reason": "API_TOKEN or USER unavailable"}

    try:
        import requests

        url = f"https://www.pythonanywhere.com/api/v0/user/{username}/schedule/"
        r = requests.get(
            url,
            headers={"Authorization": f"Token {token}"},
            timeout=20,
        )
        if r.status_code != 200:
            return {"available": False, "http_status": r.status_code}

        sanitized = []
        for task in r.json():
            sanitized.append(
                {
                    "id": task.get("id"),
                    "enabled": task.get("enabled"),
                    "interval": task.get("interval"),
                    "hour": task.get("hour"),
                    "minute": task.get("minute"),
                    "description": task.get("description"),
                }
            )
        return {"available": True, "tasks": sanitized}
    except Exception as exc:
        return {"available": False, "reason": type(exc).__name__}

snapshot = {
    "schema_version": 2,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "source": "pythonanywhere",
    "active_branch": run(["git", "branch", "--show-current"])["stdout"],
    "critical_paths": [path_meta(p) for p in CRITICAL_PATHS],
    "git": {
        "status": run(["git", "status", "--short"]),
        "last_commit": run(["git", "log", "-1", "--format=%H|%cI|%s"]),
        "origin_reachable": run(["git", "ls-remote", "--exit-code", "origin", "HEAD"]),
    },
    "pythonanywhere_schedule": pythonanywhere_schedule(),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
    json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

# Publish only the health snapshot through an isolated temporary worktree.
fetch = run(["git", "fetch", "origin", "main"], timeout=60)
if not fetch.get("ok"):
    raise SystemExit("Health snapshot written locally, but fetching origin/main failed")

with tempfile.TemporaryDirectory(prefix="acs-health-") as td:
    worktree = Path(td) / "main"
    add = run(
        ["git", "worktree", "add", "--detach", str(worktree), "origin/main"],
        timeout=60,
    )
    if not add.get("ok"):
        raise SystemExit("Could not create isolated main worktree")

    try:
        target = worktree / "logs" / "system" / "pythonanywhere_health.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(OUT, target)

        add_file = run(
            ["git", "add", "-f", "--", "logs/system/pythonanywhere_health.json"],
            cwd=worktree,
        )
        if not add_file.get("ok"):
            raise SystemExit("Could not stage health snapshot")

        commit = run(
            ["git", "commit", "-m", "Update PythonAnywhere health snapshot"],
            cwd=worktree,
        )
        if not commit.get("ok"):
            raise SystemExit("Could not commit health snapshot")

        push = run(
            ["git", "push", "origin", "HEAD:main"],
            cwd=worktree,
            timeout=60,
        )
        if not push.get("ok"):
            raise SystemExit("Health snapshot committed, but GitHub push failed")
    finally:
        run(["git", "worktree", "remove", "--force", str(worktree)], timeout=30)

print("logs/system/pythonanywhere_health.json")
