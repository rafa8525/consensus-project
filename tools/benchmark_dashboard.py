#!/usr/bin/env python3
import os
import datetime

BASE_DIR = "/home/rafa1215/consensus-project/memory"
DASHBOARD_DIR = os.path.join(BASE_DIR, "logs/dashboard")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

os.makedirs(DASHBOARD_DIR, exist_ok=True)

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] DASHBOARD: {status}\n")

def read_tail(path, lines=5):
    if not os.path.exists(path):
        return f"(missing: {path})"
    try:
        with open(path, "r") as f:
            return "".join(f.readlines()[-lines:]).strip()
    except Exception as e:
        return f"(error reading {path}: {e})"

def generate_dashboard():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    out_file = os.path.join(DASHBOARD_DIR, f"dashboard_{ts}.md")

    sections = {
        "VPN": os.path.join(BASE_DIR, "logs/vpn/vpn_log.md"),
        "Fitness": os.path.join(BASE_DIR, "logs/fitness/fitness_daily_summary.md"),
        "Security": os.path.join(BASE_DIR, "logs/security"),
        "Finance": os.path.join(BASE_DIR, "logs/finance"),
        "Media": os.path.join(BASE_DIR, "logs/media"),
        "AGI Simulation": os.path.join(BASE_DIR, "logs/agi"),
        "Progress": os.path.join(BASE_DIR, "logs/progress"),
    }

    with open(out_file, "w") as f:
        f.write(f"# Weekly Benchmark Dashboard — {ts}\n\n")
        for name, path in sections.items():
            f.write(f"## {name}\n")
            if os.path.isdir(path):
                # Summarize last file in directory
                files = sorted([os.path.join(path, p) for p in os.listdir(path)])
                if files:
                    f.write(read_tail(files[-1], 10) + "\n\n")
                else:
                    f.write("(no entries)\n\n")
            else:
                f.write(read_tail(path, 10) + "\n\n")

    heartbeat_log("SUCCESS: Dashboard generated")
    return out_file

if __name__ == "__main__":
    # Only run on Mondays
    if datetime.datetime.now().weekday() != 0:
        heartbeat_log("INFO: Dashboard skipped (not Monday)")
        exit(0)

    try:
        dashboard = generate_dashboard()
        print(f"Dashboard saved: {dashboard}")
    except Exception as e:
        heartbeat_log(f"ERROR: Dashboard generation failed — {e}")
