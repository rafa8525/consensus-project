#!/usr/bin/env python3
import re, subprocess, time, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM  = ROOT / "memory"
HB   = MEM / "logs" / "heartbeat" / "memory_absorption_heartbeat.log"
SYNC = MEM / "logs" / "github_sync" / "sync.log"

def human_ago(ts_utc):
    try:
        now = int(time.time())
        then = int(time.mktime(time.strptime(ts_utc, "%Y-%m-%dT%H:%M:%SZ")))
        delta = max(0, now - then)
        mins = delta // 60; hrs = mins // 60
        if delta < 90: return f"{delta}s ago"
        if mins < 90:  return f"{mins}m ago"
        if hrs < 48:   return f"{hrs}h ago"
        days = hrs // 24
        return f"{days}d ago"
    except Exception:
        return ""

def last_absorb():
    if not HB.exists():
        print("No absorption heartbeat found.")
        return
    line = HB.read_text(encoding="utf-8", errors="ignore").strip().splitlines()[-1]
    m = re.match(r"\[(?P<ts>[^]]+)\]\s+indexed=(?P<idx>\d+).*elapsed=(?P<sec>[\d\.]+)s", line)
    if not m:
        print("Heartbeat present but unparsable.")
        return
    ts = m.group("ts"); idx = m.group("idx"); sec = m.group("sec")
    print(f"Last absorption was {ts} ({human_ago(ts)}), indexed {idx} files, took {sec}s.")

def sh(args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT, text=True).strip()

def last_github_update():
    # Prefer authoritative git history on remote
    try:
        sh(["git","fetch","origin"])
        out = sh(["git","log","-n","1","--date=iso-strict",
                  "--pretty=format:%H|%ad|%s","origin/v1.1-dev","--","memory"])
        h, when, subj = out.split("|",2)
        print(f"Last GitHub update to memory/ was commit {h[:9]} at {when} — {subj}.")
        return
    except Exception:
        pass
    # Fallback to our sync log
    if SYNC.exists():
        lines = [l for l in SYNC.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        # Find the last commit line: "[ts] <hash>"
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
        last_absorb()
        last_github_update()
        return
    if args.last_absorb: last_absorb()
    if args.last_github_update: last_github_update()

if __name__ == "__main__":
    main()
