#!/usr/bin/env python3
"""Process-boundary, DISPOSABLE scheduler outage recovery integration test.

Separate OS child processes simulate a crashed job, a disabled synthetic task,
and an independent watchdog invoking the real ACS-01 guard with a SQLite-only
API adapter. No PythonAnywhere API, network or production process is accessed.
"""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import phase1_independent_schedule_guard as guard

COMMAND = "bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh"
THIS = Path(__file__).resolve()


def open_db(path):
    db = sqlite3.connect(path, timeout=8)
    db.execute("PRAGMA busy_timeout=8000")
    return db


def initialize(path):
    with open_db(path) as db:
        db.execute("CREATE TABLE task (id INTEGER PRIMARY KEY, command TEXT, enabled INTEGER, hour INTEGER, minute INTEGER)")
        db.execute("CREATE TABLE events (seq INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, pid INTEGER)")
        db.execute("INSERT INTO task VALUES (?,?,?,?,?)", (guard.TASK_ID, COMMAND, 1, 10, 0))


def event(db, name):
    import os
    db.execute("INSERT INTO events(name,pid) VALUES (?,?)", (name, os.getpid()))


def task(db):
    r = db.execute("SELECT id,command,enabled,hour,minute FROM task").fetchone()
    return {"id": r[0], "command": r[1], "enabled": bool(r[2]),
            "hour": r[3], "minute": r[4], "interval": "daily"}


def scenario(path, mode):
    with open_db(path) as db:
        if mode == "crash":
            event(db, "child_started")
            db.commit()
            # Exit unexpectedly from a *real separate OS process*.
            import os
            os._exit(71)
        if mode == "outage":
            db.execute("UPDATE task SET enabled=0")
            event(db, "synthetic_scheduler_disabled")
            return 0
        if mode == "recover":
            if not task(db)["enabled"]:
                return 9
            event(db, "child_resumed_after_guard")
            return 0
        if mode == "observe":
            print(json.dumps({
                "task": task(db),
                "events": db.execute("SELECT name,pid FROM events ORDER BY seq").fetchall()
            }, sort_keys=True))
            return 0
        if mode == "guard":
            def fetch(url, token=None, method="GET", body=None):
                if url == guard.REPORT_URL:
                    return {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
                            "agents": {f"ACS-{n:02d}": {
                                "verified": True, "status": "current",
                                "health_status": "healthy"} for n in range(1, 6)}}
                if url != guard.API_URL or token != "isolated-no-real-credentials":
                    raise AssertionError("blocked external API")
                if method == "PATCH":
                    if body != {"enabled": True}:
                        raise AssertionError("unexpected write")
                    db.execute("UPDATE task SET enabled=1")
                    event(db, "guard_reenabled_disposable_task")
                    db.commit()
                elif method != "GET":
                    raise AssertionError("unexpected HTTP verb")
                return task(db)
            result = guard.guard(True, True, "isolated-no-real-credentials",
                                 datetime.now(timezone.utc), fetcher=fetch)
            print(json.dumps({"status": result["status"], "changed": result["changed"]}))
            return 0 if result["status"] == "SCHEDULE_REENABLED_NEXT_RUN_ONLY" else 2
    return 4


def child(path, mode):
    return subprocess.run([sys.executable, str(THIS), "_scenario", str(path), mode],
                          capture_output=True, text=True, timeout=15)


class IndependentProcessRecoveryTests(unittest.TestCase):
    def test_crash_scheduler_outage_and_independent_guard_recovery(self):
        with tempfile.TemporaryDirectory(prefix="acs-phase1-disposable-") as folder:
            path = Path(folder) / "state.sqlite"
            initialize(path)
            crash = child(path, "crash")
            self.assertEqual(crash.returncode, 71, crash.stderr)
            outage = child(path, "outage")
            self.assertEqual(outage.returncode, 0, outage.stderr)
            # A separate child cannot resume while the synthetic task is disabled.
            blocked = child(path, "recover")
            self.assertEqual(blocked.returncode, 9, blocked.stderr)
            watchdog = child(path, "guard")
            self.assertEqual(watchdog.returncode, 0, watchdog.stderr)
            self.assertEqual(json.loads(watchdog.stdout)["status"],
                             "SCHEDULE_REENABLED_NEXT_RUN_ONLY")
            resumed = child(path, "recover")
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            observed = child(path, "observe")
            self.assertEqual(observed.returncode, 0, observed.stderr)
            state = json.loads(observed.stdout)
            self.assertTrue(state["task"]["enabled"])
            self.assertEqual(state["task"]["command"], COMMAND)
            self.assertEqual((state["task"]["hour"], state["task"]["minute"]), (10, 0))
            names = [e[0] for e in state["events"]]
            self.assertEqual(names, ["child_started", "synthetic_scheduler_disabled",
                                     "guard_reenabled_disposable_task",
                                     "child_resumed_after_guard"])
            self.assertEqual(len(set(e[1] for e in state["events"])), 4)
            # A second watchdog run is idempotent and must not PATCH again.
            repeat = child(path, "guard")
            self.assertEqual(repeat.returncode, 2, repeat.stderr)
            self.assertEqual(json.loads(repeat.stdout)["status"], "HEALTHY_NOOP")
            state2 = json.loads(child(path, "observe").stdout)
            self.assertEqual(len(state2["events"]), 4)
            print("PASS: isolated process crash, task outage, independent re-enable, resume")
            print("SCOPE=isolated_simulation_only; PRODUCTION_OUTAGE_PROVEN=false")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "_scenario":
        sys.exit(scenario(sys.argv[2], sys.argv[3]))
    unittest.main()
