#!/usr/bin/env python3
import os, json
from pathlib import Path
from datetime import date, datetime, timezone

ROOT = Path.home() / "consensus-project"
LOGS = ROOT / "memory" / "logs"
TODAY = date.today().isoformat()
SUG  = LOGS / "agents" / "suggestions" / f"suggestions_{TODAY}.jsonl"
DGST_DIR = LOGS / "agents" / "digests"
PROJ_UPD = LOGS / "project-updates"
DGST_DIR.mkdir(parents=True, exist_ok=True); PROJ_UPD.mkdir(parents=True, exist_ok=True)

def iso_now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def read_jsonl(p: Path):
    items=[]
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            try: items.append(json.loads(ln))
            except: pass
    return items

def summarize(items):
    by_impact = {"high":[], "medium":[], "low":[], "info":[]}
    for it in items:
        imp = (it.get("impact") or "low").lower()
        if imp not in by_impact: imp = "low"
        by_impact[imp].append(it)
    return by_impact
def write_digest(by_impact):
    lines = [f"# Agents Daily Digest — {TODAY}", f"- ts: {iso_now()}"]
    total = sum(len(v) for v in by_impact.values())
    lines.append(f"- total_suggestions: {total}")
    for bucket in ("high","medium","low","info"):
        if by_impact[bucket]:
            lines.append(f"\n## {bucket.capitalize()} ({len(by_impact[bucket])})")
            for it in by_impact[bucket]:
                title = it.get('title','(no title)')
                action = (it.get('action','') or '').replace('\n',' ')
                lines.append(f"- **{title}** — {action}")
    body = "\n".join(lines) + "\n"
    day = f"agents_digest_{TODAY}.md"
    (DGST_DIR / day).write_text(body, encoding="utf-8")
    (PROJ_UPD / day).write_text(body, encoding="utf-8")  # mirror for webhook/absorb
    return day
def maybe_sms(by_impact, digest_name):
    high = len(by_impact.get("high", []))
    if high <= 0:
        return {"status":"skipped","reason":"no high-impact"}
    allow = os.getenv("TWILIO_ALLOW_SEND","0") == "1"
    to = os.getenv("ALERT_PHONE","").strip()
    msg = f"Agents: {high} high-impact ideas — see {digest_name}"
    if not allow or not to:
        return {"status":"skipped","reason":"send not allowed or ALERT_PHONE missing","preview":msg}
    try:
        from common.twilio_guard import send_sms
        send_sms(to=to, body=msg)
        return {"status":"sent"}
    except Exception as e:
        return {"status":"error","error":str(e),"preview":msg}

def main():
    items = read_jsonl(SUG)
    by_impact = summarize(items)
    digest_name = write_digest(by_impact)
    sms = maybe_sms(by_impact, digest_name)
    print(json.dumps({"ok":True,"digest":digest_name,"counts":{k:len(v) for k,v in by_impact.items()},"sms":sms}))

if __name__ == "__main__":
    main()
