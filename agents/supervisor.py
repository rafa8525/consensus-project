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
        """Advance the live branch only when no genuine local source edits exist."""
        repo = Path(__file__).resolve().parent.parent
        remote = "origin/v1.1-dev"

        runtime_prefixes = (
            "memory/logs/",
            "memory/agents/",
            "memory/exports/",
        )
        runtime_files = {
            "memory/centralized_knowledge_base.txt",
            "memory/security_audit_schedule.txt",
        }

        def run(*args: str, timeout: int = 180):
            return subprocess.run(
                list(args),
                cwd=repo,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )

        fetch = run("git", "fetch", "--quiet", "origin", "v1.1-dev")
        if fetch.returncode != 0:
            return {
                "ok": False,
                "status": "fetch_failed",
                "stderr": fetch.stderr[-1000:],
            }

        status = run("git", "status", "--porcelain=v1", "-uno")
        if status.returncode != 0:
            return {
                "ok": False,
                "status": "status_failed",
                "stderr": status.stderr[-1000:],
            }

        meaningful = []
        for raw in status.stdout.splitlines():
            if not raw:
                continue
            path = raw[3:].strip()
            if path in runtime_files or any(path.startswith(x) for x in runtime_prefixes):
                continue
            meaningful.append(path)

        safe_refresh = []
        unsafe = []

        for path in meaningful:
            remote_blob = run("git", "show", f"{remote}:{path}")
            if remote_blob.returncode != 0:
                unsafe.append(path)
                continue

            local = repo / path
            if not local.exists():
                safe_refresh.append(path)
                continue

            try:
                local_text = local.read_text(encoding="utf-8")
            except Exception:
                unsafe.append(path)
                continue

            if local_text == remote_blob.stdout:
                safe_refresh.append(path)
            else:
                unsafe.append(path)

        if unsafe:
            return {
                "ok": False,
                "status": "blocked_local_source_changes",
                "unsafe_paths": unsafe[:20],
            }

        for path in safe_refresh:
            restore = run("git", "restore", "--source=HEAD", "--", path)
            if restore.returncode != 0:
                return {
                    "ok": False,
                    "status": "restore_failed",
                    "path": path,
                    "stderr": restore.stderr[-1000:],
                }

        merge = run("git", "merge", "--ff-only", remote, timeout=300)
        if merge.returncode != 0:
            return {
                "ok": False,
                "status": "fast_forward_failed",
                "stderr": merge.stderr[-1200:],
            }

        head = run("git", "rev-parse", "--short", "HEAD")
        return {
            "ok": True,
            "status": "synced",
            "head": head.stdout.strip(),
            "refreshed_paths": safe_refresh,
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
