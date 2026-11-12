"""Actual OS child-process termination in a disposable SQLite sandbox.

The child intentionally exits immediately after claiming a synthetic task.
Parent validates real process exit, durable state, and no accidental replay.
"""
import os
import subprocess
import sys
import tempfile
import unittest

from agents.phase2_durable import DurableSimulatedRouter, DurableTaskJournal


class ProcessKillTests(unittest.TestCase):
    def test_os_process_exits_during_claim_then_restart_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            db = os.path.join(folder, "tasks.sqlite")
            child_code = (
                "import os,sys\n"
                "from agents.phase2_durable import DurableTaskJournal\n"
                "journal=DurableTaskJournal(sys.argv[1],simulation=True)\n"
                "journal.register('task1','executor','synthetic task')\n"
                "journal.claim('task1')\n"
                "os._exit(47)\n"
            )
            child = subprocess.run(
                [sys.executable, "-c", child_code, db],
                cwd=os.getcwd(), capture_output=True, text=True, timeout=20)
            self.assertEqual(child.returncode, 47, child.stderr)
            executed = []
            router = DurableSimulatedRouter(
                db, {"executor": lambda task: executed.append(task) or "done"},
                simulation=True)
            self.assertEqual(router.journal.get("task1")["state"], "uncertain")
            report = router.dispatch("task1", "executor", "synthetic task")
            self.assertEqual(report["state"], "uncertain")
            self.assertFalse(report["executed"])
            self.assertEqual(executed, [])
            router.close()
            journal = DurableTaskJournal(db, simulation=True)
            self.assertEqual(journal.get("task1")["state"], "uncertain")
            journal.close()


if __name__ == "__main__":
    unittest.main()
