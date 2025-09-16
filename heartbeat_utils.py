#!/usr/bin/env python3
"""
heartbeat_utils.py
Shared utilities for writing and reading heartbeat files.

Features:
- Atomic JSON heartbeat writes (safe for guard processes to read)
- Optional text log output for human tailing
- Helper to read and validate heartbeat freshness
"""

import os
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

# Default directory for all heartbeat files
HEARTBEAT_DIR = "memory/logs/system"

# Ensure directory exists
os.makedirs(HEARTBEAT_DIR, exist_ok=True)

def write_heartbeat(agent_name: str, pid: int = None, status: str = "alive",
                    write_text_log: bool = True) -> None:
    """
    Write a heartbeat JSON file atomically, with optional text log line.

    Args:
        agent_name (str): Name of the agent (e.g., "voice_worker", "github_sync").
        pid (int, optional): Process ID of the agent. Defaults to os.getpid().
        status (str, optional): Status string, usually "alive".
        write_text_log (bool, optional): Whether to also append a plain text
                                         heartbeat line for humans to tail.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pid = pid or os.getpid()

    data = {
        "timestamp": ts,
        "pid": pid,
        "status": status,
        "agent": agent_name
    }

    # Write to temp file first, then rename atomically
    hb_file = Path(HEARTBEAT_DIR) / f"{agent_name}_heartbeat.json"
    tmp_file = str(hb_file) + ".tmp"

    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp_file, hb_file)

    # Optional: write to human-readable .log file
    if write_text_log:
        log_file = Path(HEARTBEAT_DIR) / f"{agent_name}.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] ❤️ {agent_name.upper()}_HEARTBEAT (pid={pid})\n")

    logging.debug(f"Heartbeat written for {agent_name}: {data}")


def read_heartbeat(agent_name: str, timeout: int = 60) -> tuple[bool, dict | None]:
    """
    Read and validate a heartbeat JSON file.

    Args:
        agent_name (str): Name of the agent (e.g., "voice_worker").
        timeout (int): How many seconds before a heartbeat is considered stale.

    Returns:
        (bool, dict|None): Tuple of (is_healthy, data).
    """
    hb_file = Path(HEARTBEAT_DIR) / f"{agent_name}_heartbeat.json"

    if not hb_file.exists():
        return False, None

    try:
        with open(hb_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        ts_str = data.get("timestamp")
        hb_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - hb_time).total_seconds()
        data["age_seconds"] = age

        if age <= timeout:
            return True, data
        else:
            return False, data

    except Exception as e:
        logging.error(f"Error reading heartbeat for {agent_name}: {e}")
        return False, None
