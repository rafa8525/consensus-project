#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Consensus System – Recursive Self-Improvement Engine (AGI Phase 3, Stable Build)
Author: Rafael / AI Consensus System
Purpose: Allow agents to benchmark, mutate, and evolve their own logic safely.
"""

import os
import json
import time
import random
import hashlib
import subprocess
from datetime import datetime, timezone

BASE_DIR = os.path.expanduser("~/consensus-project")
LOG_DIR = os.path.join(BASE_DIR, "memory/logs/agents/evolution")
os.makedirs(LOG_DIR, exist_ok=True)

AGENTS_DIR = os.path.join(BASE_DIR, "tools")
BACKUP_DIR = os.path.join(BASE_DIR, "archive/agent_backups")
os.makedirs(BACKUP_DIR, exist_ok=True)


def timestamp() -> str:
    """UTC timestamp, timezone-aware (Python 3.13 safe)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str):
    """Append message to daily log and echo to console."""
    log_path = os.path.join(LOG_DIR, f"self_improvement_{datetime.now(timezone.utc).date()}.md")
    with open(log_path, "a") as f:
        f.write(f"[{timestamp()}] {msg}\n")
    print(msg)


def benchmark_agent(agent_path: str) -> float:
    """Benchmark a script by timing a lightweight dry run."""
    try:
        start = time.time()
        subprocess.run(
            ["python3", agent_path, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        latency = time.time() - start
        score = max(0.1, 5.0 - latency)  # higher = faster
    except Exception:
        score = 0.0
    return round(score, 3)


def mutate_agent_logic(agent_path: str) -> str:
    """Create a small random mutation in the agent code."""
    with open(agent_path, "r") as f:
        code = f.read()

    lines = [ln for ln in code.splitlines()]
    if not lines:
        log(f"⚠️ Skipping {os.path.basename(agent_path)} — empty or unreadable.")
        return agent_path

    mutation_tag = f"# Mutation_{hashlib.md5(str(random.random()).encode()).hexdigest()[:6]}"
    insert_at = random.randint(0, max(0, len(lines) - 1))
    lines.insert(insert_at, mutation_tag)

    mutated_path = agent_path.replace(".py", f"_mutated_{random.randint(1000,9999)}.py")
    with open(mutated_path, "w") as f:
        f.write("\n".join(lines))
    return mutated_path


def select_best_variant(original: str, mutant: str, score_orig: float, score_mut: float):
    """Keep whichever performs better; archive the other."""
    try:
        if score_mut > score_orig:
            backup_name = os.path.basename(original).replace(".py", f"_{timestamp()}_old.py")
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            os.rename(original, backup_path)
            os.rename(mutant, original)
            log(f"✅ Replaced {os.path.basename(original)} with improved variant (score {score_mut} > {score_orig}).")
        else:
            if os.path.exists(mutant):
                os.remove(mutant)
            log(f"⚖️ Kept original {os.path.basename(original)} (score {score_orig} ≥ {score_mut}).")
    except Exception as e:
        log(f"❌ Error selecting variant for {os.path.basename(original)}: {e}")


def main():
    log("=== Recursive Self-Improvement Cycle Start ===")
    try:
        candidates = [
            f for f in os.listdir(AGENTS_DIR)
            if f.endswith(".py") and f != os.path.basename(__file__)
        ]
        if not candidates:
            log("⚠️ No agent files found for benchmarking.")
            return

        for agent_file in candidates:
            agent_path = os.path.join(AGENTS_DIR, agent_file)
            score_orig = benchmark_agent(agent_path)
            mutant_path = mutate_agent_logic(agent_path)
            if mutant_path == agent_path:
                continue
            score_mut = benchmark_agent(mutant_path)
            select_best_variant(agent_path, mutant_path, score_orig, score_mut)
            time.sleep(1)

    except Exception as e:
        log(f"❌ Unexpected failure: {e}")

    log("=== Cycle Complete ===")


if __name__ == "__main__":
    main()
