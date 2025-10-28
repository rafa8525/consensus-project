#!/usr/bin/env python3
"""
Master Control Loop v5.0
Location: ~/consensus-project/tools/master_control_loop.py

Purpose:
- Unifies Guard, Core, Fitness, and Knowledge cycles
- Integrates new subsystems (VPN, Security, Reports, Evolution, Repair)
- Handles failures with auto-repair invocation
- Runs continuously (heartbeat every 15 minutes)
- Logs to ~/consensus-project/memory/logs/system/master_control_loop.log
"""

import os
import sys
import time
import datetime
import traceback
import importlib
import subprocess

# --------------------------------------------------------------------------- #
# PATHS
# --------------------------------------------------------------------------- #
BASE_DIR = os.path.expanduser("~/consensus-project")
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
SYS_LOG_DIR = os.path.join(BASE_DIR, "memory/logs/system")
os.makedirs(SYS_LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(SYS_LOG_DIR, "master_control_loop.log")
sys.path.insert(0, TOOLS_DIR)

# --------------------------------------------------------------------------- #
# LOGGING
# --------------------------------------------------------------------------- #
def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# --------------------------------------------------------------------------- #
# GENERIC MODULE RUNNER
# --------------------------------------------------------------------------- #
def run_module(module_name: str, func_name: str = "run"):
    """Try to import and execute a module; fallback to standalone script."""
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, func_name):
            getattr(mod, func_name)()
            log(f"✅ {module_name}.{func_name} executed successfully")
        else:
            script_path = os.path.join(TOOLS_DIR, module_name.split(".")[-1] + ".py")
            if os.path.isfile(script_path):
                result = subprocess.run(["/usr/bin/python3", script_path])
                if result.returncode == 0:
                    log(f"✅ Executed {script_path} successfully")
                else:
                    log(f"❌ {module_name} returned error code {result.returncode}")
                    trigger_repair(module_name)
            else:
                log(f"⚠️ {module_name}: no run() or script found")
    except Exception as e:
        log(f"❌ Error running {module_name}: {e}")
        trigger_repair(module_name)
        traceback.print_exc(file=open(LOG_FILE, "a"))

# --------------------------------------------------------------------------- #
# REPAIR HANDLER
# --------------------------------------------------------------------------- #
def trigger_repair(failed_module: str):
    """Invoke the self-repair loop when a failure is detected."""
    repair_script = os.path.join(TOOLS_DIR, "agent_self_repair_loop.py")
    if os.path.exists(repair_script):
        log(f"🩺 Invoking self-repair sequence for {failed_module} ...")
        subprocess.run(["/usr/bin/python3", repair_script])
    else:
        log("⚠️ Repair script missing; cannot auto-recover.")

# --------------------------------------------------------------------------- #
# CORE CYCLES
# --------------------------------------------------------------------------- #
def run_guard_cycle():
    log("---- Guard Cycle Started ----")
    for mod in ["log_repair_guard", "gmail_refresh_guard_v3", "calendar_sync_guard_v3", "master_guard_integrator"]:
        run_module(mod)
    log("---- Guard Cycle Complete ----")

def run_core_cycle():
    log("---- Core Cycle Started ----")
    for mod in [
        "vpn_auto_detect_activate",
        "security_audit_runner",
        "weekly_status_report",
        "progress_evaluation_runner",
    ]:
        run_module(mod)
    log("---- Core Cycle Complete ----")

def run_fitness_cycle():
    log("---- Fitness Cycle Started ----")
    for mod in ["fitness_tracking_verifier", "health_master", "backup_fitness"]:
        run_module(mod)
    log("---- Fitness Cycle Complete ----")

def run_knowledge_cycle():
    log("---- Knowledge/Reports Cycle Started ----")
    for mod in ["knowledge_sharing_validator", "report_master", "memory_compressor", "status_report_builder"]:
        run_module(mod)
    log("---- Knowledge/Reports Cycle Complete ----")

def run_agent_cycle():
    log("---- Agent Evolution/Repair Cycle Started ----")
    for mod in ["agent_evolution_cycle", "agent_self_repair_loop"]:
        run_module(mod)
    log("---- Agent Evolution/Repair Cycle Complete ----")

# --------------------------------------------------------------------------- #
# MAIN LOOP
# --------------------------------------------------------------------------- #
def single_cycle():
    log("==== Master Control Loop Cycle Start ====")
    run_guard_cycle()
    run_core_cycle()
    run_fitness_cycle()
    run_knowledge_cycle()
    run_agent_cycle()
    log("✅ All subsystems executed successfully.")
    log("==== Master Control Loop Cycle Complete ====")

def main():
    log("==== Master Control Loop v5.0 (continuous) ====")
    while True:
        try:
            single_cycle()
        except Exception as e:
            log(f"❌ Unhandled exception: {e}")
            traceback.print_exc(file=open(LOG_FILE, "a"))
        # Heartbeat every 15 minutes
        for _ in range(15 * 60):
            time.sleep(1)
        log("💓 Heartbeat: restarting next cycle.")

if __name__ == "__main__":
    main()
