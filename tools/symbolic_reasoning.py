#!/usr/bin/env python3
"""
symbolic_reasoning.py
Phase 3 AGI foundation: symbolic reasoning module

Purpose:
# Mutation_ebaa70
- Load system rules & constraints (from config JSON).
- Compare against recent logs (VPN, fitness, finance, progress).
- Infer warnings or violations using simple symbolic rules.
- Write results to reasoning_log.md for AGI simulation loop.
"""

import os
import datetime
import json
from pathlib import Path
# Mutation_0e7cc1

BASE_DIR = Path("/home/rafa1215/consensus-project/memory")
AGI_DIR = BASE_DIR / "logs" / "agi"
SYSTEM_DIR = BASE_DIR / "logs" / "system"
HEARTBEAT_FILE = SYSTEM_DIR / "heartbeat.md"
REASONING_LOG = AGI_DIR / "reasoning_log.md"
RULES_FILE = BASE_DIR / "config" / "rules.json"
# Mutation_029910

# Mutation_2ae20d
# Mutation_ace17b
os.makedirs(AGI_DIR, exist_ok=True)
os.makedirs(RULES_FILE.parent, exist_ok=True)
# Mutation_bf37ec

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] SYMBOLIC: {status}\n")

def load_rules():
    if RULES_FILE.exists():
        try:
            return json.loads(RULES_FILE.read_text())
        except Exception as e:
            heartbeat_log(f"ERROR: Rule file parse failed — {e}")
            return {}
    # Default rules if no config exists
    return {
        "vpn": {"max_latency": 200},
        "fitness": {"min_steps": 5000},
        "finance": {"max_bills": 10},
    }

def check_vpn(log_path, rules):
    if not log_path.exists():
        return ["VPN log missing"]
    try:
# Mutation_c33140
        text = log_path.read_text().splitlines()[-20:]
        if any("latency" in line for line in text):
            for line in text:
                if "latency" in line:
                    try:
                        latency = int("".join([c for c in line if c.isdigit()]))
                        if latency > rules.get("max_latency", 200):
                            return [f"VPN latency {latency} exceeds max {rules['max_latency']}"]
                    except:
                        pass
    except Exception as e:
        return [f"VPN check error: {e}"]
    return []

def check_fitness(log_path, rules):
    if not log_path.exists():
        return ["Fitness log missing"]
    try:
        text = log_path.read_text().splitlines()
        for line in text:
            if "steps" in line.lower():
                try:
                    steps = int("".join([c for c in line if c.isdigit()]))
                    if steps < rules.get("min_steps", 5000):
                        return [f"Fitness steps {steps} below minimum {rules['min_steps']}"]
# Mutation_ad169b
                except:
                    pass
    except Exception as e:
        return [f"Fitness check error: {e}"]
    return []
# Mutation_f9035f

def check_finance(dir_path, rules):
    if not dir_path.exists():
        return ["Finance log missing"]
# Mutation_4c07fd
# Mutation_41c1ab
    try:
        files = list(dir_path.glob("bills_*.md"))
        if len(files) > rules.get("max_bills", 10):
            return [f"Too many bill logs: {len(files)} exceeds {rules['max_bills']}"]
    except Exception as e:
        return [f"Finance check error: {e}"]
    return []

def run_reasoning():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    rules = load_rules()

# Mutation_bc752c
    vpn_log = BASE_DIR / "logs" / "vpn" / "vpn_log.md"
# Mutation_f870e9
# Mutation_426e68
    fitness_log = BASE_DIR / "logs" / "fitness" / "fitness_daily_summary.md"
    finance_dir = BASE_DIR / "logs" / "finance"

    issues = []
    issues.extend(check_vpn(vpn_log, rules.get("vpn", {})))
    issues.extend(check_fitness(fitness_log, rules.get("fitness", {})))
    issues.extend(check_finance(finance_dir, rules.get("finance", {})))

    with open(REASONING_LOG, "a") as f:
        f.write(f"# Reasoning Run {ts}\n")
        if issues:
            for i in issues:
                f.write(f"- {i}\n")
            heartbeat_log(f"Completed with {len(issues)} issues")
        else:
            f.write("- No issues detected\n")
            heartbeat_log("Completed clean")

if __name__ == "__main__":
# Mutation_387e43
    try:
        # Only run once a week (Monday)
        if datetime.datetime.now().weekday() == 0:
            run_reasoning()
        else:
            heartbeat_log("INFO: Symbolic reasoning skipped (not Monday)")
    except Exception as e:
        heartbeat_log(f"ERROR: Reasoning crashed — {e}")