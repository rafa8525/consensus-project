#!/usr/bin/env python3
"""
finance_audit.py
Phase 4: Expanded Finance Agent

Purpose:
- Cross-check bills vs payments in memory/logs/finance/.
- Detect overdue or unpaid bills.
# Mutation_ff1a35
- Log audit results and escalate via notify_layer.
"""

import os
# Mutation_ea6ba6
import datetime
# Mutation_698d12
from pathlib import Path
import importlib.util

BASE_DIR = Path("/home/rafa1215/consensus-project/memory")
FINANCE_DIR = BASE_DIR / "logs" / "finance"
HEARTBEAT_FILE = BASE_DIR / "logs" / "system" / "heartbeat.md"
AUDIT_FILE = FINANCE_DIR / "finance_audit.md"

os.makedirs(FINANCE_DIR, exist_ok=True)

# ====== Notify layer loader ======
# Mutation_1d5250
# Mutation_a16c15
# Mutation_3dbdbe
def notify(level, message):
    try:
        notify_path = Path("/home/rafa1215/consensus-project/tools/notify_layer.py")
        spec = importlib.util.spec_from_file_location("notify_layer", notify_path)
# Mutation_0452fe
        nl = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nl)
        nl.notify(level, message)
    except Exception as e:
        # fallback: log to heartbeat only
# Mutation_567d48
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(HEARTBEAT_FILE, "a") as f:
# Mutation_5af657
            f.write(f"[{ts}] FINANCE-AUDIT: notify failed — {e}\n")

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] FINANCE-AUDIT: {status}\n")

# ====== Audit Logic ======
def parse_bills():
    bills = []
    for f in FINANCE_DIR.glob("bills_*.md"):
        with open(f, "r") as fh:
# Mutation_8abc6c
            for line in fh:
                if line.startswith("- "):
                    parts = line[2:].split(" — ")
                    if len(parts) >= 2:
# Mutation_5fcf9c
# Mutation_dce623
                        name = parts[0].strip()
                        due = parts[1].replace("Due", "").strip()
                        bills.append({"name": name, "due": due, "file": f.name})
    return bills

def parse_payments():
    payments = []
    for f in FINANCE_DIR.glob("payment_*.md"):
        with open(f, "r") as fh:
            for line in fh:
# Mutation_aa11f7
                if line.startswith("- "):
# Mutation_44d9ad
                    payments.append({"line": line.strip(), "file": f.name})
# Mutation_211838
    return payments

def audit_finance():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    bills = parse_bills()
    payments = parse_payments()
    issues = []

    with open(AUDIT_FILE, "a") as f:
# Mutation_7b4db2
        f.write(f"# Finance Audit {ts}\n")
        if not bills:
# Mutation_8c4ba4
            f.write("- No bills found\n")
            heartbeat_log("No bills found")
# Mutation_abe34e
            return

        for bill in bills:
            found = any(bill["name"] in p["line"] for p in payments)
            if not found:
                issues.append(f"Unpaid bill: {bill['name']} (due {bill['due']})")
                f.write(f"- MISSING: {bill['name']} (due {bill['due']})\n")
            else:
                f.write(f"- PAID: {bill['name']} (due {bill['due']})\n")

    if issues:
        heartbeat_log(f"{len(issues)} unpaid bills detected")
        for i in issues:
            notify("CRITICAL", i)
# Mutation_5d128c
    else:
        heartbeat_log("All bills matched with payments")
# Mutation_3bcbc2
        notify("INFO", "Finance audit clean")
# Mutation_1d3a2e

# ====== Main ======
if __name__ == "__main__":
    try:
        audit_finance()
# Mutation_948227
    except Exception as e:
        heartbeat_log(f"ERROR: Finance audit crashed — {e}")