#!/usr/bin/env python3
"""Read-only ACS-03 runtime diagnosis; prints no personal fitness records.

No agent cycles, SSH, external requests, state writes or file timestamps changed.
This is inspection only, not a repair and not certification.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

COMPONENTS = ("health_connect_cloud_cycle", "fitness_tracking_verifier",
              "health_master", "backup_fitness")


def summarize(root, home):
    root, home = Path(root), Path(home)
    checks = {}
    source = root / "memory/logs/fitness/daily_metrics.jsonl"
    state = root / "memory/agents/acs03_state.json"
    script = home / "acs-runtime/repairs/acs03/cloud/health_connect_cloud_cycle.py"
    checks["cloud_cycle_script_present"] = script.is_file()
    checks["verifier_script_present"] = (root / "tools/fitness_tracking_verifier.py").is_file()
    checks["fitness_source_present"] = source.is_file() and not source.is_symlink()
    checks["fitness_source_symlink"] = source.is_symlink()
    checks["state_present"] = state.is_file()
    checks["state_valid"] = False
    checks["fitness_source_age_hours"] = None
    checks["fitness_source_size_bytes"] = None
    if checks["fitness_source_present"]:
        try:
            stat = source.stat()
            checks["fitness_source_size_bytes"] = stat.st_size
            checks["fitness_source_age_hours"] = round(
                (datetime.now(timezone.utc).timestamp() - stat.st_mtime) / 3600, 1)
        except OSError:
            pass

    report = {"status": None, "results": [], "unexpected_component_count": 0}
    if checks["state_present"] and not state.is_symlink():
        try:
            payload = json.loads(state.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                results = payload.get("results")
                if not isinstance(results, list):
                    results = []
                report["status"] = payload.get("status") if payload.get("status") in (
                    "healthy", "warning", "critical", "execution_failure") else "unknown"
                checks["state_valid"] = True
                for item in results[:16]:
                    if not isinstance(item, dict):
                        report["unexpected_component_count"] += 1
                        continue
                    component = item.get("component")
                    if component not in COMPONENTS:
                        report["unexpected_component_count"] += 1
                        component = "unexpected_or_unnamed"
                    status = item.get("status")
                    status = status if status in ("healthy","warning","critical","execution_failure") else "unknown"
                    code = item.get("returncode")
                    report["results"].append({
                        "component": component,
                        "status": status,
                        "returncode": code if type(code) is int else None,
                        "exception_type": "captured_error" if item.get("error") else None,
                    })
        except (ValueError, OSError, UnicodeError):
            pass
    return {"mode": "read_only_no_personal_records", "checks": checks, "state": report}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.home() / "consensus-project")
    ap.add_argument("--home", type=Path, default=Path.home())
    args = ap.parse_args()
    print(json.dumps(summarize(args.root, args.home), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
