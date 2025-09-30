#!/usr/bin/env python3
import argparse, yaml, re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def load_registry(path):
    with open(path) as f:
        return yaml.safe_load(f)

def parse_logs(logfile):
    entries = {}
    with open(logfile) as f:
        for line in f:
            m = re.match(r'Agent\s+(\d+):\s+(.*)', line)
            if m:
                agent_id, activity = m.groups()
                entries.setdefault(int(agent_id), []).append(activity.strip())
    return entries

def build_pdf(outpath, registry, logs):
    c = canvas.Canvas(outpath, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Consensus Project – 55 Agents Final Report")
    y -= 30

    for i in range(1, 56):
        agent_name = registry.get(f"Agent {i}", f"Agent {i} (Unnamed)")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{agent_name}")
        y -= 20
        c.setFont("Helvetica", 10)
        details = logs.get(i, ["No activity logged"])
        for d in details:
            if "CHANGED ROLE" in d.upper():
                c.setFillColor(colors.red)
            else:
                c.setFillColor(colors.black)
            c.drawString(70, y, f"- {d}")
            y -= 15
            if y < 100:
                c.showPage()
                y = height - 50
        y -= 10
    c.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--logs", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    reg = load_registry(args.registry)
    logs = parse_logs(args.logs)
    build_pdf(args.out, reg, logs)
    print(f"SUCCESS: Wrote report to {args.out}")
