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
import fcntl

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
    """Execute a module and report success only after a clean exit."""
    try:
        mod = importlib.import_module(module_name)
        script_path = _script_path(module_name)

        if hasattr(mod, func_name):
            import inspect

            func = getattr(mod, func_name)
            required = [
                p
                for p in inspect.signature(func).parameters.values()
                if p.default is inspect.Parameter.empty
                and p.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            ]

            # Only call run() directly when it requires no arguments.
            if not required:
                result = func()

                if isinstance(result, int) and result != 0:
                    if module_name == "infrastructure_guardian" and result == 1:
                        log(
                            "⚠️ infrastructure_guardian reported warning status "
                            "(exit code 1); continuing without self-repair"
                        )
                        return True
                    log(
                        f"❌ {module_name}.{func_name} "
                        f"returned error code {result}"
                    )
                    trigger_repair(module_name)
                    return False

                log(f"✅ {module_name}.{func_name} executed successfully")
                return True

            log(
                f"ℹ️ {module_name}.{func_name} requires arguments; "
                "using script entrypoint instead"
            )

        # Modules whose run() requires arguments are executed through
        # their normal script/main entrypoint instead.
        if script_path:
            env = os.environ.copy()

            if module_name == "infrastructure_guardian":
                env["CONSENSUS_REPO_ROOT"] = BASE_DIR
                env["CONSENSUS_MEMORY_ROOT"] = os.path.join(BASE_DIR, "memory")

            result = subprocess.run(
                [sys.executable, script_path],
                cwd=BASE_DIR,
                env=env,
            )

            if result.returncode == 0:
                log(f"✅ Executed {script_path} successfully")
                return True

            if module_name == "infrastructure_guardian" and result.returncode == 1:
                log(
                    "⚠️ infrastructure_guardian reported warning status "
                    "(exit code 1); continuing without self-repair"
                )
                return True

            log(
                f"❌ {module_name} returned error code "
                f"{result.returncode}"
            )
            trigger_repair(module_name)
            return False

        log(f"⚠️ {module_name}: no usable run() or script entrypoint found")
        return False

    except Exception as exc:
        log(f"❌ Error running {module_name}: {exc}")
        trigger_repair(module_name)

        with open(LOG_FILE, "a") as f:
            traceback.print_exc(file=f)

        return False


def trigger_repair(failed_module: str):
    repair_script = os.path.join(TOOLS_DIR, "agent_self_repair_loop.py")
    if os.path.exists(repair_script):
        log(f"🩺 Invoking self-repair sequence for {failed_module} ...")
        subprocess.run([sys.executable, repair_script], cwd=BASE_DIR)
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
            "infrastructure_guardian",
            "log_repair_guard",
            "calendar_sync_guard_v3",
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
    # OS-level singleton lock.  The lock is automatically released when
    # this process exits, including crashes, so stale lock files are safe.
    MASTER_CONTROL_LOCK_FILE = "/tmp/ai_consensus_master_control_loop.lock"
    lock_fd = open(MASTER_CONTROL_LOCK_FILE, "w")

    try:
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("Master Control Loop already running; duplicate start rejected.")
        return 0

    lock_fd.write(str(os.getpid()))
    lock_fd.flush()

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
