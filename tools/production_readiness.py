#!/usr/bin/env python3
"""Read-only, secret-safe production readiness report for AI Consensus.

Run from PythonAnywhere after obtaining the latest code:
    python3 tools/production_readiness.py

Does not fetch, reset, change files, execute agents, or reveal credential values.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENTS = ("ACS-02", "ACS-03", "ACS-04", "ACS-05")
MAX_STATE_AGE_HOURS = 36


def git(*args: str) -> str | None:
    try:
        p = subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                           text=True, check=False, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def state_health(path: Path, now: datetime) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("not a JSON object")
        stamp = data.get("finished_at_utc")
        if not isinstance(stamp, str):
            raise ValueError("missing finished_at_utc")
        when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if when.tzinfo is None:
            raise ValueError("timestamp has no timezone")
        age_hours = (now - when).total_seconds() / 3600
        status = data.get("status", "unknown")
        fresh = 0 <= age_hours <= MAX_STATE_AGE_HOURS
        return {
            "status": status if status in ("healthy", "warning", "critical", "execution_failure") else "unknown",
            "fresh": fresh,
            "age_hours": round(age_hours, 2),
            "verified": data.get("verified") is True,
        }
    except (OSError, ValueError, TypeError) as exc:
        return {"status": "unknown", "fresh": False, "verified": False,
                "reason": type(exc).__name__}


def build_report(repo: Path = REPO, environ: dict | None = None,
                 now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    environ = os.environ if environ is None else environ
    token_path = Path.home() / ".secrets/google/token_gmail.json"
    creds_path = Path.home() / ".secrets/google/credentials.json"
    statuses = {
        agent: state_health(repo / "memory/agents" /
                            (agent.lower().replace("-", "") + "_state.json"), now)
        for agent in AGENTS
    }
    # True means configured/present, NOT authenticated or delivered.
    alert_keys = ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
                  "TWILIO_FROM_NUMBER", "TWILIO_TO_NUMBER")
    alert_presence = {key: bool(environ.get(key)) for key in alert_keys}
    report = {
        "checked_at_utc": now.isoformat(),
        "branch": git("branch", "--show-current") if repo == REPO else "not_checked",
        "local_commit": git("rev-parse", "HEAD") if repo == REPO else "not_checked",
        "remote_tracking_commit": git("rev-parse", "origin/v1.1-dev") if repo == REPO else "not_checked",
        "agents": statuses,
        "gmail": {"oauth_token_file_present": token_path.is_file(),
                  "oauth_client_file_present": creds_path.is_file(),
                  "authorization_verified": False},
        "twilio": {
            "required_environment_present": alert_presence,
            "guard_enabled": environ.get("TWILIO_ENABLE_SEND") == "1",
            "guard_not_silenced": environ.get("TWILIO_SILENCE", "0") != "1",
            "delivery_verified": False,
        },
    }
    report["ready"] = (
        report["branch"] == "v1.1-dev"
        and bool(report["local_commit"])
        and report["local_commit"] == report["remote_tracking_commit"]
        and all(d["status"] == "healthy" and d["fresh"] and d["verified"]
                for d in statuses.values())
        and report["gmail"]["oauth_token_file_present"]
        and report["gmail"]["oauth_client_file_present"]
        and all(alert_presence.values())
        and report["twilio"]["guard_enabled"]
        and report["twilio"]["guard_not_silenced"]
    )
    # Explicitly distinguish static preflight from live authentication / SMS proof.
    report["scope"] = "configuration_and_recent_agent_state_only"
    report["production_verified"] = False
    return report


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
