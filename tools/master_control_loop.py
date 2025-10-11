#!/usr/bin/env python3
"""
Master Control Loop — AI Consensus System (v2025.10.09+VOICE)
Fully autonomous orchestrator for all system agents.
Includes emotion tracking, predictive task flow, recursive evolution,
and ChatGPT Voice synchronization for full historical awareness.

Author: Rafael Lymburner (AI Consensus System)
"""

import os, sys, datetime, time, subprocess, traceback

BASE = "/home/rafa1215/consensus-project"
TOOLS = f"{BASE}/tools"
LOG_DIR = f"{BASE}/memory/logs/system"
HEARTBEAT = f"{LOG_DIR}/heartbeat_master.log"
EVOLVE_FLAG = "--evolve" in sys.argv

# ---------- Utility Functions ---------- #

def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(HEARTBEAT, "a") as f:
        f.write(line + "\n")

def run_script(path, desc):
    try:
        start = time.time()
        subprocess.run(["python3", path], timeout=120, check=True)
        elapsed = round(time.time() - start, 2)
        log(f"✅ {desc} completed in {elapsed}s")
    except subprocess.TimeoutExpired:
        log(f"⚠️ Timeout running {desc}")
    except subprocess.CalledProcessError:
        log(f"❌ Error running {desc}")
    except Exception as e:
        log(f"❌ Exception in {desc}: {e}\n{traceback.format_exc()}")

# ---------- Core Autonomous Tasks ---------- #

def run_emotion_state_tracker():
    path = f"{TOOLS}/emotion_state_tracker.py"
    if os.path.exists(path):
        run_script(path, "Emotion State Tracker")

def run_predictive_task_flow():
    path = f"{TOOLS}/predictive_task_flow.py"
    if os.path.exists(path):
        run_script(path, "Predictive Task Flow")

def run_recursive_evolution():
    path = f"{TOOLS}/recursive_evolution_manager.py"
    if os.path.exists(path):
        run_script(path, "Recursive Evolution Manager")

# ---------- Existing Agent Invocations ---------- #

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

# ---------- Voice Awareness Integration ---------- #

def run_voice_context_update():
    """Ensure ChatGPT Voice always has full project knowledge and recent events."""
    voice_scripts = [
        ("voice_context_loader.py", "Voice Context Digest Builder"),
        ("generate_daily_state.py", "Voice Daily State Summary"),
    ]
    for fname, desc in voice_scripts:
        path = f"{TOOLS}/{fname}"
        if os.path.exists(path):
            run_script(path, desc)
        else:
            log(f"⚠️ Missing voice tool: {fname}")

# ---------- Control Flow ---------- #

def main():
    log("=== Master Control Loop Start ===")

    # 1. Emotional awareness before all scheduling
    run_emotion_state_tracker()

    # 2. Predictive task generation (proactive flow)
    run_predictive_task_flow()

    # 3. Standard agents (VPN, Fitness, Security, Summary)
    run_standard_agents()

    # 4. Recursive self-evolution (weekly or manual trigger)
    if EVOLVE_FLAG or datetime.datetime.today().weekday() == 6:  # Sunday
        run_recursive_evolution()

    # 5. Voice awareness — keeps ChatGPT Voice informed of all progress
    run_voice_context_update()

    log("=== Master Control Loop End ===\n")

if __name__ == "__main__":
    main()
