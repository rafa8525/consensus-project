#!/usr/bin/env python3
"""
Master Control Loop v5.1
Location: ~/consensus-project/tools/master_control_loop.py

Purpose:
- Unifies Guard, Core, Fitness, and Knowledge cycles
- Integrates VPN, Security, Reports, Evolution, Repair, and Continuity Guardian
- Handles failures with auto-repair invocation
- Runs continuously (heartbeat every 15 minutes)
- Logs truthful per-cycle success/failure status
"""

import os
import sys
import time
import datetime
import traceback
import importlib
import subprocess

BASE_DIR = os.path.expanduser("~/consensus-project")
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
SYS_LOG_DIR = os.path.join(BASE_DIR, "memory/logs/system")
os.makedirs(SYS_LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(SYS_LOG_DIR, "master_control_loop.log")
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, AGENTS_DIR)


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def _script_path(module_name: str):
    filename = module_name.split(".")[-1] + ".py"
    for root in (TOOLS_DIR, AGENTS_DIR):
        candidate = os.path.join(root, filename)
        if os.path.isfile(candidate):
            return candidate
    return None


def run_module(module_name: str, func_name: str = "run") -> bool:
    """Execute a module and return True only when the task actually exits cleanly."""
    try:
        mod = importlib.import_module(module_name)
        script_path = _script_path(module_name)

        if hasattr(mod, func_name):
            import inspect
            func = getattr(mod, func_name)
            required = [
                p for p in inspect.signature(func).parameters.values()
                if p.default is inspect.Parameter.empty
                and p.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            ]

            if not required:
                result = func()
                if isinstance(result, int) and result != 0:
                    log(f"❌ {module_name}.{func_name} returned error code {result}")
                    trigger_repair(module_name)
                    return False
                log(f"✅ {module_name}.{func_name} executed successfully")
                return True

        if script_path:
            result = subprocess.run(["/usr/bin/python3", script_path])
            if result.returncode == 0:
                log(f"✅ Executed {script_path} successfully")
                return True
            log(f"❌ {module_name} returned error code {result.returncode}")
            trigger_repair(module_name)
            return False

        log(f"⚠️ {module_name}: no callable run() or script found")
        return False
    except Exception as e:
        log(f"❌ Error running {module_name}: {e}")
        trigger_repair(module_name)
        with open(LOG_FILE, "a") as f:
            traceback.print_exc(file=f)
        return False


def trigger_repair(failed_module: str):
    repair_script = os.path.join(TOOLS_DIR, "agent_self_repair_loop.py")
    if os.path.exists(repair_script):
        log(f"🩺 Invoking self-repair sequence for {failed_module} ...")
        subprocess.run(["/usr/bin/python3", repair_script])
    else:
        log("⚠️ Repair script missing; cannot auto-recover.")


def run_group(label: str, modules: list[str]) -> bool:
    log(f"---- {label} Started ----")
    results = [run_module(mod) for mod in modules]
    ok = all(results)
    log(f"---- {label} Complete ({'PASS' if ok else 'FAIL'}) ----")
    return ok


def run_guard_cycle():
    return run_group(
        "Guard Cycle",
        [
            "continuity_guardian_agent",
            "log_repair_guard",
            "gmail_refresh_guard_v3",
            "calendar_sync_guard_v3",
            "master_guard_integrator",
        ],
    )


def run_core_cycle():
    return run_group(
        "Core Cycle",
        [
            "vpn_auto_detect_activate",
            "security_audit_runner",
            "weekly_status_report",
            "progress_evaluation_runner",
        ],
    )


def run_fitness_cycle():
    return run_group(
        "Fitness Cycle",
        ["fitness_tracking_verifier", "health_master", "backup_fitness"],
    )


def run_knowledge_cycle():
    return run_group(
        "Knowledge/Reports Cycle",
        ["knowledge_sharing_validator", "report_master", "memory_compressor", "status_report_builder"],
    )


def run_agent_cycle():
    return run_group(
        "Agent Evolution/Repair Cycle",
        ["agent_evolution_cycle", "agent_self_repair_loop"],
    )


def single_cycle():
    log("==== Master Control Loop Cycle Start ====")
    results = [
        run_guard_cycle(),
        run_core_cycle(),
        run_fitness_cycle(),
        run_knowledge_cycle(),
        run_agent_cycle(),
    ]
    if all(results):
        log("✅ All subsystems executed successfully.")
    else:
        failed = sum(1 for result in results if not result)
        log(f"❌ Master Control Loop cycle completed with {failed} failed subsystem group(s).")
    log("==== Master Control Loop Cycle Complete ====")
    return all(results)


def main():
    log("==== Master Control Loop v5.1 (continuous + continuity guardian) ====")
    while True:
        try:
            single_cycle()
        except Exception as e:
            log(f"❌ Unhandled exception: {e}")
            with open(LOG_FILE, "a") as f:
                traceback.print_exc(file=f)
        for _ in range(15 * 60):
            time.sleep(1)
        log("💓 Heartbeat: restarting next cycle.")


if __name__ == "__main__":
    main()
