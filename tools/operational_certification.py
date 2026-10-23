#!/usr/bin/env python3
"""Read-only ACS operational certification. Never loads credentials or sends SMS."""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

UTC = timezone.utc

def parse_time(raw):
    stamp = datetime.fromisoformat(str(raw).strip().replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("timezone missing")
    return stamp.astimezone(UTC)

def age_ok(value, now, max_minutes, *, future_minutes=2):
    age = (now - parse_time(value)).total_seconds() / 60
    return -future_minutes <= age <= max_minutes

def evaluate(repo: Path, mem: Path, now: datetime) -> dict:
    checks = {}
    def add(name, passed, detail):
        checks[name] = {"pass": bool(passed), "detail": detail}
    # Evaluate the latest *complete* cycle, not a past successful marker.
    try:
        lines = (repo / "memory/logs/system/master_control_loop.log").read_text(errors="replace").splitlines()
        starts = [i for i, line in enumerate(lines) if "==== Master Control Loop Cycle Start ====" in line]
        last = lines[starts[-1]:] if starts else []
        ends = [(i, line) for i, line in enumerate(last) if "==== Master Control Loop Cycle Complete ====" in line]
        if not ends:
            add("unattended_cycle", False, "no completed latest cycle")
        else:
            section = last[:ends[0][0]+1]
            completed = section[-1]
            match = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", completed)
            if not match:
                raise ValueError("missing cycle completion timestamp")
            # MCL log timestamps use local machine time with no offset. Compare
            # freshness via the log file mtime; avoid assuming its timezone.
            fresh = 0 <= (now.timestamp() - (repo / "memory/logs/system/master_control_loop.log").stat().st_mtime) / 60 <= 45
            success = any("✅ All subsystems executed successfully." in line for line in section)
            failed = any("❌" in line or "Complete (FAIL)" in line for line in section)
            add("unattended_cycle", fresh and success and not failed, "latest complete cycle PASS" if fresh and success and not failed else "latest cycle stale or contains failure")
    except (OSError, ValueError) as exc:
        add("unattended_cycle", False, type(exc).__name__)
    try:
        doc = (mem / "logs/status/system_health_snapshot.md").read_text(errors="replace")
        generated = re.findall(r"^- Generated:\s*(\S+)\s*$", doc, re.M)
        overall = re.findall(r"^- Overall:\s*(\w+)\s*$", doc, re.M)
        ok = len(generated) == 1 and age_ok(generated[0], now, 180) and len(overall)==1 and overall[0].lower()=="ok"
        add("health_snapshot", ok, "fresh and OK" if ok else "missing, stale or not OK")
    except (OSError, ValueError):
        add("health_snapshot", False, "missing or invalid")
    try:
        infra = json.loads((mem / "logs/system/infrastructure_guardian_status.json").read_text())
        finished = infra["finished_at"]
        ok = age_ok(finished, now, 90) and infra.get("overall_status") == "healthy"
        add("acs04", ok, "recent healthy canonical report" if ok else "stale or unhealthy canonical report")
    except (OSError, ValueError, KeyError, TypeError):
        add("acs04", False, "missing or invalid canonical report")
    try:
        state = json.loads((repo / "memory/logs/system/continuity_guardian_state.json").read_text())
        ok = (age_ok(state["last_full_check_utc"], now, 90)
              and state.get("last_status")=="OK"
              and not state.get("critical") and not state.get("warnings"))
        add("acs05", ok, "recent full check OK" if ok else "stale, critical or warning")
    except (OSError, ValueError, KeyError, TypeError):
        add("acs05", False, "missing or invalid state")
    try:
        today = now.date()
        candidates = [mem / "logs/system/predictions" / f"prediction_feed_{day.isoformat()}.md"
            for day in (today, today - timedelta(days=1))]
        valid = False
        for file in candidates:
            if not file.is_file():
                continue
            content = file.read_text(errors="replace")
            stamps = re.findall(r"^Generated:\s*(\S+)\s*$", content, re.M)
            if len(stamps)==1 and age_ok(stamps[0], now, 26*60):
                valid = True
                break
        add("prediction_feed", valid, "recent generated feed" if valid else "missing or stale generated feed")
    except (OSError, ValueError):
        add("prediction_feed", False, "missing or invalid")
    # Never load .env / .pa_env.json here. Guard configuration is tested as code,
    # while real SMS delivery remains UNVERIFIED until separately authorized.
    try:
        guard = (repo / "common/twilio_guard.py").read_text()
        agent = (repo / "agents/continuity_guardian_agent.py").read_text()
        safe = all(marker in guard for marker in (
            'TWILIO_SILENCE', 'TWILIO_ENABLE_SEND', 'def send_sms(', 'RATE_PER_MIN'
        )) and 'twilio_guard.send_sms(' in agent
        add("sms_safety_code", safe, "safety gate present; delivery not exercised" if safe else "safety gate not proven")
    except OSError:
        add("sms_safety_code", False, "SMS safety code unavailable")
    core = all(v["pass"] for k,v in checks.items() if k != "sms_safety_code")
    return {
        "core_certified_now": core,
        "sms_safety_code_verified": checks["sms_safety_code"]["pass"],
        "sms_delivery_verified": False,
        "full_operational_certification": False,
        "checks": checks,
        "note": "Read-only snapshot. No message sent; does not prove future recovery."
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.home() / "consensus-project")
    parser.add_argument("--memory", type=Path, default=Path.home() / "memory")
    args = parser.parse_args()
    result = evaluate(args.repo, args.memory, datetime.now(UTC))
    print(json.dumps(result, indent=2))
    return 0 if result["core_certified_now"] and result["sms_safety_code_verified"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
