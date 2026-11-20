"""Read-only public ACS health triage. Never touches production or credentials."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

EXPECTED = tuple(f"ACS-{i:02}" for i in range(1,6))
HEALTHY = {"healthy", "ok"}
ACS03_COMPONENTS = {"health_connect_cloud_cycle", "fitness_tracking_verifier",
                    "health_master", "backup_fitness"}
ACS05_CODES = {"ORCHESTRATION_WIRING_WARNING", "ALERT_DELIVERY_WARNING"}

def assess(report, now=None):
    if not isinstance(report,dict): raise ValueError("Health snapshot must be an object")
    timestamp=report.get("generated_at_utc")
    if not isinstance(timestamp,str): raise ValueError("Missing report timestamp")
    t=datetime.fromisoformat(timestamp.replace("Z","+00:00"))
    if t.tzinfo is None: raise ValueError("Timestamp must be timezone-aware")
    now=now or datetime.now(timezone.utc)
    age=(now-t.astimezone(timezone.utc)).total_seconds()/3600
    agents=report.get("agents")
    if not isinstance(agents,dict): raise ValueError("Agent statuses missing")
    findings=[]
    for key in EXPECTED:
        record=agents.get(key)
        if not isinstance(record,dict): 
            findings.append({"agent":key,"severity":"unknown","reason":"missing_agent"})
            continue
        health=record.get("health_status")
        if health not in HEALTHY or record.get("status") != "current":
            findings.append({"agent":key,"severity":"attention","reason":"reported_unhealthy",
                             "health_status":str(health)[:40]})
    acs03=agents.get("ACS-03",{})
    acs03=acs03 if isinstance(acs03,dict) else {}
    components=(acs03.get("diagnostics") or {}).get("components") or []
    failed=[]
    for item in components[:8]:
        if not isinstance(item,dict): continue
        name=item.get("component")
        if name in ACS03_COMPONENTS and item.get("status")=="execution_failure":
            failed.append({"component":name,
                           "returncode":item.get("returncode") if type(item.get("returncode")) is int else None})
    acs05=agents.get("ACS-05",{})
    acs05=acs05 if isinstance(acs05,dict) else {}
    diag=acs05.get("diagnostics") or {}
    codes=[c for c in (diag.get("issue_codes") or []) if isinstance(c,str)]
    safe_codes=[c for c in codes if c in ACS05_CODES]
    actions=[]
    if any(x["component"]=="health_connect_cloud_cycle" for x in failed):
        actions.append("Inspect private PythonAnywhere stderr for the external ACS-03 cloud-cycle script; do not guess missing files or credentials")
    if any(x["component"]=="fitness_tracking_verifier" for x in failed):
        actions.append("Inspect genuine fitness JSONL presence, measurement validity and <=24-hour timestamp freshness; do not fabricate or touch timestamps")
    if "ORCHESTRATION_WIRING_WARNING" in safe_codes:
        actions.append("Inspect private continuity guardian finding and Master Control Loop dispatch/run evidence before any wiring changes")
    if "ALERT_DELIVERY_WARNING" in safe_codes:
        actions.append("Inspect private alert transport and Twilio error category without disclosing credentials or sending test messages")
    actions.append("Re-run ACS checks only in authorized live environment, then verify a new published snapshot; never mark healthy on code inspection alone")
    return {"source":"public_snapshot_only","generated_at_utc":timestamp,
            "age_hours":round(age,2),"fresh_within_30_hours":0<=age<=30,
            "healthy_agents":sorted(k for k,v in agents.items() if k in EXPECTED and isinstance(v,dict)
                                    and v.get("status")=="current" and v.get("health_status") in HEALTHY),
            "unhealthy_findings":findings,"acs03_failed_components":failed,
            "acs05_issue_codes":safe_codes,"actions":actions,
            "production_repair_performed":False,"phase1_certified":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("snapshot",type=Path)
    args=p.parse_args()
    if args.snapshot.stat().st_size>100000: raise ValueError("Snapshot too large")
    print(json.dumps(assess(json.loads(args.snapshot.read_text(encoding="utf-8"))),indent=2,sort_keys=True))
if __name__=="__main__": main()
