from __future__ import annotations

from typing import Dict, Any
import json
import os
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

    def _launcher_sync_evidence(self) -> Dict[str, Any]:
        """Read the one sync outcome supplied by the scheduled launcher.

        Never fetch, merge, or alter Git state inside the supervisor.
        Direct invocation without launcher evidence fails closed.
        """
        raw = os.environ.get("ACS01_BRANCH_SYNC_RC")
        if raw is None:
            return {"ok": False, "status": "launcher_evidence_missing"}
        try:
            rc = int(raw)
        except ValueError:
            return {"ok": False, "status": "launcher_evidence_invalid"}
        return {
            "ok": rc == 0,
            "status": "launcher_sync_ok" if rc == 0 else "launcher_sync_failed",
            "returncode": rc,
            "owner": "agents/run_acs01_supervisor.sh",
        }

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

    def _prepare_acs05_dependencies(self) -> Dict[str, Any]:
        """Refresh authoritative upstream evidence before ACS-05 evaluates it.

        Never sends SMS, replaces OAuth clients, or prints raw command output.
        Every stage runs even when an earlier stage fails, ensuring a degraded
        snapshot remains visible rather than silently reusing stale evidence.
        """
        repo = Path(__file__).resolve().parent.parent
        steps = (
            ("gmail_oauth", "tools/gmail_refresh_guard.py"),
            ("health_snapshot", "tools/core_monitors_bundle.py"),
            ("prediction_feed", "agents/prediction_feed_agent.py"),
        )
        outcomes = {}
        for name, relative in steps:
            try:
                proc = subprocess.run(
                    [sys.executable, str(repo / relative)],
                    cwd=repo,
                    capture_output=True,
                    text=True,
                    timeout=180,
                    check=False,
                )
                outcomes[name] = {
                    "ok": proc.returncode == 0,
                    "returncode": proc.returncode,
                }
            except Exception as exc:
                outcomes[name] = {
                    "ok": False,
                    "error_type": type(exc).__name__,
                }
        return {
            "ok": all(item["ok"] for item in outcomes.values()),
            "steps": outcomes,
        }

    def run(self) -> Dict[str, Any]:
        started = time.time()
        results: Dict[str, Any] = {}

        # The scheduled launcher owns synchronization; observe its exit code.
        results["branch_sync"] = self._launcher_sync_evidence()

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

        # Run every child cycle even if another child fails. Refresh ACS-05's
        # real upstream dependencies after ACS-02/03/04 and before ACS-05.
        # This is the same sequence verified in production on October 29.
        for agent in ("ACS-02", "ACS-03", "ACS-04", "ACS-05"):
            if agent == "ACS-05":
                results["acs_05_dependencies"] = self._prepare_acs05_dependencies()
            results[agent.lower().replace("-", "_")] = self._run_child_cycle(agent)

        # Fail closed when the last remote verified restore is missing or overdue.
        # Backup execution is intentionally separate from the supervisor cycle.
        from agents.backup_health import evaluate as evaluate_backup_health
        results["encrypted_backup"] = evaluate_backup_health(
            Path.home() / ".secrets/google/acs_backup_success.json"
        )

        # Publish bounded lessons from verified child failures for next cycle.
        # No attempted code repair or sensitive log/health content is persisted.
        from tools.shared_agent_lessons import produce
        try:
            results["lesson_exchange"] = {
                "ok": True,
                "result": produce(Path.cwd(), results),
            }
        except Exception as exc:
            results["lesson_exchange"] = {
                "ok": False,
                "error_type": type(exc).__name__,
            }

        finished = time.time()
        # Separate ACS-01 operational health from the health of its dependencies.
        # A child warning must remain visible without mislabeling its parent.
        core_keys = ("branch_sync", "log_audit", "self_improve",
                     "evaluation", "lesson_exchange")
        core_ok = all(
            isinstance(results.get(key), dict) and results[key].get("ok") is True
            for key in core_keys
        )
        dependency_keys = ("acs_02", "acs_03", "acs_04", "acs_05",
                           "acs_05_dependencies", "encrypted_backup")
        dependencies_ok = all(
            isinstance(results.get(key), dict) and results[key].get("ok") is True
            for key in dependency_keys
        )
        ok = core_ok
        results["system_health"] = {
            "ok": core_ok and dependencies_ok,
            "status": "healthy" if core_ok and dependencies_ok else "degraded",
            "dependency_failures": [
                key for key in dependency_keys
                if not isinstance(results.get(key), dict)
                or results[key].get("ok") is not True
            ],
        }

        st = store.load()
        st["last_supervisor_ts"] = finished
        st["last_supervisor_started_ts"] = started
        st["last_supervisor_status"] = "ok" if ok else "degraded"
        st["last_system_status"] = results["system_health"]["status"]
        st["last_supervisor_results"] = results
        store.save(st)

        record("supervisor_cycle", status=st["last_supervisor_status"])
        # Minimal, append-only per-agent outcomes permit future longitudinal
        # analysis without storing health data, OAuth details or SMS content.
        # Metrics are observational: success rates alone do NOT prove learning.
        record("agent_cycle_outcome", agent="ACS-01",
               status="healthy" if ok else "degraded")
        for agent in ("ACS-02", "ACS-03", "ACS-04", "ACS-05"):
            outcome = results.get(agent.lower().replace("-", "_"), {})
            record(
                "agent_cycle_outcome",
                agent=agent,
                status=str(outcome.get("status", "execution_failure")),
                attempt_count=outcome.get("attempt_count"),
            )
        return {
            "status": st["last_supervisor_status"],
            "started_ts": started,
            "finished_ts": finished,
            "results": results,
        }


def main() -> int:
    result = Supervisor({}).safe_run()
    # safe_run() only confirms the Python call did not raise. It does NOT
    # mean the supervisor completed a healthy ACS-01..ACS-05 cycle.
    cycle = result.get("result") if isinstance(result, dict) else None
    supervisor_healthy = (
        isinstance(result, dict)
        and result.get("ok") is True
        and isinstance(cycle, dict)
        and cycle.get("status") == "ok"
    )

    system_health = (
        cycle.get("results", {}).get("system_health", {})
        if isinstance(cycle, dict) and isinstance(cycle.get("results"), dict)
        else {}
    )
    system_healthy = supervisor_healthy and system_health.get("ok") is True

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

    # Scheduler failure indicates aggregate degradation even if ACS-01 itself
    # succeeded. Keep both health dimensions in the published state.
    return 0 if system_healthy and bridge.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
