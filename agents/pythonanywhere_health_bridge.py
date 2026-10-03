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
import sys
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
        "success_markers": ['"overall_status": "healthy"', '"status": "healthy"', '"status": "ok"', "- Overall: ok"],
        "failure_markers": ['"overall_status": "critical"', '"overall_status": "execution_failure"', '"status": "critical"', '"status": "degraded"', "- Overall: warn"],
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
        "success_markers": ['"last_status": "OK"', '"critical": []', "CRITICAL=0", "critical=0"],
        "failure_markers": ['"last_status": "CRITICAL"', '"last_status": "WARN"', "CRITICAL=", "critical="],
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

def safe_sync_v11_dev():
    """Safely fast-forward the live v1.1-dev checkout without discarding source edits."""
    runtime_prefixes = (
        "memory/logs/",
        "memory/agents/",
        "memory/exports/",
    )
    runtime_files = {
        "memory/centralized_knowledge_base.txt",
        "memory/security_audit_schedule.txt",
    }

    fetch = run(["git", "fetch", "--quiet", "origin", "v1.1-dev"], timeout=180)
    if not fetch.get("ok"):
        return {"ok": False, "status": "fetch_failed", "details": fetch}

    status = run(["git", "status", "--porcelain=v1", "--untracked-files=no"], timeout=120)
    if not status.get("ok"):
        return {"ok": False, "status": "status_failed", "details": status}

    meaningful = []
    for raw in status.get("stdout", "").splitlines():
        if not raw:
            continue
        path = raw[3:].strip()
        if path in runtime_files or any(path.startswith(x) for x in runtime_prefixes):
            continue
        meaningful.append(path)

    safe_refresh = []
    unsafe = []

    for path in meaningful:
        local = REPO / path

        remote_sha = run(
            ["git", "rev-parse", "--verify", f"origin/v1.1-dev:{path}"],
            timeout=60,
        )
        if not remote_sha.get("ok"):
            unsafe.append(path)
            continue

        if not local.exists():
            safe_refresh.append(path)
            continue

        local_sha = run(["git", "hash-object", "--", path], timeout=60)
        if not local_sha.get("ok"):
            unsafe.append(path)
            continue

        if local_sha.get("stdout", "").strip() == remote_sha.get("stdout", "").strip():
            safe_refresh.append(path)
        else:
            unsafe.append(path)

    if unsafe:
        return {
            "ok": False,
            "status": "blocked_local_source_changes",
            "unsafe_paths": unsafe[:20],
        }

    for path in safe_refresh:
        restored = run(["git", "restore", "--source=HEAD", "--", path], timeout=60)
        if not restored.get("ok"):
            return {
                "ok": False,
                "status": "restore_failed",
                "path": path,
                "details": restored,
            }

    merged = run(["git", "merge", "--ff-only", "origin/v1.1-dev"], timeout=300)
    if not merged.get("ok"):
        return {"ok": False, "status": "fast_forward_failed", "details": merged}

    head = run(["git", "rev-parse", "--short", "HEAD"])
    return {
        "ok": True,
        "status": "synced",
        "head": head.get("stdout", ""),
        "refreshed_paths": safe_refresh,
    }


def heal_infrastructure_after_sync(sync_result):
    """Refresh ACS-04/05 immediately after a successful branch self-heal."""
    if not sync_result.get("ok"):
        return {"attempted": False, "reason": sync_result.get("status")}

    outcomes = {}
    for agent in ("ACS-04", "ACS-05"):
        attempts = []
        for attempt in (1, 2):
            result = run(
                [sys.executable, str(REPO / "agents" / "run_acs_cycle.py"), agent],
                timeout=1200,
            )
            attempts.append(result)
            if result.get("ok"):
                break
            if attempt == 1:
                time.sleep(5)
        outcomes[agent] = attempts

    return {"attempted": True, "outcomes": outcomes}


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
        supervisor_health = str(raw.get("last_supervisor_status", "")).lower()

        if age > ACS01_MAX_AGE_SECONDS:
            bridge_status = "stale"
        elif supervisor_health == "ok":
            bridge_status = "current"
        elif supervisor_health:
            bridge_status = "degraded"
        else:
            bridge_status = "unverified"

        base.update({
            "last_execution_utc": datetime.fromtimestamp(float(ts), timezone.utc).isoformat(),
            "age_seconds": round(age, 1),
            "verified": supervisor_health in {"ok", "degraded"},
            "status": bridge_status,
            "health_status": supervisor_health or None,
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

def agent_diagnostics(agent):
    """Return compact non-secret diagnostics for unhealthy ACS states."""
    try:
        if agent == "ACS-04":
            candidates = [
                Path.home() / "memory" / "logs" / "system" / "infrastructure_guardian_status.json",
                REPO / "memory" / "logs" / "system" / "infrastructure_guardian_status.json",
            ]
            path = _first_existing(candidates)
            if path is None:
                return {"diagnostics_status": "missing"}
            data = json.loads(path.read_text(encoding="utf-8"))
            findings = []
            for item in data.get("findings", []):
                if item.get("severity") in {"warning", "critical"}:
                    findings.append({
                        "severity": item.get("severity"),
                        "code": item.get("code"),
                        "message": item.get("message"),
                        "repaired": item.get("repaired"),
                        "repair_message": item.get("repair_message"),
                    })
            return {
                "diagnostics_source": str(path),
                "overall_status": data.get("overall_status"),
                "findings": findings[:10],
            }

        if agent == "ACS-05":
            candidates = [
                REPO / "memory" / "logs" / "system" / "continuity_guardian_state.json",
                Path.home() / "memory" / "logs" / "system" / "continuity_guardian_state.json",
            ]
            path = _first_existing(candidates)
            if path is None:
                return {"diagnostics_status": "missing"}
            data = json.loads(path.read_text(encoding="utf-8"))
            return {
                "diagnostics_source": str(path),
                "last_status": data.get("last_status"),
                "critical": list(data.get("critical") or [])[:10],
                "warnings": list(data.get("warnings") or [])[:10],
            }
    except Exception as exc:
        return {
            "diagnostics_status": "unreadable",
            "diagnostics_error_type": type(exc).__name__,
        }

    return {}


def acs_execution_evidence(agent, spec):
    """Verify ACS-02..05 from authoritative ACS state, with legacy fallback."""
    base = {
        "agent": agent, "role": spec["role"], "verified": False,
        "status": "missing", "stale_after_seconds": spec["max_age"],
    }

    # The ACS execution harness is the authoritative health contract.
    # Component artifacts remain fallback evidence only.
    state_path = ACS_STATE_FILES.get(agent)
    if state_path is not None and state_path.exists():
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
            health = str(data.get("status", "")).lower()
            finished = _iso_from_value(data.get("finished_at_utc"))

            if finished is None:
                finished = datetime.fromtimestamp(
                    state_path.stat().st_mtime,
                    timezone.utc,
                )

            age = max(0.0, time.time() - finished.timestamp())

            status_map = {
                "healthy": "current",
                "warning": "degraded",
                "critical": "degraded",
                "execution_failure": "degraded",
            }

            bridge_status = status_map.get(health, "unverified")

            if age > spec["max_age"]:
                bridge_status = "stale"

            base.update({
                "evidence_source": str(state_path),
                "last_execution_utc": finished.astimezone(timezone.utc).isoformat(),
                "age_seconds": round(age, 1),
                "verified": bool(data.get("verified")) and health in status_map,
                "status": bridge_status,
                "health_status": health,
                "stale_after_seconds": spec["max_age"],
            })
            if bridge_status != "current" or health != "healthy":
                base["diagnostics"] = agent_diagnostics(agent)
            return base
        except Exception as exc:
            base.update({
                "evidence_source": str(state_path),
                "status": "unreadable",
                "error_type": type(exc).__name__,
            })
            return base
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

self_heal_sync = safe_sync_v11_dev()
self_heal_cycles = heal_infrastructure_after_sync(self_heal_sync)

git_status = run(["git", "status", "--porcelain=v1", "--untracked-files=no"])
status_text = git_status.get("stdout", "")
conflict = any(line[:2] in {"DD","AU","UD","UA","DU","AA","UU"} for line in status_text.splitlines())

snapshot = {
    "schema_version": 6,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "source": "pythonanywhere",
    "self_heal": {
        "branch_sync": self_heal_sync,
        "post_sync_cycles": self_heal_cycles,
    },
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
