#!/usr/bin/env python3
import re, json, time, argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM  = ROOT / "memory"
CONF = MEM / "config"; CONF.mkdir(parents=True, exist_ok=True)
REM  = CONF / "reminders.json"
LOGD = MEM / "logs" / "reminders"; LOGD.mkdir(parents=True, exist_ok=True)

def parse_when(s: str) -> int:
    s = s.strip().lower()
    now = datetime.now(timezone.utc)
    # in Xs / Xm / Xh / Xd
    m = re.match(r"in\s+(\d+)\s*s(ec(ond)?s?)?$", s)
    if m: return int((now + timedelta(seconds=int(m.group(1)))).timestamp())
    m = re.match(r"in\s+(\d+)\s*m(in(ute)?s?)?$", s)
    if m: return int((now + timedelta(minutes=int(m.group(1)))).timestamp())
    m = re.match(r"in\s+(\d+)\s*h(our)?s?$", s)
    if m: return int((now + timedelta(hours=int(m.group(1)))).timestamp())
    m = re.match(r"in\s+(\d+)\s*d(ay)?s?$", s)
    if m: return int((now + timedelta(days=int(m.group(1)))).timestamp())
    # today HH:MM [am/pm]
    m = re.match(r"(today\s+)?(\d{1,2}):(\d{2})(\s*(am|pm))?$", s)
    if m:
        h = int(m.group(2)); mi = int(m.group(3)); ap = (m.group(5) or "").lower()
        if ap == "pm" and h < 12: h += 12
        if ap == "am" and h == 12: h = 0
        dt = now.replace(hour=h, minute=mi, second=0, microsecond=0)
        if dt.timestamp() < now.timestamp(): dt += timedelta(days=1)
        return int(dt.timestamp())
    # tomorrow HH:MM [am/pm]
    m = re.match(r"tomorrow\s+(\d{1,2}):(\d{2})(\s*(am|pm))?$", s)
    if m:
        h = int(m.group(1)); mi = int(m.group(2)); ap = (m.group(4) or "").lower()
        if ap == "pm" and h < 12: h += 12
        if ap == "am" and h == 12: h = 0
        dt = now.replace(hour=h, minute=mi, second=0, microsecond=0) + timedelta(days=1)
        return int(dt.timestamp())
    # absolute UTC: YYYY-MM-DD HH:MM
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})$", s)
    if m:
        y, mo, d, hh, mm = map(int, m.groups())
        dt = datetime(y, mo, d, hh, mm, tzinfo=timezone.utc)
        return int(dt.timestamp())
    raise SystemExit(f"Unable to parse --when: {s}")

def load_db():
    if REM.exists():
        try:
            d = json.loads(REM.read_text(encoding="utf-8"))
            if not isinstance(d, dict): return {"items": []}
            if "items" not in d or not isinstance(d["items"], list): d["items"] = []
            return d
        except Exception:
            return {"items": []}
    return {"items": []}

def save_db(d):
    tmp = REM.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(REM)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True, help="what to remind")
    ap.add_argument("--when", required=True, help="when (e.g., 'in 45s', 'in 5m', 'today 6:30pm', 'YYYY-MM-DD HH:MM' UTC)")
    ap.add_argument("--channel", default="log", choices=["log","twilio","both"])
    a = ap.parse_args()

    due_ts = parse_when(a.when)
    db = load_db()
    rid = f"r{int(time.time())}"
    db["items"].append({"id": rid, "text": a.text, "due_ts": int(due_ts), "channel": a.channel, "sent_ts": None})
    save_db(db)

    with open(LOGD / "reminder_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] scheduled id={rid} due_ts={due_ts} text={a.text}\n")
    print(f"OK scheduled id={rid} due_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(due_ts))}  {a.text}")

if __name__ == "__main__":
    main()
