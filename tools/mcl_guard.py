#!/usr/bin/env python3
"""
MCL Guard — Supervisor and Voice Persistence Check
Location: /home/rafa1215/consensus-project/tools/mcl_guard.py

Features
- Heartbeat logging to ~/memory/logs/system/mcl_guard_heartbeat.log
- Voice health check against /health and /voice_trigger (uses VOICE_TOKEN from ~/reminder-api/.env)
- Automatic WSGI reload on repeated voice failure
- Lightweight scheduled runners for project tools (idempotent)
- One-shot or loop mode (MCL_ONESHOT=true runs once and exits)
"""

import os
import sys
import time
import json
import traceback
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError

# -------- Paths --------
HOME = Path(os.path.expanduser("~"))
ROOT = HOME / "consensus-project"
TOOLS = ROOT / "tools"
LOG_DIR = HOME / "memory" / "logs" / "system"
LOG_DIR.mkdir(parents=True, exist_ok=True)

HEARTBEAT = LOG_DIR / "mcl_guard_heartbeat.log"
ERRORS = LOG_DIR / "mcl_guard_errors.log"
STATUS = LOG_DIR / "mcl_guard_status.log"

# -------- Config (env-overridable) --------
VOICE_HOST = os.environ.get("VOICE_HOST", "https://rafa1215.pythonanywhere.com")
HEALTH_URL = os.environ.get("VOICE_HEALTH_URL", f"{VOICE_HOST}/health")
VOICE_URL = os.environ.get("VOICE_TRIGGER_URL", f"{VOICE_HOST}/voice_trigger")
WSGI_PATH = os.environ.get("WSGI_PATH", "/var/www/rafa1215_pythonanywhere_com_wsgi.py")
VOICE_ENV = HOME / "reminder-api" / ".env"
VOICE_ENABLED = os.environ.get("VOICE_ENABLED", "true").lower() == "true"
RETRY_SLEEP = int(os.environ.get("VOICE_RETRY_SLEEP", "4"))
LOOP_SLEEP = int(os.environ.get("MCL_LOOP_SLEEP", "60"))  # seconds between cycles in loop mode
ONESHOT = os.environ.get("MCL_ONESHOT", "false").lower() == "true"

# Default tasks (safe, quick). You can add/remove entries to match your install.
# Each task is a dict: {"every_s": seconds_between_runs}
TASKS = {
    "kb_smoke_test.py": {"every_s": 60 * 60},             # hourly
    "knowledge_share_kpi.py": {"every_s": 60 * 60},       # hourly
    "fitness_audit.py": {"every_s": 6 * 60 * 60},         # 6-hourly
    "vpn_test_runner.py": {"every_s": 24 * 60 * 60},      # daily
    "publish_status_report.py": {"every_s": 24 * 60 * 60},
    "movies_monitor.py": {"every_s": 24 * 60 * 60},
    "ride_deals_scan.py": {"every_s": 12 * 60 * 60},      # twice daily
    "agent_log_indexer.py": {"every_s": 60 * 60},         # hourly
    "geofence_nudger.py": {"every_s": 20 * 60},           # every 20 min
    # Weekly agent email can be scheduled separately; include it here if desired:
    # "weekly_agent_email.py": {"every_s": 7 * 24 * 60 * 60},
}

# -------- Utilities --------
def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line)
    with open(HEARTBEAT, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def append_json_line(path: Path, payload: dict):
    payload["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")

def read_voice_token():
    token = None
    if VOICE_ENV.exists():
        try:
            for line in VOICE_ENV.read_text(encoding="utf-8").splitlines():
                if line.startswith("VOICE_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    break
        except Exception:
            pass
    return token

def http_get(url: str, timeout_s: int = 10):
    try:
        with urlopen(url, timeout=timeout_s) as r:
            return r.read().decode("utf-8", "ignore")
    except URLError as e:
        return f"ERR:{e}"

def voice_post(query: str, token: str, timeout_s: int = 15):
    try:
        body = f"query={query}".encode()
        req = Request(VOICE_URL, data=body, method="POST",
                      headers={"Content-Type": "application/x-www-form-urlencoded",
                               "X-Auth": token})
        with urlopen(req, timeout=timeout_s) as r:
            return r.read().decode("utf-8", "ignore")
    except URLError as e:
        return f"ERR:{e}"

def wsgi_touch():
    try:
        subprocess.run(["touch", WSGI_PATH], check=True)
        time.sleep(2)
        return "WSGI_TOUCHED"
    except Exception as e:
        return f"TOUCH_ERR:{e}"

# Per-task run throttling via .last files
def should_run_task(task: str, every_s: int) -> bool:
    marker = LOG_DIR / f".last_{task}"
    now = datetime.now(timezone.utc)
    if marker.exists():
        last = datetime.fromtimestamp(marker.stat().st_mtime, tz=timezone.utc)
        if now - last < timedelta(seconds=every_s):
            return False
    marker.touch()
    return True

def run_tool(task_py: str):
    script = TOOLS / task_py
    if not script.exists():
        log(f"missing tool: {task_py}")
        return
    try:
        res = subprocess.run([sys.executable, str(script)],
                             capture_output=True, text=True, timeout=900)
        if res.returncode == 0:
            log(f"ran {task_py} ok")
        else:
            log(f"{task_py} exited {res.returncode}")
            append_json_line(ERRORS, {"task": task_py, "rc": res.returncode, "stderr": res.stderr[-800:]})
    except Exception as e:
        log(f"exception running {task_py}: {e}")
        append_json_line(ERRORS, {"task": task_py, "exception": str(e)})

# -------- Voice checks --------
def voice_health_cycle():
    if not VOICE_ENABLED:
        append_json_line(STATUS, {"voice": "disabled"})
        return

    token = read_voice_token()
    health = http_get(HEALTH_URL, timeout_s=10)
    result1 = None
    result2 = None
    reload_action = None

    if token:
        result1 = voice_post("What%20was%20my%20last%20absorption%20run?", token, timeout_s=15)
        if isinstance(result1, str) and result1.startswith("ERR:"):
            time.sleep(RETRY_SLEEP)
            result2 = voice_post("What%20was%20my%20last%20absorption%20run?", token, timeout_s=15)
            if isinstance(result2, str) and result2.startswith("ERR:"):
                reload_action = wsgi_touch()
    else:
        result1 = "NO_TOKEN"

    append_json_line(STATUS, {
        "health": health[:200] if health else "",
        "voice_try1": (result1 or "")[:240],
        "voice_try2": (result2 or "")[:240] if result2 else "",
        "action": reload_action or ""
    })

# -------- Main cycles --------
def run_tasks_cycle():
    for task, meta in TASKS.items():
        every = int(meta.get("every_s", 0)) or 0
        if every <= 0:
            continue
        if should_run_task(task, every):
            run_tool(task)

def main():
    if ONESHOT:
        log("MCL Guard one-shot run")
        voice_health_cycle()
        run_tasks_cycle()
        log("MCL Guard one-shot complete")
        return

    log("MCL Guard loop starting")
    while True:
        try:
            voice_health_cycle()
            run_tasks_cycle()
            log("heartbeat ok")
        except Exception as e:
            log(f"fatal loop error: {e}")
            append_json_line(ERRORS, {"fatal_loop_error": str(e)})
        time.sleep(LOOP_SLEEP)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("stopped by user")
    except Exception as e:
        log(f"fatal error: {e}")
        append_json_line(ERRORS, {"fatal_error": str(e)})
        traceback.print_exc(file=open(ERRORS, "a", encoding="utf-8"))
