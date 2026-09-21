#!/usr/bin/env python3
"""PythonAnywhere -> GitHub operational health bridge.

Publishes logs/system/pythonanywhere_health.json to origin/main without merging
or rebasing the live PythonAnywhere branch. No secrets or file contents are
included in the snapshot.

Source-of-truth rules:
- runtime execution evidence comes from PythonAnywhere runtime state;
- GitHub commit activity is repository evidence, not agent-execution evidence;
- legacy heartbeat/knowledge-validation logs are not authoritative.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path.home() / "consensus-project"
OUT = REPO / "logs" / "system" / "pythonanywhere_health.json"
EXPECTED_HEALTH_MARKER = "run_pythonanywhere_health_bridge.sh"
ACS01_STATE = REPO / "memory" / "agents" / "state.json"
ACS01_MAX_AGE_SECONDS = 36 * 60 * 60
ACS_STATE_FILES = {
    "ACS-02": REPO / "memory" / "agents" / "acs02_state.json",
    "ACS-03": REPO / "memory" / "agents" / "acs03_state.json",
    "ACS-04": REPO / "memory" / "agents" / "acs04_state.json",
    "ACS-05": REPO / "memory" / "agents" / "acs05_state.json",
}
ACS_DEFINITIONS = {
    "ACS-02": {
        "role": "Knowledge Cycle",
        "paths": [
            REPO / "memory" / "public" / "absorption_last_success.json",
            Path.home() / "memory" / "public" / "absorption_last_success.json",
        ],
        "json_ts": "last_success_utc",
        "json_status": "status",
        "max_age": 36 * 60 * 60,
    },
    "ACS-03": {
        "role": "Health Cycle",
        "paths": [
            REPO / "memory" / "logs" / "system" / "fitness_integration.log",
            Path.home() / "memory" / "logs" / "system" / "fitness_integration.log",
        ],
        "max_age": 36 * 60 * 60,
        "success_markers": ["PASS", "Fitness logs are current"],
        "failure_markers": ["ATTENTION REQUIRED", "ERROR", "FAIL"],
    },
    "ACS-04": {
        "role": "Infrastructure Cycle",
        "paths": [
            REPO / "memory" / "logs" / "system" / "infrastructure_guardian_status.json",
            Path.home() / "memory" / "logs" / "system" / "infrastructure_guardian_status.json",
            REPO / "memory" / "logs" / "status" / "system_health_snapshot.md",
            Path.home() / "memory" / "logs" / "status" / "system_health_snapshot.md",
        ],
        "max_age": 36 * 60 * 60,
        "success_markers": ['"status": "healthy"', '"status": "ok"', "- Overall: ok"],
        "failure_markers": ['"status": "critical"', '"status": "degraded"', "- Overall: warn"],
    },
    "ACS-05": {
        "role": "Continuity Cycle",
        "paths": [
            REPO / "memory" / "logs" / "system" / "continuity_guardian_state.json",
            Path.home() / "memory" / "logs" / "system" / "continuity_guardian_state.json",
            REPO / "memory" / "logs" / "system" / "continuity_guardian.log",
            Path.home() / "memory" / "logs" / "system" / "continuity_guardian.log",
        ],
        "max_age": 36 * 60 * 60,
        "success_markers": ['"status": "ok"', '"critical": []', "CRITICAL=0", "critical=0"],
        "failure_markers": ['"status": "critical"', "CRITICAL=", "critical="],
    },
}
CRITICAL_PATHS = [
    REPO / "agents",
    REPO / "memory",
    REPO / "logs",
    REPO / "requirements.txt",
]
KNOWLEDGE_PATHS = [
    REPO / "memory",
    REPO / "memory" / "agents",
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

def acs01_execution_evidence():
    """Read Supervisor/ACS-01 runtime evidence without inventing a run."""
    base = {
        "agent": "ACS-01",
        "runtime_component": "agents.supervisor.Supervisor",
        "cadence": "daily",
        "evidence_source": "memory/agents/state.json:last_supervisor_ts",
        "verified": False,
        "status": "missing",
    }
    try:
        raw = json.loads(ACS01_STATE.read_text(encoding="utf-8"))
        ts = raw.get("last_supervisor_ts")
        if not isinstance(ts, (int, float)) or ts <= 0:
            return base
        age = max(0.0, time.time() - float(ts))
        base.update({
            "last_execution_utc": datetime.fromtimestamp(float(ts), timezone.utc).isoformat(),
            "age_seconds": round(age, 1),
            "verified": True,
            "status": "current" if age <= ACS01_MAX_AGE_SECONDS else "stale",
            "stale_after_seconds": ACS01_MAX_AGE_SECONDS,
        })
        return base
    except FileNotFoundError:
        return base
    except Exception as exc:
        base["status"] = "unreadable"
        base["error_type"] = type(exc).__name__
        return base


def _first_existing(paths):
    for path in paths:
        if path.exists():
            return path
    return None

def _iso_from_value(value):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None

def acs_execution_evidence(agent, spec):
    """Verify ACS-02..05 from the component's own runtime artifact."""
    base = {
        "agent": agent, "role": spec["role"], "verified": False,
        "status": "missing", "stale_after_seconds": spec["max_age"],
    }
    path = _first_existing(spec["paths"])
    if path is None:
        base["evidence_candidates"] = [str(p) for p in spec["paths"]]
        return base
    try:
        st = path.stat()
        evidence_time = datetime.fromtimestamp(st.st_mtime, timezone.utc)
        text = path.read_text(encoding="utf-8", errors="replace")
        data = None
        if path.suffix == ".json":
            data = json.loads(text)
            ts_key = spec.get("json_ts")
            if ts_key:
                parsed = _iso_from_value(data.get(ts_key))
                if parsed is not None:
                    evidence_time = parsed.astimezone(timezone.utc)
        age = max(0.0, time.time() - evidence_time.timestamp())
        status_ok = None
        if data is not None and spec.get("json_status"):
            status_ok = str(data.get(spec["json_status"], "")).lower() in {"ok", "healthy", "pass", "passed"}
        if status_ok is None:
            tail = text[-12000:]
            success_positions = [tail.rfind(m) for m in spec.get("success_markers", [])]
            failure_positions = [tail.rfind(m) for m in spec.get("failure_markers", [])]
            latest_success = max(success_positions, default=-1)
            latest_failure = max(failure_positions, default=-1)
            if latest_success >= 0 or latest_failure >= 0:
                status_ok = latest_success > latest_failure
        base.update({
            "evidence_source": str(path),
            "last_execution_utc": evidence_time.isoformat(),
            "age_seconds": round(age, 1),
            "verified": status_ok is not None,
            "status": ("stale" if age > spec["max_age"] else ("current" if status_ok else "degraded"))
                      if status_ok is not None else ("stale" if age > spec["max_age"] else "unverified"),
        })
        return base
    except Exception as exc:
        base["evidence_source"] = str(path)
        base["status"] = "unreadable"
        base["error_type"] = type(exc).__name__
        return base

def all_acs_evidence():
    result = {"ACS-01": acs01_execution_evidence()}
    for agent, spec in ACS_DEFINITIONS.items():
        result[agent] = acs_execution_evidence(agent, spec)
    return result

def knowledge_validation():
    """Validate current knowledge roots and explicitly retire obsolete checks."""
    current = [path_meta(p) for p in KNOWLEDGE_PATHS]
    ok = all(item.get("exists") for item in current)
    return {
        "status": "ok" if ok else "attention",
        "authoritative_runtime_roots": current,
        "legacy_checks": {
            "heartbeat.log": "deprecated; not execution evidence",
            "knowledge_sharing_validation.log": "deprecated; historical only",
            "centralized_knowledge_base.txt": "deprecated; absence is not a failure",
            "AI Consensus System Project.txt": "deprecated; absence is not a failure",
        },
        "source_of_truth": {
            "agent_execution": "runtime state written by the executing agent",
            "infrastructure_health": "logs/system/pythonanywhere_health.json",
            "repository_activity": "Git history; never substitute for agent execution",
        },
    }

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
        acs01_matches = []
        for task in r.json():
            command = str(task.get("command") or "")
            description = str(task.get("description") or "")
            is_health = EXPECTED_HEALTH_MARKER in command or "pythonanywhere health" in description.lower()
            is_acs01 = (
                "agents.supervisor" in command
                or "agents/supervisor.py" in command
                or "supervisor.py" in command
                or "run_acs01_supervisor.sh" in command
                or "acs-01" in description.lower()
            )
            item = {"id": task.get("id"), "enabled": task.get("enabled"),
                    "interval": task.get("interval"), "hour": task.get("hour"),
                    "minute": task.get("minute"), "description": description,
                    "is_health_task": is_health, "is_acs01_task": is_acs01}
            sanitized.append(item)
            if is_health:
                matches.append(item)
            if is_acs01:
                acs01_matches.append(item)

        enabled_matches = [x for x in matches if x.get("enabled") is True]
        enabled_acs01 = [x for x in acs01_matches if x.get("enabled") is True]
        return {"available": True, "tasks": sanitized,
                "health_task": {"found": bool(matches),
                                "enabled": bool(enabled_matches),
                                "matching_task_ids": [x.get("id") for x in matches]},
                "acs01_task": {"found": bool(acs01_matches),
                               "enabled": bool(enabled_acs01),
                               "matching_task_ids": [x.get("id") for x in acs01_matches]}}
    except Exception as exc:
        return {"available": False, "reason": type(exc).__name__,
                "health_task": {"found": False, "enabled": False},
                "acs01_task": {"found": False, "enabled": False}}

git_status = run(["git", "status", "--porcelain=v1", "--untracked-files=no"])
status_text = git_status.get("stdout", "")
conflict = any(line[:2] in {"DD","AU","UD","UA","DU","AA","UU"} for line in status_text.splitlines())

snapshot = {
    "schema_version": 5,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "source": "pythonanywhere",
    "active_branch": run(["git", "branch", "--show-current"]).get("stdout", ""),
    "critical_paths": [path_meta(p) for p in CRITICAL_PATHS],
    "acs01_orchestrator": acs01_execution_evidence(),
    "agents": all_acs_evidence(),
    "knowledge_validation": knowledge_validation(),
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
