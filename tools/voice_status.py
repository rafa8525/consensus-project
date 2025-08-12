#!/usr/bin/env python3
import os, re, subprocess, time, json, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM  = ROOT / "memory"
HB   = MEM / "logs" / "heartbeat" / "memory_absorption_heartbeat.log"
SYNC = MEM / "logs" / "github_sync" / "sync.log"
IDXF = MEM / "index" / "search_index.json"

def parse_ts_str(ts: str) -> int | None:
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try: return int(time.mktime(time.strptime(ts, fmt)))
        except Exception: pass
    return None

def human_ago_from_epoch(epoch: int) -> str:
    delta = max(0, int(time.time()) - int(epoch))
    if delta < 90: return f"{delta}s ago"
    mins = delta // 60
    if mins < 90: return f"{mins}m ago"
    hrs = mins // 60
    if hrs < 48: return f"{hrs}h ago"
    return f"{hrs//24}d ago"

def fmt_ts(epoch: int, tz_mode: str, tz_name: str) -> str:
    # tz_mode: "utc" or "local"; if local, use tz_name (default America/Los_Angeles)
    if tz_mode == "utc":
        return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(epoch))
    # local
    try:
        prev = os.environ.get("TZ")
        os.environ["TZ"] = tz_name
        if hasattr(time, "tzset"): time.tzset()
    except Exception: pass
    lt = time.localtime(epoch)
    abbr = time.tzname[lt.tm_isdst]
    out = time.strftime(f"%Y-%m-%d %H:%M:%S {abbr}", lt)
    # best-effort restore
    try:
        if 'prev' in locals():
            if prev is None: os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = prev
                if hasattr(time, "tzset"): time.tzset()
    except Exception: pass
    return out

def sh(args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT, text=True).strip()

def last_absorb(tz_mode: str, tz_name: str, brief: bool):
    # 1) Try heartbeat (scan backwards)
    if HB.exists():
        lines = HB.read_text(encoding="utf-8", errors="ignore").splitlines()[-200:]
        for line in reversed(lines):
            m = re.match(r"\[(?P<ts>[^]]+)\]\s+indexed=(?P<idx>\d+).*?elapsed=(?P<sec>[\d\.]+)s", line)
            if m:
                ts = m.group("ts"); idx = int(m.group("idx")); sec = m.group("sec")
                epoch = parse_ts_str(ts)
                if epoch is None: break
                if brief:
                    print(f"Absorbed {human_ago_from_epoch(epoch)} ({fmt_ts(epoch, tz_mode, tz_name)}), ~{idx} files.")
                else:
                    print(f"Last absorption was {fmt_ts(epoch, tz_mode, tz_name)} ({human_ago_from_epoch(epoch)}), indexed {idx} files, took {sec}s.")
                return
            m2 = re.match(r"Last full memory absorption:\s+(?P<dt>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
            if m2:
                ts = m2.group("dt")
                epoch = parse_ts_str(ts)
                approx = None
                if IDXF.exists():
                    try: approx = json.loads(IDXF.read_text(encoding='utf-8')).get("total_files")
                    except Exception: pass
                if epoch is None:
                    print("Absorption time recorded but unparsable."); return
                if brief:
                    extra = f", ~{approx} files" if approx is not None else ""
                    print(f"Absorbed {human_ago_from_epoch(epoch)} ({fmt_ts(epoch, tz_mode, tz_name)}{extra}).")
                else:
                    where = fmt_ts(epoch, tz_mode, tz_name)
                    if approx is not None:
                        print(f"Last absorption was {where} ({human_ago_from_epoch(epoch)}), indexed ~{approx} files.")
                    else:
                        print(f"Last absorption was {where} ({human_ago_from_epoch(epoch)}).")
                return
    # 2) Fallback: index metadata
    if IDXF.exists():
        try:
            d = json.loads(IDXF.read_text(encoding="utf-8"))
            gen = d.get("generated_at"); idx = d.get("total_files")
            if gen:
                epoch = int(gen)
                if brief:
                    print(f"Absorbed {human_ago_from_epoch(epoch)} ({fmt_ts(epoch, tz_mode, tz_name)}), ~{idx} files.")
                else:
                    print(f"Last absorption (from index) was {fmt_ts(epoch, tz_mode, tz_name)} ({human_ago_from_epoch(epoch)}), indexed {idx} files.")
                return
        except Exception: pass
    print("No absorption heartbeat/index found.")

def last_github_update(tz_mode: str, tz_name: str, brief: bool):
    try:
        sh(["git","fetch","origin"])
        out = sh(["git","log","-n","1","--date=unix","--pretty=format:%H|%ad|%s","origin/v1.1-dev","--","memory"])
        h, epoch, subj = out.split("|",2)
        epoch = int(epoch)
        if brief:
            print(f"GitHub updated {human_ago_from_epoch(epoch)} ({fmt_ts(epoch, tz_mode, tz_name)}) by {h[:9]}: {subj[:80]}")
        else:
            print(f"Last GitHub update to memory/ was commit {h[:9]} at {fmt_ts(epoch, tz_mode, tz_name)} — {subj}.")
        return
    except Exception:
        pass
    if SYNC.exists():
        lines = [l for l in SYNC.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        for line in reversed(lines):
            if line.startswith("[") and "] " in line:
                ts = line.split("] ",1)[0].strip("[]")
                h = line.split("] ",1)[1].strip()
                if re.fullmatch(r"[0-9a-f]{7,40}", h):
                    epoch = parse_ts_str(ts) or int(time.time())
                    if brief:
                        print(f"GitHub updated {human_ago_from_epoch(epoch)} ({fmt_ts(epoch, tz_mode, tz_name)}) by {h[:9]}")
                    else:
                        print(f"Last GitHub update to memory/ was commit {h[:9]} at {fmt_ts(epoch, tz_mode, tz_name)}.")
                    return
    print("No GitHub memory update found yet.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--last-absorb", action="store_true")
    ap.add_argument("--last-github-update", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--brief", action="store_true", help="short voice-friendly output")
    ap.add_argument("--tz", choices=["utc","local"], default="local")
    ap.add_argument("--tz-name", default="America/Los_Angeles")
    args = ap.parse_args()
    if args.summary or (not args.last_absorb and not args.last_github_update):
        last_absorb(args.tz, args.tz_name, args.brief)
        last_github_update(args.tz, args.tz_name, args.brief)
        return
    if args.last_absorb: last_absorb(args.tz, args.tz_name, args.brief)
    if args.last_github_update: last_github_update(args.tz, args.tz_name, args.brief)

if __name__ == "__main__":
    main()
