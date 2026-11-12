"""Actual process termination plus independent read-only staging verification."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from agents.phase3_pipeline import SimulatedEvidencePipeline
from agents.phase5_durable import DurableMockRegistry

def subprocess_run(module, folder, mode=None):
    args = [sys.executable, "-m", module]
    if mode is not None:
        args.append(mode)
    args.append(folder)
    return subprocess.run(args, capture_output=True, text=True, timeout=20)


class StagingSupervisionTests(unittest.TestCase):
    def test_task_crash_stays_uncertain_and_no_notification_occurs(self):
        with tempfile.TemporaryDirectory() as folder:
            child = subprocess_run("agents.staging_child", folder, "kill_task")
            self.assertEqual(child.returncode, 71, child.stderr)
            observer = subprocess_run("agents.staging_observer", folder)
            self.assertEqual(observer.returncode, 0, observer.stderr)
            snapshot = json.loads(observer.stdout)
            self.assertEqual(snapshot["tasks"], [["staging.task1", "running"]])
            self.assertEqual(snapshot["memory"], [])
            self.assertEqual(snapshot["deliveries"], [])
            calls = []
            pipeline = SimulatedEvidencePipeline(
                os.path.join(folder, "tasks.sqlite"),
                os.path.join(folder, "memory.sqlite"),
                {"executor": lambda task: calls.append(task) or "ok"}, simulation=True)
            replay = pipeline.dispatch("staging.task1", "executor", "synthetic work")
            self.assertEqual(replay["state"], "uncertain")
            self.assertFalse(replay["executed"])
            self.assertEqual(calls, [])
            pipeline.close()
            after = subprocess_run("agents.staging_observer", folder)
            self.assertEqual(json.loads(after.stdout)["tasks"], [["staging.task1", "uncertain"]])

    def test_notification_crash_is_claimed_without_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            child = subprocess_run("agents.staging_child", folder, "kill_notification")
            self.assertEqual(child.returncode, 72, child.stderr)
            before = subprocess_run("agents.staging_observer", folder)
            self.assertEqual(before.returncode, 0, before.stderr)
            state = json.loads(before.stdout)
            self.assertEqual(state["tasks"], [["staging.task1", "completed"]])
            self.assertEqual(state["memory"], [["phase3.staging.task1", "staging.task1"]])
            self.assertEqual(state["deliveries"],
                             [["notifications.mock", "staging.event1", "claimed"]])
            calls = []
            registry = DurableMockRegistry(os.path.join(folder, "events.sqlite"),
                                           simulation=True)
            registry.register(adapter_id="notifications.mock", capability="notifications",
                              workflow_key="existing.status.summary", owner="acs-02",
                              permissions={"notify_mock"},
                              handler=lambda payload: calls.append(payload) or "ok")
            replay = registry.dispatch(
                adapter_id="notifications.mock", principal="acs-02",
                permission="notify_mock", event_id="staging.event1",
                payload={"synthetic_value": "synthetic task finished"})
            self.assertEqual(replay["status"], "claimed")
            self.assertTrue(replay["duplicate"])
            self.assertFalse(replay["executed"])
            self.assertEqual(calls, [])
            registry.close()

    def test_successful_complete_run_observed_across_process(self):
        with tempfile.TemporaryDirectory() as folder:
            child = subprocess_run("agents.staging_child", folder, "success")
            self.assertEqual(child.returncode, 0, child.stderr)
            observed = subprocess_run("agents.staging_observer", folder)
            self.assertEqual(observed.returncode, 0, observed.stderr)
            state = json.loads(observed.stdout)
            self.assertEqual(state["tasks"], [["staging.task1", "completed"]])
            self.assertEqual(state["memory"], [["phase3.staging.task1", "staging.task1"]])
            self.assertEqual(state["deliveries"],
                             [["notifications.mock", "staging.event1", "delivered"]])


if __name__ == "__main__":
    unittest.main()
