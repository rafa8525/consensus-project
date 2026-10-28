"""Offline failure-injection tests for ACS-01 orchestration exit contracts."""
import ast
import contextlib
import io
import types
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "agents" / "supervisor.py"


class FailureSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        main = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        cls.main_code = compile(ast.Module(body=[main], type_ignores=[]),
                                str(SOURCE), "exec")

    def run_main(self, supervisor_ok=True, supervisor_status="ok",
                 system_ok=True, publish_returncodes=(0,)):
        cycle = {"status": supervisor_status,
                 "results": {"system_health": {"ok": system_ok}}}
        payload = {"ok": supervisor_ok, "result": cycle}
        mock_supervisor = types.SimpleNamespace(safe_run=lambda: payload)
        fake_supervisor = lambda context: mock_supervisor
        results = iter(publish_returncodes)
        calls = []
        def fake_run(*args, **kwargs):
            calls.append(args)
            return types.SimpleNamespace(returncode=next(results),
                                         stdout="", stderr="")
        fake_subprocess = types.SimpleNamespace(run=fake_run)
        fake_time = types.SimpleNamespace(sleep=lambda _: None)
        namespace = {
            "Supervisor": fake_supervisor,
            "subprocess": fake_subprocess,
            "time": fake_time,
            "Path": Path,
            "__file__": str(SOURCE),
            "__name__": "acs_phase1_simulation",
        }
        exec(self.main_code, namespace)
        with contextlib.redirect_stdout(io.StringIO()):
            result = namespace["main"]()
        return result, len(calls)

    def test_all_healthy_returns_zero(self):
        self.assertEqual(self.run_main(), (0, 1))

    def test_child_failure_propagates_aggregate_failure(self):
        self.assertEqual(self.run_main(system_ok=False), (1, 1))

    def test_supervisor_failure_propagates(self):
        self.assertEqual(self.run_main(supervisor_ok=False), (1, 1))

    def test_supervisor_degraded_propagates(self):
        self.assertEqual(self.run_main(supervisor_status="degraded"), (1, 1))

    def test_publication_failure_retries_and_fails(self):
        self.assertEqual(self.run_main(publish_returncodes=(1, 1)), (1, 2))

    def test_publication_transient_failure_recovers(self):
        self.assertEqual(self.run_main(publish_returncodes=(1, 0)), (0, 2))

    def test_aggregate_missing_fails_closed(self):
        self.assertEqual(self.run_main(system_ok=None), (1, 1))


if __name__ == "__main__":
    unittest.main()
