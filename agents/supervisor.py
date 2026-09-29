from __future__ import annotations

from typing import Dict, Any
import time

from agents.core.agent_base import Agent
from agents.core.metrics import record
from agents.core import store


class Supervisor(Agent):
    """ACS-01 runtime supervisor.

    The cycle is deliberately self-contained: missing optional configuration
    cannot disable orchestration, and every attempted cycle writes durable
    execution evidence plus child-agent results to memory/agents/state.json.
    """

    name = "supervisor"

    def run(self) -> Dict[str, Any]:
        started = time.time()
        results: Dict[str, Any] = {}

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
    if not result.get("ok"):
        print(result)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
