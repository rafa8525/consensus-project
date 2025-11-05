#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
from datetime import datetime, timezone

HOME  = Path.home()
TOOLS = HOME / "consensus-project" / "tools"
SYS   = HOME / "memory" / "logs" / "system"
SYS.mkdir(parents=True, exist_ok=True)

CHECKS = [
  ("security_suite.py",       ["python3", str(TOOLS/"security_suite.py")]),
  ("morning_master.py",       ["python3", str(TOOLS/"morning_master.py")]),
  ("publish_status_report.py",["python3", str(TOOLS/"publish_status_report.py")]),
  ("agent_log_indexer.py",    ["python3", str(TOOLS/"agent_log_indexer.py")]),
  ("kb_smoke_test.py",        ["python3", str(TOOLS/"kb_smoke_test.py")]),
  ("knowledge_share_kpi.py",  ["python3", str(TOOLS/"knowledge_share_kpi.py")]),
  ("geofence_nudger.py",      ["python3", str(TOOLS/"geofence_nudger.py")]),
  ("vpn_test_runner.py",      ["python3", str(TOOLS/"vpn_test_runner.py")]),
  ("ride_deals_scan.py",      ["python3", str(TOOLS/"ride_deals_scan.py")]),
]

def run(cmd):
  try:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=False)
    return p.returncode, (p.stdout or "")[-400:], (p.stderr or "")[-200:]
  except Exception as e:
    return -1, "", f"EXC:{e}"

def main():
  issues=[]
  for name, cmd in CHECKS:
    path = TOOLS / name
    if not path.exists():
      issues.append({"missing": name})
      continue
    rc,out,err = run(cmd)
    if rc != 0:
      issues.append({"tool": name, "rc": rc, "err": err})
  ok = not issues
  summary = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "status": "OK" if ok else "ISSUES",
    "issues": issues,
    "recommend_cron_utc": [
      "00:00  python3 ~/consensus-project/tools/run_absorption.py",
      "18:00  python3 ~/consensus-project/tools/run_absorption.py",
      "Sun 03:00  python3 ~/consensus-project/tools/weekly_agent_email.py",
      "Tue & Fri 19:00  python3 ~/consensus-project/tools/ride_deals_scan.py"
    ]
  }
  print(json.dumps(summary, indent=2))
  (SYS/"consensus_doctor.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
  raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
  main()
