#!/usr/bin/env python3
import sys, time, re
from pathlib import Path

HOME = Path("/home/rafa1215")
MEM  = HOME / "memory"
SYS  = MEM / "logs" / "system"

def fmt_ts(ts):
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(ts))
    except Exception:
        return str(ts)

def find_last_absorption():
    candidates = [
        SYS / "memory_manifest_autofix.json",
        SYS / "absorb.log",
        SYS / "absorption.log",
        SYS / "run_absorption.log",
        SYS / "report_master.log",
        SYS / "absorption.log",  # fallback heartbeat from absorber
    ]
    mtimes = [(pth, pth.stat().st_mtime) for pth in candidates if pth.exists()]
    best_mtime = max(mtimes, key=lambda x: x[1])[1] if mtimes else None

    # Parse timestamps from file tails if present
    for pth in candidates:
        if not pth.exists():
            continue
        try:
            tail = (pth.read_text(encoding="utf-8", errors="ignore").splitlines())[-200:]
            s = "\n".join(tail)
            m = re.findall(r"(20\d{2}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2})", s)
            if m:
                return f"Last absorption (parsed from {pth.name}): {m[-1]}"
        except Exception:
            pass

    if best_mtime:
        best_path = max(mtimes, key=lambda x: x[1])[0]
        return f"Last absorption (by mtime of {best_path.name}): {fmt_ts(best_mtime)}"
    return None

def find_next_calendar():
    # Placeholder until real calendar integration is wired
    return "[No calendar integration configured]"

def find_pool_laps_today():
    # Looks for a swim/fitness log entry today
    from datetime import datetime
    fit_dir = HOME / "memory" / "logs" / "fitness"
    today = datetime.now().strftime("%Y-%m-%d")
    if fit_dir.exists():
        for pth in sorted(fit_dir.glob("*.log"))[::-1]:
            try:
                t = pth.read_text(encoding="utf-8", errors="ignore")
                if today in t and ("laps" in t.lower() or "swim" in t.lower()):
                    return "Pool laps logged today (see fitness logs)."
            except Exception:
                pass
    return "No pool laps logged yet today."

def main():
    if len(sys.argv) < 2:
        print("[No results found for: ]")
        return
    q_raw = sys.argv[1]
    q = q_raw.strip().lower()

    # Absorption status
    if "last absorption" in q or "last absorption run" in q or "last absorb" in q:
        ans = find_last_absorption()
        print(ans if ans else "[No results found for: last absorption]")
        return

    # Calendar stub
    if "next calendar" in q or "next event" in q:
        print(find_next_calendar()); return

    # Pool laps today
    if "pool laps" in q and ("today" in q or "did i" in q or "have i" in q):
        print(find_pool_laps_today()); return

    # Fallback
    print(f"[No results found for: {q_raw}]")

if __name__ == "__main__":
    main()
