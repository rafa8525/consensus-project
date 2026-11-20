#!/usr/bin/env python3
"""Read-only, privacy-preserving ACS-03/05 diagnostics. No network or code execution.

Inspect existing state metadata. Never output raw state strings, metrics or secrets.
"""
from __future__ import annotations
import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

RECOGNIZED = frozenset({"health_connect_cloud_cycle", "fitness_tracking_verifier",
                        "health_master", "backup_fitness"})
def _time(value):
    if not isinstance(value, str):
        return None
    try:
        stamp = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        return stamp.astimezone(timezone.utc) if stamp.tzinfo else None
    except (ValueError, OverflowError):
        return None

def _json(path, limit=2_000_000):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None

def fitness_evidence(path, now=None, max_bytes=2_000_000):
    """Only disclose freshness/validity category, never personal measurements."""
    now = now or datetime.now(timezone.utc)
    if path.is_symlink(): return "symlink_rejected"
    if not path.is_file(): return "source_missing"
    if path.stat().st_size > max_bytes: return "size_limit_exceeded"
    from json import JSONDecodeError
    metrics = ("steps", "active_minutes", "swim_laps", "laps", "heart_rate", "avg_hr",
               "max_hr", "weight_lbs", "bmi", "distance_km", "calories", "sleep_minutes")
    newest = None
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except JSONDecodeError:
                    continue
                if not isinstance(record, dict): continue
                stamp = _time(record.get("timestamp") or record.get("time") or record.get("ts"))
                if stamp is None: continue
                has_numeric = any(type(record.get(k)) in (int, float)
                    and math.isfinite(record[k]) for k in metrics)
                age = (now - stamp).total_seconds()
                if has_numeric and age >= -300 and (newest is None or stamp > newest):
                    newest = stamp
    except (OSError, UnicodeError):
        return "source_unreadable"
    if newest is None: return "no_valid_measurements"
    return "current" if (now - newest).total_seconds() <= 86400 else "stale_over_24h"

def diagnose(repo, memory_root=None, now=None):
    repo = Path(repo)
    mem = Path(memory_root) if memory_root is not None else repo / "memory"
    now = now or datetime.now(timezone.utc)
    acs03 = _json(mem / "agents" / "acs03_state.json")
    acs05 = _json(mem / "agents" / "acs05_state.json")
    guardian = _json(mem / "logs" / "system" / "continuity_guardian_state.json")
    components = []
    if isinstance(acs03, dict):
        for item in (acs03.get("results") or [])[:12]:
            if not isinstance(item, dict) or item.get("component") not in RECOGNIZED: continue
            code = item.get("returncode")
            components.append({"component": item["component"],
                               "status": item.get("status") if item.get("status") in
                                ("healthy", "warning", "critical", "execution_failure") else "unknown",
                               "returncode": code if type(code) is int and -1 <= code <= 255 else None,
                               "error_type": "present" if item.get("error") else "not_recorded"})
    guardian_findings = []
    if isinstance(guardian, dict):
        # Avoid printing message text or private exception strings.
        for severity in ("critical", "warnings"):
            values = guardian.get(severity, [])
            if isinstance(values, list):
                guardian_findings.append({"category": severity, "count": len(values)})
    return {
        "source": "local_private_state_metadata_only",
        "report_utc": now.isoformat(),
        "acs03_state": "available" if isinstance(acs03, dict) else "missing_or_unreadable",
        "acs03_reported_health": acs03.get("status") if isinstance(acs03, dict) and
             acs03.get("status") in ("healthy", "warning", "critical", "execution_failure") else "unknown",
        "acs03_components": components,
        "fitness_input": fitness_evidence(mem / "logs/fitness/daily_metrics.jsonl", now),
        "acs05_state": "available" if isinstance(acs05, dict) else "missing_or_unreadable",
        "acs05_reported_health": acs05.get("status") if isinstance(acs05, dict) and
             acs05.get("status") in ("healthy", "warning", "critical", "execution_failure") else "unknown",
        "guardian_state": "available" if isinstance(guardian, dict) else "missing_or_unreadable",
        "guardian_summary": guardian_findings,
        "cloud_script_state": ("exists" if (Path.home()/"acs-runtime/repairs/acs03/cloud/health_connect_cloud_cycle.py").is_file()
             else "not_present_at_default_path"),
        "production_mutations": 0,
        "secrets_or_personal_records_in_output": False,
        "actual_fault_cause_confirmed": False,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.home()/"consensus-project")
    parser.add_argument("--memory-root", type=Path)
    a = parser.parse_args()
    print(json.dumps(diagnose(a.repo, a.memory_root), sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
