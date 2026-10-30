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
    """Run the canonical safe-sync engine from origin/v1.1-dev."""
    try:
        fetch = subprocess.run(
            ["git", "fetch", "--quiet", "origin", "v1.1-dev"],
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
        )
        if fetch.returncode != 0:
            return {
                "ok": False,
                "status": "fetch_failed",
                "stderr": fetch.stderr[-1200:],
            }

        script = subprocess.run(
            ["git", "show", "origin/v1.1-dev:agents/safe_sync_live_branch.py"],
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        if script.returncode != 0:
            return {
                "ok": False,
                "status": "sync_engine_unavailable",
                "stderr": script.stderr[-1200:],
            }

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                prefix="acs-safe-sync-",
                delete=False,
                encoding="utf-8",
            ) as handle:
                handle.write(script.stdout)
                temp_path = Path(handle.name)

            proc = subprocess.run(
                [sys.executable, str(temp_path)],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=600,
                check=False,
            )

            payload = None
            for line in reversed(proc.stdout.splitlines()):
                try:
                    candidate = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(candidate, dict) and "status" in candidate:
                    payload = candidate
                    break

            if payload is None:
                return {
                    "ok": False,
                    "status": "sync_engine_unreadable_output",
                    "returncode": proc.returncode,
                    "stdout_tail": proc.stdout[-2000:],
                    "stderr": proc.stderr[-1200:],
                }

            payload["returncode"] = proc.returncode
            return payload
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    except Exception as exc:
        return {
            "ok": False,
            "status": "sync_engine_execution_failure",
            "error_type": type(exc).__name__,
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
        if agent == "ACS-03":
            state = ACS_STATE_FILES["ACS-03"]
            if not state.is_file():
                return {"diagnostics_status": "missing"}
            payload = json.loads(state.read_text(encoding="utf-8"))
            return {
                "diagnostics_status": "available",
                "components": [
                    {
                        "component": str(item.get("component", "unknown"))[:64],
                        "status": str(item.get("status", "unknown"))[:32],
                        "returncode": item.get("returncode")
                        if type(item.get("returncode")) is int else None,
                    }
                    for item in payload.get("results", [])[:8]
                    if isinstance(item, dict)
                ],
            }
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

def public_diagnostics(agent, diagnostic):
    """Allowlist fields published to GitHub; never publish raw exception/mail text."""
    if not isinstance(diagnostic, dict):
        return {"diagnostics_status": "unavailable"}
    if agent == "ACS-03":
        components = []
        valid_statuses = {"healthy", "warning", "critical", "execution_failure"}
        known_components = {
            "fitness_tracking_verifier", "health_master", "backup_fitness"
        }
        for item in (diagnostic.get("components") or [])[:8]:
            if not isinstance(item, dict):
                continue
            name = item.get("component")
            status = item.get("status")
            code = item.get("returncode")
            components.append({
                "component": name if name in known_components else "unknown",
                "status": status if status in valid_statuses else "unknown",
                "returncode": code if type(code) is int and -1 <= code <= 255 else None,
            })
        return {
            "diagnostics_status": diagnostic.get("diagnostics_status")
            if diagnostic.get("diagnostics_status") in ("available", "missing", "unreadable")
            else "unavailable",
            "components": components,
        }
    if agent == "ACS-04":
        findings = []
        for item in (diagnostic.get("findings") or [])[:10]:
            if not isinstance(item, dict):
                continue
            code = item.get("code")
            if not isinstance(code, str) or not code.isascii() or not code.replace("_", "").isalnum() or len(code) > 48:
                code = "UNCLASSIFIED"
            findings.append({"severity": item.get("severity") if item.get("severity") in ("warning", "critical") else "unknown",
                             "code": code, "repaired": item.get("repaired") is True})
        return {"overall_status": diagnostic.get("overall_status") if diagnostic.get("overall_status") in ("healthy", "warning", "critical", "execution_failure") else "unknown",
                "findings": findings}
    if agent == "ACS-05":
        critical = diagnostic.get("critical") or []
        warnings = diagnostic.get("warnings") or []
        codes = []
        for message in list(critical) + list(warnings):
            lower = str(message).lower()
            if "invalid_grant" in lower or "revoked" in lower:
                code = "GOOGLE_OAUTH_INVALID_GRANT"
            elif "deleted_client" in lower or "client has been deleted" in lower:
                code = "GOOGLE_OAUTH_CLIENT_DELETED"
            elif "invalid_client" in lower:
                code = "GOOGLE_OAUTH_INVALID_CLIENT"
            elif "gmail" in lower or "google oauth" in lower:
                code = "GOOGLE_OAUTH_OR_GMAIL_FAILURE"
            elif "absorption" in lower or "knowledge" in lower:
                code = "KNOWLEDGE_FRESHNESS_WARNING"
            elif "infrastructure" in lower or "acs-04" in lower:
                code = "INFRASTRUCTURE_EVIDENCE_WARNING"
            elif "prediction" in lower:
                code = "PREDICTION_FEED_WARNING"
            elif "memory" in lower or "compressor" in lower:
                code = "MEMORY_MAINTENANCE_WARNING"
            elif "vpn" in lower or "security" in lower:
                code = "SECURITY_VERIFICATION_WARNING"
            elif "twilio" in lower or "sms" in lower:
                code = "ALERT_DELIVERY_WARNING"
            elif "process" in lower or "resource" in lower or "fork" in lower:
                code = "RESOURCE_PRESSURE_WARNING"
            elif "master control" in lower or "guard" in lower:
                code = "ORCHESTRATION_WIRING_WARNING"
            else:
                code = "CONTINUITY_OTHER_FINDING"
            if code not in codes:
                codes.append(code)
        return {
            "last_status": diagnostic.get("last_status") if diagnostic.get("last_status") in ("OK", "WARN", "CRITICAL") else "UNKNOWN",
            "critical_count": len(critical), "warning_count": len(warnings),
            "issue_codes": codes[:10],
        }
    return {"diagnostics_status": "unavailable"}


def sanitize_public_snapshot(snapshot):
    """Reduce a private runtime report to fixed non-secret fields before publishing."""
    safe = {
        "schema_version": snapshot.get("schema_version"),
        "generated_at_utc": snapshot.get("generated_at_utc"),
        "source": "pythonanywhere",
        "active_branch": snapshot.get("active_branch"),
        "critical_paths": snapshot.get("critical_paths", []),
    }
    allowed_agent_keys = ("agent", "role", "cadence", "verified", "status",
                          "health_status", "last_execution_utc", "age_seconds",
                          "stale_after_seconds", "runtime_component")
    def clean_agent(agent, data):
        if not isinstance(data, dict):
            return {"verified": False, "status": "unreadable"}
        out = {k: data[k] for k in allowed_agent_keys if k in data}
        if "diagnostics" in data:
            out["diagnostics"] = public_diagnostics(agent, data["diagnostics"])
        return out
    safe["agents"] = {name: clean_agent(name, info)
                      for name, info in (snapshot.get("agents") or {}).items()
                      if name in ("ACS-01", "ACS-02", "ACS-03", "ACS-04", "ACS-05")}
    safe["acs01_orchestrator"] = clean_agent("ACS-01", snapshot.get("acs01_orchestrator", {}))
    knowledge = snapshot.get("knowledge_validation") or {}
    safe["knowledge_validation"] = {"status": knowledge.get("status")}
    sync = (snapshot.get("self_heal") or {}).get("branch_sync") or {}
    allowed_sync_keys = ("ok", "status", "branch", "remote", "head", "remote_head",
                         "ahead_before", "behind_before", "ahead_after", "behind_after", "returncode")
    # Do not claim that a successful no-op sync proved recovery from failure.
    # Recovery is verified only when a real remote-behind state was corrected.
    recovery_proof = {
        "verified": (
            sync.get("ok") is True
            and sync.get("status") == "synced"
            and isinstance(sync.get("behind_before"), int)
            and sync["behind_before"] > 0
            and sync.get("ahead_after") == 0
            and sync.get("behind_after") == 0
        ),
        "test_type": "observed_remote_divergence_recovery",
        "not_tested": "process_crash_and_external_scheduler_outage",
    }
    post = (snapshot.get("self_heal") or {}).get("post_sync_cycles") or {}
    outcomes = {}
    for name, attempts in (post.get("outcomes") or {}).items():
        if name in ("ACS-04", "ACS-05"):
            outcomes[name] = [{"ok": a.get("ok") is True, "returncode": a.get("returncode")}
                              for a in attempts if isinstance(a, dict)]
    safe["self_heal"] = {
        "recovery_proof": recovery_proof,
        "branch_sync": {k: sync[k] for k in allowed_sync_keys if k in sync},
        "post_sync_cycles": {"attempted": post.get("attempted") is True, "outcomes": outcomes},
    }
    git = snapshot.get("git") or {}
    status = git.get("status") or {}
    commit = git.get("last_commit") or {}
    safe["git"] = {
        "status": {"ok": status.get("ok"), "returncode": status.get("returncode"),
                   "tracked_changes_count": len((status.get("stdout") or "").splitlines())},
        "unresolved_merge_conflict": git.get("unresolved_merge_conflict") is True,
        "last_commit": {"ok": commit.get("ok"),
                        "sha": (commit.get("stdout") or "").split("|")[0][:40]},
        "origin_reachable": {"ok": (git.get("origin_reachable") or {}).get("ok")},
    }
    schedule = snapshot.get("pythonanywhere_schedule") or {}
    safe["pythonanywhere_schedule"] = {
        "available": schedule.get("available") is True,
        "acs01_task": schedule.get("acs01_task", {}),
        "health_task": schedule.get("health_task", {}),
    }
    return safe



def main():
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
    OUT.write_text(json.dumps(sanitize_public_snapshot(snapshot), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    
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


if __name__ == "__main__":
    main()
