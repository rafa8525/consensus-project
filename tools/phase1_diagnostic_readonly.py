#!/usr/bin/env python3
"""Read-only Phase 1 diagnostic: no secrets, mutations or outbound messages."""
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
home=Path.home()
root=home/"consensus-project"
def run(*args):
    p=subprocess.run(args,cwd=root,text=True,capture_output=True,timeout=60)
    return p.stdout if p.returncode==0 else ""
print("=== ACS Phase 1 read-only diagnosis ===")
print("UTC",dt.datetime.now(dt.timezone.utc).isoformat())
print("branch",run("git","branch","--show-current").strip())
status=run("git","status","--porcelain=v1","-uno").splitlines()
runtime_prefix=("memory/logs/","memory/agents/","memory/exports/","memory/state/")
runtime_files={"memory/centralized_knowledge_base.txt","memory/security_audit_schedule.txt"}
runtime=[];source=[]
for line in status:
    path=line[3:]
    (runtime if path.startswith(runtime_prefix) or path in runtime_files else source).append(path)
print("tracked runtime paths",len(runtime))
for path in runtime: print("  runtime",path)
print("tracked source/config paths",len(source))
for path in source: print("  review",path)
now=dt.datetime.now(dt.timezone.utc)
candidates=[]
for base in (root/"memory/logs/system/predictions",home/"memory/logs/system/predictions"):
    for offset in (0,1):
        p=base/("prediction_feed_"+(now-dt.timedelta(days=offset)).date().isoformat()+".md")
        if p.is_file() and p not in candidates:
            candidates.append(p)
print("prediction candidates",len(candidates))
for p in candidates:
    body=p.read_text(encoding="utf-8",errors="replace")
    stamps=re.findall(r"^Generated:\s*(20\d{2}-\d{2}-\d{2}T[^\s]+)\s*$",body,re.M)
    findings=[]
    if "Health snapshot is stale" in body: findings.append("stale upstream snapshot")
    if "Health snapshot freshness is unknown" in body: findings.append("unknown upstream freshness")
    if re.search(r"System health:\s*(WARN|ERROR|CRITICAL|FAIL)",body,re.I): findings.append("degraded upstream health")
    age=None
    if len(stamps)==1:
        try:
            stamp=dt.datetime.fromisoformat(stamps[0].replace("Z","+00:00"))
            if stamp.tzinfo: age=round((now-stamp).total_seconds()/3600,2)
        except ValueError: pass
    print("feed",str(p),"generated_age_hours",age,"findings",findings or "none","mtime_utc",dt.datetime.fromtimestamp(p.stat().st_mtime,dt.timezone.utc).isoformat())
try:
    from common.twilio_config import load_existing_twilio_settings
    settings=load_existing_twilio_settings()
    for key in ("TWILIO_ACCOUNT_SID","TWILIO_AUTH_TOKEN","TWILIO_FROM_NUMBER","TWILIO_TO_NUMBER"):
        print("twilio",key,"configured" if settings.get(key) else "missing")
    for key in ("TWILIO_ENABLE_SEND","TWILIO_SILENCE"):
        print("twilio",key,"1" if settings.get(key)=="1" else "0")
except Exception as exc:
    print("twilio config error type",type(exc).__name__)
for p in (root/"memory/logs/system/continuity_guardian_state.json",home/"memory/logs/system/continuity_guardian_state.json"):
    try:
        state=json.loads(p.read_text())
    except (OSError,ValueError):
        continue
    print("continuity state",str(p),"status",state.get("last_status"))
    for key in ("critical","warnings"):
        raw=state.get(key,[])
        # Older state schemas can store one string rather than an array.
        findings=raw if isinstance(raw,list) else ([raw] if isinstance(raw,str) and raw else [])
        print(key,"stored_type",type(raw).__name__,"finding_count",len(findings))
        for finding in findings[:12]:
            # Do not reveal paths, personal data or credentials from raw findings.
            low=str(finding).lower()
            category=("prediction" if "prediction" in low else
                      "alert" if "twilio" in low or "sms" in low else
                      "oauth" if "oauth" in low or "gmail" in low else
                      "infrastructure" if "infrastructure" in low else
                      "other")
            print(key,"category",category)
print("COMPLETE: read only")
