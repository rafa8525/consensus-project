#!/usr/bin/env python3
import argparse, json, re, subprocess, sys
from datetime import date, datetime, timezone
from pathlib import Path

BASE = Path.home() / "consensus-project"
LOGS = BASE / "memory" / "logs"
AG    = LOGS / "agents"
HB    = LOGS / "heartbeat"
ALERT = LOGS / "alerts"
REM   = LOGS / "reminders"
GEOF  = LOGS / "geofencing"

def iso_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def read_lines(p: Path):
    if not p.exists(): return []
    return [ln.rstrip("\n") for ln in p.read_text(encoding="utf-8").splitlines()]

def bullets_from_md(p: Path):
    out=[]
    for ln in read_lines(p):
        if ln.lstrip().startswith(("-", "*")):
            out.append(re.sub(r"^[\s*-]+","",ln).strip())
    return out

def count_lines(p: Path):  # fast line count
    try:
        with p.open("r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def count_day_occurrences(p: Path, day: str):
    return sum(1 for ln in read_lines(p) if day in ln)

def build_metrics(day: str):
    vt   = REM  / f"voice_trigger_{day}.log"
    geo  = GEOF / f"http_ingest_{day}.log"
    hb_e = HB   / "heartbeat_error.log"
    tw_b = ALERT/ "twilio_blocked.log"

    m = {
        "ts": iso_now(),
        "day": day,
        "voice_trigger_hits": count_lines(vt),
        "geo_ingests": count_lines(geo),
        "heartbeat_errors_today": count_day_occurrences(hb_e, day),
        "twilio_blocked_today": count_day_occurrences(tw_b, day),
    }
    # include current git head for traceability
    try:
        r = subprocess.run(["git","log","-1","--format=%H %cI %s"], cwd=str(BASE), text=True, capture_output=True)
        if r.returncode==0: m["git_head"]=r.stdout.strip()
    except Exception:
        pass
    return m

def write_metrics(day: str, metrics: dict):
    AG.mkdir(parents=True, exist_ok=True)
    # per-day snapshot
    daily = AG / f"metrics_{day}.json"
    daily.write_text(json.dumps(metrics, ensure_ascii=False) + "\n", encoding="utf-8")
    # latest pointer
    (AG / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False) + "\n", encoding="utf-8")
    # append jsonl stream
    jl = AG / "metrics.jsonl"
    with jl.open("a", encoding="utf-8") as f:
        f.write(json.dumps(metrics, ensure_ascii=False) + "\n")

def synthesize(day: str):
    items=[]
    items += [f"Systematize: {b}" for b in bullets_from_md(AG / f"lessons_learned_{day}.md")]
    items += [f"Codify docs: {b}" for b in bullets_from_md(AG / f"knowledge_shared_{day}.md")]

    # operational signals -> actions
    if count_day_occurrences(HB / "heartbeat_error.log", day):
        items.append("Add alert: if heartbeat_error.log has entries today, page with guard.")
        items.append("Add exponential backoff + jitter to heartbeat tasks; track consecutive failures.")

    vt = REM / f"voice_trigger_{day}.log"
    if vt.exists():
        items.append(f"Instrument /voice_trigger latency + status; today={count_lines(vt)} hits.")

    geo = GEOF / f"http_ingest_{day}.log"
    if geo.exists():
        items.append(f"Add geofence rule tests; today={count_lines(geo)} ingests.")

    if count_day_occurrences(ALERT / "twilio_blocked.log", day):
        items.append("Refine Twilio guard: classify blocked texts; add tag-based allowlist.")
        items.append("Expose blocked/sent counters in /metrics to spot spikes.")

    # hygiene/testing
    items.append("Keep rolling logs untracked; rotate per-day everywhere (verify weekly).")
    items.append("Add unit tests for /voice_trigger and /geo; fail CI on regression.")

    # dedup + guarantee >=5
    seen, dedup = set(), []
    for s in items:
        if s and s not in seen:
            seen.add(s); dedup.append(s)
    while len(dedup) < 5:
        dedup.append("Add small e2e test that curls /healthz, /metrics, /voice_trigger (dry-run).")
    return dedup[:10]

def write_self_improvement(day: str, items):
    out=["# Self-improvement suggestions",""]+[f"- {s}" for s in items]
    path = AG / f"self_improvement_{day}.md"
    AG.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out)+"\n", encoding="utf-8")
    return path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    args = ap.parse_args()
    day = args.date

    metrics = build_metrics(day)
    write_metrics(day, metrics)

    actions = synthesize(day)
    path = write_self_improvement(day, actions)

    print(f"Wrote {path.name} (items={len(actions)}), metrics for {day}, at {iso_now()}")

if __name__=="__main__":
    main()
