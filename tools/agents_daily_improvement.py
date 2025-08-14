#!/usr/bin/env python3
import argparse, json, re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE = Path.home() / "consensus-project"
AGENTS = BASE / "memory" / "logs" / "agents"
HB     = BASE / "memory" / "logs" / "heartbeat"
ALERTS = BASE / "memory" / "logs" / "alerts"
REM    = BASE / "memory" / "logs" / "reminders"
GEOF   = BASE / "memory" / "logs" / "geofencing"

def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def ensure_metrics_snapshot():
    """Create metrics.json from last line of metrics.jsonl if snapshot missing."""
    j  = AGENTS / "metrics.json"
    jl = AGENTS / "metrics.jsonl"
    if j.exists() or not jl.exists():
        return
    last = None
    with jl.open("r", encoding="utf-8") as f:
        for last in f:
            pass
    if last:
        j.write_text(last.strip() + "\n", encoding="utf-8")

def read_lines(p: Path):
    if not p.exists(): return []
    return [ln.rstrip("\n") for ln in p.read_text(encoding="utf-8").splitlines()]

def bullets_from_md(p: Path):
    out = []
    for ln in read_lines(p):
        if ln.lstrip().startswith(("-", "*")):
            out.append(re.sub(r"^[\s*-]+", "", ln).strip())
    return out

def count_today(p: Path, day: str) -> int:
    return sum(1 for ln in read_lines(p) if day in ln)

def synthesize(day: str):
    """Produce >=5 actionable items using available signals; never empty."""
    items = []

    # 1) Learnings → actions
    items += [f"Systematize: {b}" for b in bullets_from_md(AGENTS / f"lessons_learned_{day}.md")]
    items += [f"Codify docs: {b}" for b in bullets_from_md(AGENTS / f"knowledge_shared_{day}.md")]

    # 2) Heartbeat errors → reliability actions
    hb_err = HB / "heartbeat_error.log"
    if hb_err.exists() and count_today(hb_err, day):
        items.append("Add alert: if heartbeat_error.log has entries today, page with guard.")
        items.append("Add exponential backoff + jitter to heartbeat tasks; track consecutive failures.")

    # 3) Twilio guard → comms hygiene
    blocked = ALERTS / "twilio_blocked.log"
    if blocked.exists() and count_today(blocked, day):
        items.append("Refine Twilio guard: classify blocked texts; add tag-based allowlist.")
        items.append("Expose blocked/sent counters in /metrics to spot spikes.")

    # 4) Endpoint usage → observability
    vt = REM / f"voice_trigger_{day}.log"
    geo = GEOF / f"http_ingest_{day}.log"
    if vt.exists():
        n = sum(1 for _ in vt.open("r", encoding="utf-8"))
        items.append(f"Instrument /voice_trigger latency + status; today={n} hits.")
    if geo.exists():
        n = sum(1 for _ in geo.open("r", encoding="utf-8"))
        items.append(f"Add geofence rule tests; today={n} ingests.")

    # 5) Repo hygiene (always valuable)
    items.append("Keep rolling logs untracked; rotate per-day everywhere (done—verify weekly).")
    items.append("Add unit tests for /voice_trigger and /geo; fail CI on regression.")

    # Deduplicate and guarantee at least 5
    seen, dedup = set(), []
    for s in items:
        if s and s not in seen:
            seen.add(s); dedup.append(s)
    while len(dedup) < 5:
        dedup.append("Add small e2e test that curls /healthz, /metrics, /voice_trigger (dry-run).")
    return dedup[:10]

def write_self_improvement(day: str, items):
    AGENTS.mkdir(parents=True, exist_ok=True)
    out = ["# Self-improvement suggestions", ""] + [f"- {s}" for s in items]
    path = AGENTS / f"self_improvement_{day}.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    args = ap.parse_args()
    day = args.date

    ensure_metrics_snapshot()
    items = synthesize(day)
    path = write_self_improvement(day, items)
    print(f"Wrote {path} with {len(items)} items at {iso_now()}")

if __name__ == "__main__":
    main()
