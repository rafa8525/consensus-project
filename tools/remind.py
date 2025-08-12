#!/usr/bin/env python3
import re, json, time, argparse
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parent.parent
MEM  = ROOT / "memory"
CONF = MEM / "config"; CONF.mkdir(parents=True, exist_ok=True)
REM  = CONF / "reminders.json"
LOGD = MEM / "logs" / "reminders"; LOGD.mkdir(parents=True, exist_ok=True)

def parse_when(s: str) -> int:
    s = s.strip().lower()
    now = datetime.utcnow()
    # in Xm / Xh / Xd
    m = re.match(r"in\s+(\d+)\s*m(in(ute)?s?)?$", s)
    if m: return int((now + timedelta(minutes=int(m.group(1)))).timestamp())
    m = re.match(r"in\s+(\d+)\s*h(our)?s?$", s)
    if m: return int((now + timedelta(hours=int(m.group(1)))).timestamp())
    m = re.match(r"in\s+(\d+)\s*d(ay)?s?$", s)
    if m: return int((now + timedelta(days=int(m.group(1)))).timestamp())
    # today HH:MM
    m = re.match(r"(today\s+)?(\d{1,2}):(\d{2})(\s*(am|pm))?$", s)
    if m:
        h = int(m.group(2)); mi=int(m.group(3)); ap=(m.group(5) or "").lower()
        if ap == "pm" and h<12: h+=12
        if ap == "am" and h==12: h=0
        dt = now.replace(hour=h, minute=mi, second=0, microsecond=0)
        if dt.timestamp() < now.timestamp(): dt += timedelta(days=1)
        return int(dt.timestamp())
    # tomorrow HH:MM
    m = re.match(r"tomorrow\s+(\d{1,2}):(\d{2})(\s*(am|pm))?$", s)
    if m:
        h = int(m.group(1)); mi=int(m.group(2)); ap=(m.group(4) or "").lower()
        if ap == "pm" and h<12: h+=12
        if ap == "am" and h==12: h=0
        dt = now.replace(hour=h, minute=mi, second=0, microsecond=0) + timedelta(days=1)
        return int(dt.timestamp())
    # absolute: YYYY-MM-DD HH:MM (UTC)
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})$", s)
    if m:
        y,mo,d,hh,mm = map(int, m.groups())
        dt = datetime(y,mo,d,hh,mm)
        return int(dt.timestamp())
    raise ValueError(f"Unable to parse time: {s}")

def load_reminders():
    if REM.exists():
        try: return json.loads(REM.read_text(encoding="utf-8"))
        except Exception: return {"items":[]}
    return {"items":[]}

def save_reminders(d):
    tmp = REM.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(REM)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True, help="what to remind")
    ap.add_argument("--when", required=True, help="when (natural: 'in 30m', 'today 6pm', 'tomorrow 9:15', or 'YYYY-MM-DD HH:MM' UTC)")
    ap.add_argument("--channel", default="log", choices=["log","twilio","both"])
    args = ap.parse_args()
    due_ts = parse_when(args.when)

    db = load_reminders()
    rid = f"r{int(time.time())}"
    item = {"id": rid, "text": args.text, "due_ts": due_ts, "channel": args.channel, "sent_ts": None}
    db["items"].append(item); save_reminders(db)

    with open(LOGD/"reminder_log.txt","a",encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}] scheduled id={rid} when={args.when} due_ts={due_ts} text={args.text}\n")
    print(f"OK scheduled id={rid} due_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(due_ts))} text={args.text}")

if __name__ == "__main__":
    main()
