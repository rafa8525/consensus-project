"""Concurrent independent mock supervisors, SQLite claim race and replay safety."""
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from agents.phase5_durable import DurableMockRegistry
from agents.phase2_protocol import ProtocolError


def registry(path, handler):
    r = DurableMockRegistry(path, simulation=True)
    r.register(adapter_id="alerts.mock", capability="notifications",
               workflow_key="existing.alerts", owner="acs-02",
               permissions={"notify_mock"}, handler=handler)
    return r


def deliver(reg, event_id="event1", payload=None):
    return reg.dispatch(adapter_id="alerts.mock", principal="acs-02",
                        permission="notify_mock", event_id=event_id,
                        payload=payload or {"synthetic_value": "example"})


class ConcurrentSupervisorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "events.sqlite")
        seed = registry(self.path, lambda data: "ok")
        seed.close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_two_simultaneous_supervisors_single_handler(self):
        lock = threading.Lock()
        calls = []
        barrier = threading.Barrier(2)
        def worker(index):
            def mock_handler(payload):
                with lock:
                    calls.append(index)
                return "ok"
            own = registry(self.path, mock_handler)
            try:
                barrier.wait(timeout=15)
                return deliver(own)
            finally:
                own.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            reports = list(pool.map(worker, (1, 2)))
        self.assertEqual(sorted(x["duplicate"] for x in reports), [False, True])
        self.assertEqual(len(calls), 1)
        self.assertEqual(sorted(x["status"] for x in reports), ["delivered", "delivered"])

    def test_conflicting_concurrent_payload_rejected(self):
        barrier = threading.Barrier(2)
        def worker(index):
            own = registry(self.path, lambda data: "ok")
            try:
                barrier.wait(timeout=15)
                try:
                    return deliver(own, payload={"synthetic_value": index})
                except ProtocolError:
                    return "collision"
            finally:
                own.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(worker, (1, 2)))
        self.assertEqual(sum(x == "collision" for x in outcomes), 1)

    def test_two_independent_processes_same_claim(self):
        # Both children use the same SQLite file but separate Python processes.
        start = os.path.join(self.tmp.name, "start")
        effect = os.path.join(self.tmp.name, "handler-calls")
        script = (
            "import json,os,sys,time\n"
            "from agents.phase5_durable import DurableMockRegistry\n"
            "db,start,effect=sys.argv[1:]\n"
            "def handler(payload):\n"
            "    with open(effect,'a') as f: f.write('called\\n')\n"
            "    return 'ok'\n"
            "r=DurableMockRegistry(db,simulation=True)\n"
            "r.register(adapter_id='alerts.mock',capability='notifications',"
            "workflow_key='existing.alerts',owner='acs-02',permissions={'notify_mock'},handler=handler)\n"
            "deadline=time.monotonic()+15\n"
            "while not os.path.exists(start) and time.monotonic()<deadline: time.sleep(0.005)\n"
            "if not os.path.exists(start): raise SystemExit(4)\n"
            "print(json.dumps(r.dispatch(adapter_id='alerts.mock',principal='acs-02',"
            "permission='notify_mock',event_id='event-process',"
            "payload={'synthetic_value':'example'})))\n"
            "r.close()\n"
        )
        procs = [
            subprocess.Popen([sys.executable, "-c", script, self.path, start, effect],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for _ in range(2)
        ]
        try:
            with open(start, "w") as marker: marker.write("go")
            results = []
            for proc in procs:
                stdout, stderr = proc.communicate(timeout=20)
                self.assertEqual(proc.returncode, 0, stderr)
                results.append(json.loads(stdout))
            self.assertEqual(sorted(x["duplicate"] for x in results), [False, True])
            with open(effect) as history:
                self.assertEqual(history.read().count("called"), 1)
        finally:
            for proc in procs:
                if proc.poll() is None:
                    proc.kill()
                    proc.communicate(timeout=5)


if __name__ == "__main__":
    unittest.main()
