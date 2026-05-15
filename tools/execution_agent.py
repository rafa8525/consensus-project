#!/usr/bin/env python3
"""
execution_agent.py

Safe execution layer for Rafael's AI Consensus System.

Purpose:
- Read the latest master decision JSON
- Map high-level actions to safe, allowlisted operations
- Execute only non-destructive actions
- Keep a durable audit trail

Recommended loop:
1. python3 tools/master_decision_agent.py
2. python3 tools/execution_agent.py
3. python3 tools/master_decision_agent.py

Version 1 design:
- conservative
- file-based
- no arbitrary command execution
- all behavior routed through explicit allowlisted mappings
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("America/Los_Angeles")


@dataclass
class ExecutionResult:
    name: str
    status: str   # executed | skipped | failed
    detail: str
    command: Optional[List[str]] = None


class ExecutionAgent:
    def __init__(self, mem_root: Path, repo_root: Path, dry_run: bool = False) -> None:
        self.mem_root = mem_root
        self.repo_root = repo_root
        self.dry_run = dry_run

        self.decisions_dir = self.mem_root / "logs" / "decisions"
        self.system_exec_dir = self.mem_root / "logs" / "system" / "exec"
        self.prevention_dir = self.mem_root / "logs" / "prevention"

        self.audit_path = self.system_exec_dir / "execution_agent_audit.log"

        self.master_decision_script = self.repo_root / "tools" / "master_decision_agent.py"
        self.auto_remediation_script = self.repo_root / "tools" / "auto_remediation_agent.py"
        self.prevention_writer_script = self.repo_root / "tools" / "prevention_writer.py"

    def run(self) -> Dict[str, Any]:
        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone(LOCAL_TZ)
        today = now_local.date().isoformat()

        self._ensure_dirs()

        decision = self._load_latest_decision(today)
        overall_state = str(decision.get("overall_state", "UNKNOWN")).upper()
        top_actions = decision.get("top_actions", [])
        top_risk = str(decision.get("top_risk", "unknown"))
        confidence = str(decision.get("confidence", "UNKNOWN")).upper()

        results: List[ExecutionResult] = []

        # Rule 1: If system is not OK, run safe auto-remediation
        if overall_state in {"WARN", "FAIL", "UNKNOWN"}:
            results.append(
                self._run_allowlisted_python(
                    name="auto_remediation",
                    script_path=self.auto_remediation_script,
                    args=[],
                    detail="overall state not OK, running safe auto-remediation",
                )
            )
        else:
            results.append(
                ExecutionResult(
                    name="auto_remediation",
                    status="skipped",
                    detail="overall state is OK, no remediation needed",
                    command=None,
                )
            )

        # Rule 2: If system is not OK, capture prevention memory
        if overall_state in {"WARN", "FAIL", "UNKNOWN"}:
            results.append(
                self._run_allowlisted_python(
                    name="prevention_note",
                    script_path=self.prevention_writer_script,
                    args=[
                        "--issue", f"execution_agent observed {overall_state} state",
                        "--root-cause", f"Decision brief reported: {top_risk}",
                        "--fix", "Ran safe auto-remediation through execution_agent.py",
                        "--prevention-rule", "If overall state is not OK, run safe remediation and re-evaluate the same run",
                        "--owner", "Execution Agent",
                        "--verify", f"python3 {self.master_decision_script}",
                    ],
                    detail="capturing prevention memory for non-OK state",
                )
            )
        else:
            results.append(
                ExecutionResult(
                    name="prevention_note",
                    status="skipped",
                    detail="overall state is OK, no prevention note needed this run",
                    command=None,
                )
            )

        # Rule 3: Re-evaluate after execution so the loop closes in the same run
        results.append(
            self._run_allowlisted_python(
                name="re_evaluate_master_decision",
                script_path=self.master_decision_script,
                args=[],
                detail="re-running master decision agent to verify post-execution state",
            )
        )

        # Rule 4: Record a no-op trace when system is already healthy
        if overall_state == "OK":
            results.append(
                ExecutionResult(
                    name="healthy_state_trace",
                    status="executed" if not self.dry_run else "skipped",
                    detail=f"system already healthy at confidence={confidence}; maintained normal cadence",
                    command=None,
                )
            )

        output = {
            "generated_local": now_local.isoformat(),
            "generated_utc": now_utc.isoformat(),
            "dry_run": self.dry_run,
            "overall_state_seen": overall_state,
            "confidence_seen": confidence,
            "top_actions_seen": top_actions,
            "top_risk_seen": top_risk,
            "results": [asdict(r) for r in results],
        }

        if not self.dry_run:
            self._append_audit_log(output)

        return output

    def _ensure_dirs(self) -> None:
        self.system_exec_dir.mkdir(parents=True, exist_ok=True)
        self.prevention_dir.mkdir(parents=True, exist_ok=True)

    def _load_latest_decision(self, today: str) -> Dict[str, Any]:
        today_path = self.decisions_dir / f"{today}_decision.json"
        if today_path.exists():
            return self._read_json(today_path)

        candidates = sorted(self.decisions_dir.glob("*_decision.json"))
        if not candidates:
            return {}
        return self._read_json(candidates[-1])

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _run_allowlisted_python(
        self,
        name: str,
        script_path: Path,
        args: List[str],
        detail: str,
    ) -> ExecutionResult:
        if not script_path.exists():
            return ExecutionResult(
                name=name,
                status="failed",
                detail=f"allowlisted script not found: {script_path}",
                command=["python3", str(script_path), *args],
            )

        command = ["python3", str(script_path), *args]

        if self.dry_run:
            return ExecutionResult(
                name=name,
                status="executed",
                detail=f"would run allowlisted script: {detail}",
                command=command,
            )

        try:
            completed = subprocess.run(
                command,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode == 0:
                tail = self._trim_output(completed.stdout)
                msg = detail
                if tail:
                    msg += f" | stdout={tail}"
                return ExecutionResult(
                    name=name,
                    status="executed",
                    detail=msg,
                    command=command,
                )
            err = self._trim_output(completed.stderr or completed.stdout)
            return ExecutionResult(
                name=name,
                status="failed",
                detail=f"{detail} | exit={completed.returncode} | output={err}",
                command=command,
            )
        except Exception as exc:
            return ExecutionResult(
                name=name,
                status="failed",
                detail=f"{detail} | exception={exc}",
                command=command,
            )

    def _trim_output(self, text: str, limit: int = 240) -> str:
        cleaned = " ".join(text.split())
        if len(cleaned) <= limit:
            return cleaned
        return cleaned[:limit] + "..."

    def _append_audit_log(self, output: Dict[str, Any]) -> None:
        stamp = output.get("generated_utc", "")
        with self.audit_path.open("a", encoding="utf-8") as fh:
            for result in output.get("results", []):
                cmd = result.get("command")
                cmd_text = " ".join(cmd) if isinstance(cmd, list) else ""
                fh.write(
                    f"{stamp} "
                    f"name={result.get('name')} "
                    f"status={result.get('status')} "
                    f"detail={result.get('detail')} "
                    f"command={cmd_text}\n"
                )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe execution layer for AI Consensus System.")
    parser.add_argument("--mem-root", default="/home/rafa1215/memory")
    parser.add_argument("--repo-root", default="/home/rafa1215/consensus-project")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agent = ExecutionAgent(
        mem_root=Path(args.mem_root),
        repo_root=Path(args.repo_root),
        dry_run=args.dry_run,
    )
    result = agent.run()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())