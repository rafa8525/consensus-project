from __future__ import annotations

from typing import Dict, Any
import json
import subprocess
import sys
import time
from pathlib import Path

from agents.core.agent_base import Agent
from agents.core.metrics import record
from agents.core import store


class Supervisor(Agent):
    """ACS-01 runtime supervisor.

    The cycle is deliberately self-contained: missing optional configuration
    cannot disable orchestration, and every attempted cycle writes durable
    execution evidence plus child-agent results to memory/agents/state.json.

    ACS-01 is also the scheduled parent for ACS-02 through ACS-05 so one
    PythonAnywhere scheduled task can keep the full consensus system current.
    """

    name = "supervisor"

    def _safe_fast_forward_live_branch(self) -> Dict[str, Any]:
        """Run the canonical safe-sync engine fetched from origin/v1.1-dev."""
        repo = Path(__file__).resolve().parent.parent

        fetch = subprocess.run(
            ["git", "fetch", "--quiet", "origin", "v1.1-dev"],
            cwd=repo,
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
        )
        if fetch.returncode != 0:
            return {
                "ok": False,
                "status": "fetch_failed",
                "stderr": fetch.stderr[-1200:],
            }

        script = subprocess.run(
            ["git", "show", "origin/v1.1-dev:agents/safe_sync_live_branch.py"],
            cwd=repo,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        if script.returncode != 0:
            return {
                "ok": False,
                "status": "sync_engine_unavailable",
                "stderr": script.stderr[-1200:],
            }

        import tempfile
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                prefix="acs-safe-sync-",
                delete=False,
                encoding="utf-8",
            ) as handle:
                handle.write(script.stdout)
                temp_path = Path(handle.name)

            proc = subprocess.run(
                [sys.executable, str(temp_path)],
                cwd=repo,
                text=True,
                capture_output=True,
                timeout=600,
                check=False,
            )

            payload = None
            for line in reversed(proc.stdout.splitlines()):
                try:
                    candidate = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(candidate, dict) and "status" in candidate:
                    payload = candidate
                    break

            if payload is None:
                return {
                    "ok": False,
                    "status": "sync_engine_unreadable_output",
                    "returncode": proc.returncode,
                    "stdout": proc.stdout[-2000:],
                    "stderr": proc.stderr[-1200:],
                }

            payload["returncode"] = proc.returncode
            return payload
        except Exception as exc:
            return {
                "ok": False,
                "status": "sync_engine_execution_failure",
                "error_type": type(exc).__name__,
                "error": str(exc)[:1200],
            }
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    def _run_child_cycle(self, agent: str) -> Dict[str, Any]:
        repo = Path(__file__).resolve().parent.parent
        cmd = [sys.executable, str(repo / "agents" / "run_acs_cycle.py"), agent]
        attempts = []

        for attempt in (1, 2):
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=repo,
                    text=True,
                    capture_output=True,
                    timeout=1200,
                    check=False,
                )
            except Exception as exc:
                attempts.append({
                    "attempt": attempt,
                    "ok": False,
                    "status": "execution_failure",
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:500],
                })
                if attempt == 1:
                    time.sleep(5)
                    continue
                return {
                    "ok": False,
                    "agent": agent,
                    "status": "execution_failure",
                    "attempts": attempts,
                }

            payload = None
            for line in reversed(proc.stdout.splitlines()):
                line = line.strip()
                if not line:
                    continue
                try:
                    candidate = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(candidate, dict) and candidate.get("agent") == agent:
                    payload = candidate
                    break

            status = (
                str(payload.get("status", "execution_failure"))
                if payload is not None
                else "execution_failure"
            )
            ok = proc.returncode == 0 and status == "healthy"

            attempts.append({
                "attempt": attempt,
                "ok": ok,
                "status": status,
                "returncode": proc.returncode,
                "state": payload,
                "stdout_tail": proc.stdout[-2000:],
                "stderr_tail": proc.stderr[-2000:],
            })

            if ok:
                return {
                    "ok": True,
                    "agent": agent,
                    "status": status,
                    "attempt_count": attempt,
                    "attempts": attempts,
                    "state": payload,
                }

            if attempt == 1:
                time.sleep(5)

        last = attempts[-1]
        return {
            "ok": False,
            "agent": agent,
            "status": last.get("status", "execution_failure"),
            "returncode": last.get("returncode"),
            "attempt_count": 2,
            "attempts": attempts,
            "state": last.get("state"),
        }

    def run(self) -> Dict[str, Any]:
        started = time.time()
        results: Dict[str, Any] = {}

        # Bootstrap branch synchronization from inside the supervisor itself.
        # The legacy launcher already refreshes this file from origin before
        # execution, so this works even while the launcher script is still old.
        results["branch_sync"] = self._safe_fast_forward_live_branch()

        from agents.researcher import Researcher
        from agents.self_improver import SelfImprover
        from agents.evaluator import Evaluator

        # Researcher has no run() contract in this generation, so use its
        # supported research() entry point instead of pretending safe_run ran it.
        try:
            results["log_audit"] = {
                "ok": True,
                "result": Researcher(self.ctx).research("ACS runtime log audit"),
            }
        except Exception as exc:
            results["log_audit"] = {
                "ok": False,
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
            }

        results["self_improve"] = SelfImprover(self.ctx).safe_run()
        results["evaluation"] = Evaluator(self.ctx).safe_run()

        # Run every child cycle even if another child fails. This prevents one
        # failure from blocking fresh evidence for the remaining agents.
        for agent in ("ACS-02", "ACS-03", "ACS-04", "ACS-05"):
            results[agent.lower().replace("-", "_")] = self._run_child_cycle(agent)

        finished = time.time()
        ok = all(v.get("ok") is True for v in results.values())

        st = store.load()
        st["last_supervisor_ts"] = finished
        st["last_supervisor_started_ts"] = started
        st["last_supervisor_status"] = "ok" if ok else "degraded"
        st["last_supervisor_results"] = results
        store.save(st)

        record("supervisor_cycle", status=st["last_supervisor_status"])
        return {
            "status": st["last_supervisor_status"],
            "started_ts": started,
            "finished_ts": finished,
            "results": results,
        }


def main() -> int:
    result = Supervisor({}).safe_run()

    # Publish a fresh health snapshot immediately after every scheduled
    # supervisor cycle. This ensures the bridge reflects the ACS states that
    # were just produced, rather than waiting for a separate later task.
    repo = Path(__file__).resolve().parent.parent
    bridge = {
        "ok": False,
        "returncode": None,
        "stdout": "",
        "stderr": "",
    }
    bridge_attempts = []
    for attempt in (1, 2):
        try:
            proc = subprocess.run(
                ["bash", str(repo / "agents" / "run_pythonanywhere_health_bridge.sh")],
                cwd=repo,
                text=True,
                capture_output=True,
                timeout=300,
                check=False,
            )
            current = {
                "attempt": attempt,
                "ok": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout": proc.stdout[-2000:],
                "stderr": proc.stderr[-2000:],
            }
        except Exception as exc:
            current = {
                "attempt": attempt,
                "ok": False,
                "returncode": None,
                "stdout": "",
                "stderr": "",
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
            }

        bridge_attempts.append(current)
        if current["ok"]:
            bridge = dict(current)
            bridge["attempts"] = bridge_attempts
            break

        bridge = dict(current)
        bridge["attempts"] = bridge_attempts
        if attempt == 1:
            time.sleep(10)

    output = {
        "supervisor": result,
        "health_bridge": bridge,
    }
    print(output)

    return 0 if result.get("ok") and bridge.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
