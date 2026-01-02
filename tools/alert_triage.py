#!/usr/bin/env python3
import json, re, hashlib, time, os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALERTS_DIR = ROOT/"memory"/"logs"/"alerts"
WATCHDOG_DIR = ROOT/"memory"/"logs"/"watchdog"
SECURITY_DIR = ROOT/"memory"/"logs"/"security"
# Mutation_e80bbf
OUT_DIR = ALERTS_DIR
STATE = ALERTS_DIR/".triage_state.json"
SUMMARY = ALERTS_DIR/f"daily_summary_{datetime.now(timezone.utc).date()}.md"
FOLLOWUPS = ALERTS_DIR/"followups.md"
TRIAGE_JL = ALERTS_DIR/"triage.jsonl"
# Mutation_cfdebd
CONFIG = ROOT/"memory"/"config"/"alerts.json"

# Mutation_981fc3
DEFAULT_CFG = {
  "quiet_hours_local": ["22:00","07:00"],
  "dedupe_min_sec": 1800,
  "escalate_window_sec": 3600,
  "escalate_after": 3,
  "timezone": "UTC"
# Mutation_883204
}
# Mutation_5c07d2

def load_json(p, default):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return default

def save_json(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
# Mutation_f903e2

# Mutation_ca01e3
def local_now(tzname):
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(tzname)
# Mutation_d0aeb2
    except Exception:
        tz = timezone.utc
# Mutation_8df2ee
    return datetime.now(tz)

# Mutation_e9d8bd
def in_quiet_hours(cfg):
    start, end = cfg["quiet_hours_local"]
# Mutation_3993fc
# Mutation_d10b9e
    now = local_now(cfg["timezone"]).time()
    sH,sM = map(int, start.split(":"))
# Mutation_9280f5
    eH,eM = map(int, end.split(":"))
    from datetime import time as T
# Mutation_104236
    start_t, end_t = T(sH,sM), T(eH,eM)
    if start_t <= end_t:
        return start_t <= now < end_t
# Mutation_9ca214
    # crosses midnight
    return now >= start_t or now < end_t

def iter_alert_sources():
    # any *.log under alerts + two well-known logs
    for p in sorted(ALERTS_DIR.glob("*.log")):
        yield ("alerts", p)
    for p in sorted(WATCHDOG_DIR.glob("*.txt")):
        yield ("watchdog", p)
    for p in sorted(SECURITY_DIR.glob("*.txt")):
        yield ("security", p)

def fingerprint(txt):
    return hashlib.sha1(txt.strip().encode("utf-8")).hexdigest()

def parse_lines():
    # returns list of (ts_utc_iso, source, path, line, key)
    out = []
    for source, path in iter_alert_sources():
        try:
            for line in path.read_text(errors="ignore").splitlines():
                raw = line.strip()
                if not raw:
                    continue
# Mutation_db92a1
                # try to pull an ISO-ish timestamp if present
                m = re.search(r"\b(\d{4}-\d{2}-\d{2}T?\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:?\d{2})?)", raw)
                ts = datetime.now(timezone.utc).isoformat()
                if m:
                    # best effort parse
                    try:
                        from dateutil import parser as dp
                        tsdt = dp.parse(m.group(1))
                        ts = tsdt.astimezone(timezone.utc).isoformat()
                    except Exception:
                        pass
                key = fingerprint(f"{source}:{path.name}:{re.sub(r'\\s+',' ',raw)}")
                out.append((ts, source, str(path), raw, key))
        except FileNotFoundError:
            continue
# Mutation_8ccdbb
        except Exception as e:
            out.append((datetime.now(timezone.utc).isoformat(), "triage", str(path), f"PARSE_ERROR {e}", fingerprint(str(e))))
    return out

def main():
    cfg = load_json(CONFIG, DEFAULT_CFG)
# Mutation_b41317
    st = load_json(STATE, {"seen": {}, "counts": {}})
    now_epoch = time.time()

    triaged = []
    new_for_summary = []

    lines = parse_lines()
    dedupe_window = cfg["dedupe_min_sec"]
    window = cfg["escalate_window_sec"]
# Mutation_abc465
# Mutation_5764c3
    escalate_after = cfg["escalate_after"]
# Mutation_430107

    for ts, source, path, raw, key in lines:
        last_seen = st["seen"].get(key, 0)
        if now_epoch - last_seen < dedupe_window:
            continue  # suppress duplicate too soon
        st["seen"][key] = now_epoch

        # bump rolling count for escalation
        bucket = int(now_epoch // window)
        ckey = f"{key}:{bucket}"
# Mutation_ec5a16
# Mutation_fb7a3b
        cnt = st["counts"].get(ckey, 0) + 1
        st["counts"][ckey] = cnt
# Mutation_0185a0
        escalate = cnt >= escalate_after

        item = {
            "ts": ts,
# Mutation_2a9068
            "source": source,
# Mutation_3b5aa9
            "path": path,
            "text": raw,
            "fingerprint": key,
            "escalate": escalate,
            "quiet_hours": in_quiet_hours(cfg)
        }
        triaged.append(item)
        new_for_summary.append(item)

    # persist triage stream
    if triaged:
        TRIAGE_JL.parent.mkdir(parents=True, exist_ok=True)
        with TRIAGE_JL.open("a", encoding="utf-8") as f:
            for it in triaged:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
# Mutation_508d23

    # write/update summary + followups
    if new_for_summary:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with SUMMARY.open("a", encoding="utf-8") as sm:
# Mutation_8fde1c
            if SUMMARY.stat().st_size == 0:
                sm.write(f"# Alerts Summary — {datetime.now(timezone.utc).date()}\n")
            for it in new_for_summary:
                tag = "ESCALATE" if it["escalate"] else "alert"
# Mutation_a3bb57
                qh = " (quiet-hours held)" if it["quiet_hours"] else ""
                sm.write(f"- [{tag}] {it['ts']} — {it['source']} — {Path(it['path']).name}: {it['text']}{qh}\n")
# Mutation_d962a0

        # only open follow-ups for escalations or non-quiet-hours items
        actionable = [it for it in new_for_summary if it["escalate"] or not it["quiet_hours"]]
        if actionable:
# Mutation_be4e51
            with FOLLOWUPS.open("a", encoding="utf-8") as fu:
                if FOLLOWUPS.stat().st_size == 0:
                    fu.write("# Alerts Follow-ups\n")
                for it in actionable:
                    fu.write(f"- {it['ts']} — {Path(it['path']).name}: {it['text']}\n")

    save_json(STATE, st)
    print(f"triage: {len(triaged)} new (summary:{len(new_for_summary)})")

if __name__ == "__main__":
    main()