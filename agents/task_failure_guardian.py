#!/usr/bin/env python3
"""
AI Task Failure Guardian
Purpose:
- Monitor critical AI Consensus scheduled-task logs for failures and staleness.
- Send one deduplicated SMS alert via the existing Twilio setup when something breaks.
- Maintain a local heartbeat/state file so the guardian can be audited.
- Stay quiet when everything is healthy.

Designed for PythonAnywhere / Linux.
Python 3.10+; standard library only unless Twilio SMS is enabled, in which case
it uses direct HTTPS requests (no Twilio Python package required).
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = Path("/home/rafa1215/consensus-project/config/task_failure_guardian_config.json")
DEFAULT_STATE = Path("/home/rafa1215/memory/state/task_failure_guardian_state.json")
DEFAULT_HEARTBEAT = Path("/home/rafa1215/memory/logs/system/task_failure_guardian_heartbeat.json")
DEFAULT_ALERT_LOG = Path("/home/rafa1215/memory/logs/system/task_failure_guardian_alerts.log")

FAILURE_PATTERNS = [
    re.compile(r"\breturn code (?:was|=)\s*([1-9]\d*)\b", re.I),
    re.compile(r"\bTraceback \(most recent call last\)", re.I),
    re.compile(r"\bNo such file or directory\b", re.I),
    re.compile(r"\bbad interpreter\b", re.I),
    re.compile(r"\bsyntax error\b", re.I),
    re.compile(r"\bcommand not found\b", re.I),
    re.compile(r"\bpermission denied\b", re.I),
    re.compile(r"\bModuleNotFoundError\b", re.I),
    re.compile(r"\bImportError\b", re.I),
    re.compile(r"\bERROR:", re.I),
    re.compile(r"\bFATAL:", re.I),
]

# These are often harmless/noisy in monitor output and should not automatically alert.
IGNORE_PATTERNS = [
    re.compile(r"ERROR: prediction health line missing", re.I),  # handled by snapshot checks if configured
]

@dataclass
class Finding:
    task: str
    kind: str
    detail: str
    source: str

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def iso(dt: datetime | None = None) -> str:
    return (dt or utcnow()).isoformat()

def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True))
    tmp.replace(path)

def tail_text(path: Path, max_bytes: int = 120_000) -> str:
    with path.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - max_bytes))
        return f.read().decode("utf-8", errors="replace")

def is_ignored(line: str) -> bool:
    return any(p.search(line) for p in IGNORE_PATTERNS)

def scan_log(task: dict) -> list[Finding]:
    findings: list[Finding] = []
    path = Path(task["log"])
    name = task["name"]
    max_age_minutes = int(task.get("max_age_minutes", 0))

    if not path.exists():
        findings.append(Finding(name, "missing_log", "Log file does not exist", str(path)))
        return findings

    if max_age_minutes > 0:
        age_min = (time.time() - path.stat().st_mtime) / 60.0
        if age_min > max_age_minutes:
            findings.append(
                Finding(name, "stale_log",
                        f"Log has not changed for {age_min:.0f} minutes; threshold is {max_age_minutes}",
                        str(path))
            )

    text = tail_text(path, int(task.get("tail_bytes", 120_000)))
    lines = text.splitlines()
    recent_lines = lines[-int(task.get("tail_lines", 300)):]

    for line in recent_lines:
        if is_ignored(line):
            continue
        for pat in FAILURE_PATTERNS:
            m = pat.search(line)
            if m:
                findings.append(Finding(name, "failure_pattern", line.strip()[:500], str(path)))
                break

    # Optional explicit healthy marker. If configured, require it in the recent tail.
    healthy_regex = task.get("healthy_regex")
    if healthy_regex and not re.search(healthy_regex, text, re.I | re.M):
        findings.append(
            Finding(name, "missing_health_marker",
                    f"Expected health marker not found: {healthy_regex}",
                    str(path))
        )

    return findings

def scan_file_check(check: dict) -> list[Finding]:
    findings: list[Finding] = []
    path = Path(check["path"])
    name = check["name"]
    max_age_minutes = int(check.get("max_age_minutes", 0))

    if not path.exists():
        findings.append(Finding(name, "missing_file", "Expected file does not exist", str(path)))
        return findings

    if max_age_minutes > 0:
        age_min = (time.time() - path.stat().st_mtime) / 60.0
        if age_min > max_age_minutes:
            findings.append(
                Finding(name, "stale_file",
                        f"Expected file is {age_min:.0f} minutes old; threshold is {max_age_minutes}",
                        str(path))
            )

    if check.get("json_status_key"):
        data = load_json(path, {})
        key = check["json_status_key"]
        expected = check.get("json_status_value", "ok")
        actual = data.get(key)
        if actual != expected:
            findings.append(
                Finding(name, "bad_json_status",
                        f"{key}={actual!r}; expected {expected!r}",
                        str(path))
            )
    return findings

def finding_key(f: Finding) -> str:
    # Stable key for alert deduplication.
    normalized = re.sub(r"\d{4}-\d{2}-\d{2}[T ][0-9:.+\-Z]+", "<timestamp>", f.detail)
    return f"{f.task}|{f.kind}|{normalized[:240]}"

def append_alert_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{iso()} {message}\n")

def send_twilio_sms(body: str) -> tuple[bool, str]:
    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_num = (os.getenv("TWILIO_FROM_NUMBER") or os.getenv("TWILIO_PHONE_NUMBER") or "").strip()
    to_num = (os.getenv("ALERT_TO_NUMBER") or os.getenv("TWILIO_TO_NUMBER") or "").strip()

    if not all([sid, token, from_num, to_num]):
        return False, "Twilio environment variables are incomplete"

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    payload = urllib.parse.urlencode({
        "From": from_num,
        "To": to_num,
        "Body": body[:1500],
    }).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            if 200 <= r.status < 300:
                return True, f"Twilio HTTP {r.status}"
            return False, f"Twilio HTTP {r.status}"
    except Exception as e:
        return False, f"Twilio send failed: {e}"

def main() -> int:
    config_path = Path(os.getenv("TASK_FAILURE_GUARDIAN_CONFIG", str(DEFAULT_CONFIG)))
    if not config_path.exists():
        print(f"FATAL: config not found: {config_path}", file=sys.stderr)
        return 2

    config = load_json(config_path, {})
    state_path = Path(config.get("state_file", str(DEFAULT_STATE)))
    heartbeat_path = Path(config.get("heartbeat_file", str(DEFAULT_HEARTBEAT)))
    alert_log = Path(config.get("alert_log", str(DEFAULT_ALERT_LOG)))

    findings: list[Finding] = []
    for task in config.get("tasks", []):
        if task.get("enabled", True):
            findings.extend(scan_log(task))

    for check in config.get("file_checks", []):
        if check.get("enabled", True):
            findings.extend(scan_file_check(check))

    state = load_json(state_path, {"active": {}, "last_run_utc": None})
    active_prev: dict[str, Any] = state.get("active", {})
    active_now: dict[str, Any] = {}

    cooldown_min = int(config.get("repeat_alert_minutes", 360))
    now = utcnow()
    new_or_repeat: list[Finding] = []

    for f in findings:
        key = finding_key(f)
        prev = active_prev.get(key, {})
        first_seen = prev.get("first_seen_utc", iso(now))
        last_alert = prev.get("last_alert_utc")
        should_alert = last_alert is None
        if last_alert:
            try:
                age = (now - datetime.fromisoformat(last_alert)).total_seconds() / 60
                should_alert = age >= cooldown_min
            except Exception:
                should_alert = True

        active_now[key] = {
            "task": f.task,
            "kind": f.kind,
            "detail": f.detail,
            "source": f.source,
            "first_seen_utc": first_seen,
            "last_seen_utc": iso(now),
            "last_alert_utc": iso(now) if should_alert else last_alert,
        }
        if should_alert:
            new_or_repeat.append(f)

    # Recovery detection
    recovered_keys = set(active_prev) - set(active_now)
    recoveries = [active_prev[k] for k in recovered_keys]

    if new_or_repeat:
        lines = ["AI Consensus task failure detected:"]
        for f in new_or_repeat[:6]:
            lines.append(f"- {f.task}: {f.kind} — {f.detail[:180]}")
        if len(new_or_repeat) > 6:
            lines.append(f"- plus {len(new_or_repeat)-6} more finding(s)")
        body = "\n".join(lines)
        ok, status = send_twilio_sms(body)
        append_alert_log(alert_log, f"ALERT send={ok} status={status} body={body!r}")
        if not ok:
            print(body)
            print(f"ALERT DELIVERY WARNING: {status}", file=sys.stderr)

    if recoveries and config.get("send_recovery_sms", True):
        names = sorted({r.get("task", "unknown") for r in recoveries})
        body = "AI Consensus recovery: " + ", ".join(names[:8]) + " is healthy again."
        ok, status = send_twilio_sms(body)
        append_alert_log(alert_log, f"RECOVERY send={ok} status={status} body={body!r}")

    state = {
        "last_run_utc": iso(now),
        "active": active_now,
        "finding_count": len(findings),
    }
    save_json(state_path, state)
    save_json(heartbeat_path, {
        "status": "ok" if not findings else "degraded",
        "last_run_utc": iso(now),
        "finding_count": len(findings),
        "active_tasks": sorted({f.task for f in findings}),
    })

    if findings:
        print(f"Guardian completed: {len(findings)} active finding(s)")
    else:
        print("Guardian completed: all monitored tasks healthy")

    # Return 0 even when downstream tasks are unhealthy, because the guardian itself worked.
    # Return nonzero only when the guardian itself cannot execute correctly.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
