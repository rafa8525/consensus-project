#!/usr/bin/env python3
import os
import datetime
import matplotlib.pyplot as plt

BASE_DIR = "/home/rafa1215/consensus-project/memory"
DASHBOARD_DIR = os.path.join(BASE_DIR, "logs/dashboard")
CHARTS_DIR = os.path.join(DASHBOARD_DIR, "charts")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

os.makedirs(CHARTS_DIR, exist_ok=True)

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] DASHBOARD-CHARTS: {status}\n")

def plot_metric(name, values, dates):
    try:
        plt.figure(figsize=(6,4))
        plt.plot(dates, values, marker="o")
        plt.title(f"{name} Trend")
        plt.xlabel("Date")
        plt.ylabel(name)
        plt.grid(True)
        out_path = os.path.join(CHARTS_DIR, f"{name.lower()}_trend.png")
        plt.savefig(out_path)
        plt.close()
        return out_path
    except Exception as e:
        heartbeat_log(f"ERROR plotting {name}: {e}")
        return None

def generate_charts():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    summary_file = os.path.join(CHARTS_DIR, f"charts_summary_{ts}.md")

    # Placeholder simulated values
    dates = [f"Day-{i}" for i in range(1,6)]

    vpn_latency = [120, 95, 140, 110, 100]   # ms
    steps = [8000, 9500, 10200, 8700, 11000]
    bills = [200, 220, 210, 205, 215]        # $
    agi_scores = [65, 70, 68, 72, 75]

    outputs = []
    outputs.append(plot_metric("VPN Latency (ms)", vpn_latency, dates))
    outputs.append(plot_metric("Steps", steps, dates))
    outputs.append(plot_metric("Bills ($)", bills, dates))
    outputs.append(plot_metric("AGI Score", agi_scores, dates))

    with open(summary_file, "w") as f:
        f.write(f"# Dashboard Charts {ts}\n\n")
        for o in outputs:
            if o:
                f.write(f"![Chart]({o})\n\n")

    heartbeat_log("SUCCESS: Charts generated")
    return summary_file

if __name__ == "__main__":
    # Only run on Mondays
    if datetime.datetime.now().weekday() != 0:
        heartbeat_log("INFO: Charts skipped (not Monday)")
        exit(0)

    try:
        summary = generate_charts()
        print(f"Charts summary saved: {summary}")
    except Exception as e:
        heartbeat_log(f"ERROR: Chart generation failed — {e}")
