#!/usr/bin/env python3
import re, subprocess, time, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM  = ROOT / "memory"
HB   = MEM / "logs" / "heartbeat" / "memory_absorption_heartbeat.log"
SYNC = MEM / "logs" / "github_sync" / "sync.log"
IDXF = MEM / "index" / "search_index.json"

def parse_ts(ts: str) -> int | None:
    fmts = ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S")
    for fmt in fmts:
        try:
            return int(time.mktime(time.strptime(ts, fmt)))
        except Exception:
            pass
    return None

def human_ago_from_ts(ts_utc: str) -> str:
    then = parse_ts(ts_utc)
    if then is None: return ""
    delta = max(0, int(time.time()) - then)
    if delta < 90: return f"{delta}s ago"
    mins = delta // 60
    if mins < 90: return f"{mins}m ago"
    hrs = mins // 60
    if hrs < 48: return f"{hrs}h ago"
    return f"{hrs//24}d ago"

def last_absorb():
    # Try heartbeat (scan last 200 lines for either known format)
    if HB.exists():
        lines = HB.read_text(encoding="utf-8", errors="ignore").splitlines()[-200:]
        for line in reversed(lines):
            m = re.match(r"\[(?P<ts>[^]]+)\]\s+indexed=(?P<idx>\d+).*?elapsed=(?P<sec>[\d\.]+)s", line)
            if m:
                ts = m.group("ts"); idx = m.group("idx"); sec = m.group("sec")
                print(f"Last absorption was {ts} ({human_ago_from_ts(ts)}), indexed {idx} files, took {sec}s.")
                return
            m2 = re.match(r"Last full memory absorption:\s+(?P<dt>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
            if m2:
                ts = m2.group("dt")
                idx = None
                if IDXF.exists():
                    try:
                        idx = json.loads(IDXF.read_text(encoding='utf-8')).get("total_files")
                    except Exception:
                        pass
                idx_txt = f", indexed ~{idx} files" if idx is not None else ""
                print(f"Last absorption was {ts} ({human_ago_from_ts(ts)}){idx_txt}.")
                return
    # Fallback: use index metadata
    if IDXF.exists():
        try:
            d = json.loads(IDXF.read_text(encoding="utf-8"))
            gen = d.get("generated_at")
            idx = d.get("total_files")
            if gen:
                ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(gen)))
                print(f"Last absorption (from index) was {ts} ({human_ago_from_ts(ts)}), indexed {idx} files.")
                return
        except Exception:
            pass
    print("No absorption heartbeat/index found.")

def sh(args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT, text=True).strip()

def last_github_update():
    try:
        sh(["git","fetch","origin"])
        out = sh(["git","log","-n","1","--date=iso-strict",
                  "--pretty=format:%H|%ad|%s","origin/v1.1-dev","--","memory"])
        h, when, subj = out.split("|",2)
        print(f"Last GitHub update to memory/ was commit {h[:9]} at {when} — {subj}.")
        return
    except Exception:
        pass
    if SYNC.exists():
        lines = [l for l in SYNC.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        for line in reversed(lines):
            if line.startswith("[") and "] " in line:
                ts = line.split("] ",1)[0].strip("[]")
                rest = line.split("] ",1)[1].strip()
                if re.fullmatch(r"[0-9a-f]{7,40}", rest):
                    print(f"Last GitHub update to memory/ was commit {rest[:9]} at {ts}Z.")
                    return
    print("No GitHub memory update found yet.")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--last-absorb", action="store_true")
    ap.add_argument("--last-github-update", action="store_true")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    if args.summary or (not args.last_absorb and not args.last_github_update):
        last_absorb(); last_github_update(); return
    if args.last_absorb: last_absorb()
    if args.last_github_update: last_github_update()

if __name__ == "__main__":
    main()
