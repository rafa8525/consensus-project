#!/usr/bin/env python3
"""
Master Control Loop — AI Consensus System (v2025.10.15+GEN)
------------------------------------------------------------
Full autonomous orchestrator for all system agents.

Includes:
  • Emotional awareness
  • Predictive task generation
  • Recursive evolution (weekly)
  • Monthly self-optimization (benchmark + priority tuning)
  • Predictive foresight (weekly)
  • Scenario simulation (monthly)
  • Self-generation (quarterly)
  • Voice synchronization

Author: Rafael Lymburner (AI Consensus System)
"""

import os, sys, datetime, time, subprocess, traceback

BASE = "/home/rafa1215/consensus-project"
TOOLS = f"{BASE}/tools"
LOG_DIR = f"{BASE}/memory/logs/system"
HEARTBEAT = f"{LOG_DIR}/heartbeat_master.log"
EVOLVE_FLAG = "--evolve" in sys.argv

# ---------- Utilities ---------- #

def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(HEARTBEAT, "a") as f:
        f.write(line + "\n")

def run_script(path, desc, timeout=180):
    try:
        start = time.time()
        subprocess.run(["python3", path], timeout=timeout, check=True)
        elapsed = round(time.time() - start, 2)
        log(f"✅ {desc} completed in {elapsed}s")
    except subprocess.TimeoutExpired:
        log(f"⚠️ Timeout running {desc}")
    except subprocess.CalledProcessError:
        log(f"❌ Error running {desc}")
    except Exception as e:
        log(f"❌ Exception in {desc}: {e}\n{traceback.format_exc()}")

# ---------- Core Agents ---------- #

def run_emotion_state_tracker():
    p = f"{TOOLS}/emotion_state_tracker.py"
    if os.path.exists(p): run_script(p, "Emotion State Tracker")

def run_predictive_task_flow():
    p = f"{TOOLS}/predictive_task_flow.py"
    if os.path.exists(p): run_script(p, "Predictive Task Flow")

def run_recursive_evolution():
    p = f"{TOOLS}/recursive_evolution_manager.py"
    if os.path.exists(p): run_script(p, "Recursive Evolution Manager")

def run_standard_agents():
    agents = [
        ("heartbeat_scheduler_loop.py", "Heartbeat Scheduler"),
        ("vpn_test_suite.py", "VPN Test Suite"),
        ("fitness_tracking_integrator.py", "Fitness Tracking Integrator"),
        ("security_audit_agent.py", "Security Audit Agent"),
        ("daily_summary_generator.py", "Daily Summary Generator"),
    ]
    for fname, desc in agents:
        path = f"{TOOLS}/{fname}"
        if os.path.exists(path):
            run_script(path, desc)

# ---------- Voice Awareness ---------- #

def run_voice_context_update():
    for fname, desc in [
        ("voice_context_loader.py", "Voice Context Digest Builder"),
        ("generate_daily_state.py", "Voice Daily State Summary"),
    ]:
        path = f"{TOOLS}/{fname}"
        if os.path.exists(path):
            run_script(path, desc)
        else:
            log(f"⚠️ Missing voice tool: {fname}")

# ---------- Self-Optimization (Monthly) ---------- #

def run_self_optimization():
    flag = os.path.join(LOG_DIR, "last_self_optimize.flag")
    now = datetime.datetime.now()

    if not os.path.exists(flag) or (
        now - datetime.datetime.fromtimestamp(os.path.getmtime(flag))
    ).days >= 30:
        bench = f"{TOOLS}/benchmark_agents.py"
        opti  = f"{TOOLS}/optimize_agent_priorities.py"
        if os.path.exists(bench): run_script(bench, "Agent Benchmark Suite")
        if os.path.exists(opti):  run_script(opti, "Agent Priority Optimizer")
        with open(flag, "w") as f: f.write(now.isoformat())
        log(f"🧠 Monthly self-optimization completed at {now}")
        run_scenario_simulation()
    else:
        log("ℹ️ Self-optimization not due yet (less than 30 days).")

# ---------- Predictive Foresight (Weekly / Sunday) ---------- #

def run_predictive_foresight():
    today = datetime.datetime.today().weekday()  # 6 = Sunday
    foresight = f"{TOOLS}/predictive_foresight_engine.py"
    if today == 6 and os.path.exists(foresight):
        run_script(foresight, "Predictive Foresight Engine")
        run_self_generation()   # <-- trigger quarterly self-generation
    else:
        log("ℹ️ Predictive foresight not scheduled for today.")

# ---------- Scenario Simulation (Monthly) ---------- #

def run_scenario_simulation():
    flag = os.path.join(LOG_DIR, "last_simulation.flag")
    now = datetime.datetime.now()
    if not os.path.exists(flag) or (
        now - datetime.datetime.fromtimestamp(os.path.getmtime(flag))
    ).days >= 30:
        sim = f"{TOOLS}/scenario_simulation_engine.py"
        if os.path.exists(sim):
            run_script(sim, "Scenario Simulation Engine")
            with open(flag, "w") as f: f.write(now.isoformat())
            log(f"🧩 Monthly scenario simulation executed at {now}")
    else:
        log("ℹ️ Scenario simulation not due yet (less than 30 days).")

# ---------- Self-Generation (Quarterly / Every 90 days) ---------- #

def run_self_generation():
    flag = os.path.join(LOG_DIR, "last_self_generation.flag")
    now = datetime.datetime.now()
    if EVOLVE_FLAG or not os.path.exists(flag) or (
        now - datetime.datetime.fromtimestamp(os.path.getmtime(flag))
    ).days >= 90:
        gen = f"{TOOLS}/self_generation_engine.py"
        if os.path.exists(gen):
            run_script(gen, "Self-Generation Engine")
            with open(flag, "w") as f: f.write(now.isoformat())
            log(f"🧬 Quarterly self-generation executed at {now}")
    else:
        log("ℹ️ Self-generation not due yet (less than 90 days).")

# ---------- Main Loop ---------- #

def main():
    log("=== Master Control Loop Start ===")

    run_emotion_state_tracker()
    run_predictive_task_flow()
    run_standard_agents()

    if EVOLVE_FLAG or datetime.datetime.today().weekday() == 6:
        run_recursive_evolution()
        run_predictive_foresight()

    run_self_optimization()
    run_voice_context_update()

    log("=== Master Control Loop End ===\n")

if __name__ == "__main__":
    main()
