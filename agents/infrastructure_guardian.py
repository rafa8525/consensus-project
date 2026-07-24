#!/usr/bin/env python3
"""
AI Consensus Infrastructure Guardian
====================================

Purpose
-------
Own infrastructure health across PythonAnywhere and GitHub:

- disk quota and growth checks
- Git working-tree and branch divergence checks
- failed push detection
- stale Git lock detection
- oversized log rotation
- tracked generated/dependency directory detection
- loose-object and repository-size checks
- safe, conservative automatic repairs
- structured status, incident, and audit logs

Safe by default
---------------
The guardian will NOT:
- force-push
- rewrite Git history
- delete project data
- resolve merge conflicts
- discard working changes
- remove an active Git lock
- run a full git gc while disk space is constrained

Exit codes
----------
0 = healthy
1 = warning
2 = critical
3 = guardian execution failure
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


VERSION = "2026.07.24-v1"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    repaired: bool = False
    repair_message: str | None = None


@dataclass
class Config:
    repo_root: Path
    memory_root: Path
    state_dir: Path
    quota_bytes: int
    disk_warn_percent: float = 80.0
    disk_critical_percent: float = 90.0
    disk_emergency_percent: float = 95.0
    git_dir_warn_bytes: int = 500 * 1024 * 1024
    loose_object_warn_count: int = 10_000
    log_rotate_bytes: int = 25 * 1024 * 1024
    max_rotated_logs: int = 2
    auto_rotate_logs: bool = True
    auto_remove_stale_locks: bool = True
    auto_repack_loose_objects: bool = False
    auto_push_when_safe: bool = False
    suspend_nonessential_marker: Path | None = None
    notification_command: str | None = None
    tracked_path_patterns: tuple[str, ...] = (
        "node_modules/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        "*.pyc",
        "*.log",
    )


class GuardianError(RuntimeError):
    pass


class InfrastructureGuardian:
    def __init__(self, config: Config, apply_repairs: bool = False) -> None:
        self.config = config
        self.apply_repairs = apply_repairs
        self.findings: list[Finding] = []
        self.started_at = iso_now()
        self.lock_handle: Any | None = None

        self.config.state_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.config.state_dir / "infrastructure_guardian.log"
        self.status_path = self.config.state_dir / "infrastructure_guardian_status.json"
        self.incident_path = self.config.state_dir / "infrastructure_guardian_incidents.jsonl"
        self.lock_path = self.config.state_dir / ".infrastructure_guardian.lock"

    # -------------------------
    # Core helpers
    # -------------------------

    def log(self, message: str) -> None:
        line = f"{iso_now()} {message.rstrip()}\n"
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(line)

    def add(
        self,
        severity: str,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> Finding:
        finding = Finding(
            severity=severity,
            code=code,
            message=message,
            details=details or {},
        )
        self.findings.append(finding)
        self.log(f"{severity.upper()} {code}: {message}")
        return finding

    def run(
        self,
        command: Sequence[str],
        *,
        timeout: int = 60,
        check: bool = False,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            list(command),
            cwd=str(cwd or self.config.repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        if check and result.returncode != 0:
            raise GuardianError(
                f"Command failed ({result.returncode}): {' '.join(command)}\n"
                f"{result.stderr.strip()}"
            )
        return result

    def acquire_lock(self) -> None:
        self.lock_handle = self.lock_path.open("a+")
        try:
            fcntl.flock(self.lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise GuardianError("Another Infrastructure Guardian run is active.") from exc
        self.lock_handle.seek(0)
        self.lock_handle.truncate()
        self.lock_handle.write(f"{os.getpid()}\n")
        self.lock_handle.flush()

    def release_lock(self) -> None:
        if self.lock_handle is not None:
            try:
                fcntl.flock(self.lock_handle.fileno(), fcntl.LOCK_UN)
            finally:
                self.lock_handle.close()
                self.lock_handle = None

    # -------------------------
    # Disk health
    # -------------------------

    def directory_size(self, path: Path) -> int:
        total = 0
        try:
            for root, dirs, files in os.walk(path, onerror=lambda _: None):
                for name in files:
                    file_path = Path(root) / name
                    try:
                        total += file_path.stat().st_size
                    except OSError:
                        pass
        except OSError:
            pass
        return total

    def top_directories(self, root: Path, limit: int = 10) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        try:
            children = list(root.iterdir())
        except OSError:
            return rows
        for child in children:
            try:
                size = self.directory_size(child) if child.is_dir() else child.stat().st_size
            except OSError:
                continue
            rows.append({"path": str(child), "bytes": size})
        rows.sort(key=lambda row: row["bytes"], reverse=True)
        return rows[:limit]

    def check_disk(self) -> None:
        home = Path.home()
        usage = shutil.disk_usage(home)
        used_for_quota = self.directory_size(home)
        quota = self.config.quota_bytes
        percent = (used_for_quota / quota * 100.0) if quota else 0.0

        details = {
            "home": str(home),
            "home_bytes": used_for_quota,
            "quota_bytes": quota,
            "quota_percent": round(percent, 2),
            "filesystem_free_bytes": usage.free,
            "largest_home_entries": self.top_directories(home),
        }

        if percent >= self.config.disk_emergency_percent:
            finding = self.add(
                "critical",
                "DISK_EMERGENCY",
                f"Home storage is {percent:.1f}% of quota.",
                details,
            )
            self.set_nonessential_suspension(True, finding)
        elif percent >= self.config.disk_critical_percent:
            self.add(
                "critical",
                "DISK_CRITICAL",
                f"Home storage is {percent:.1f}% of quota.",
                details,
            )
        elif percent >= self.config.disk_warn_percent:
            self.add(
                "warning",
                "DISK_WARNING",
                f"Home storage is {percent:.1f}% of quota.",
                details,
            )
        else:
            self.add(
                "healthy",
                "DISK_OK",
                f"Home storage is {percent:.1f}% of quota.",
                details,
            )

    def set_nonessential_suspension(self, enabled: bool, finding: Finding) -> None:
        marker = self.config.suspend_nonessential_marker
        if marker is None or not self.apply_repairs:
            return
        try:
            marker.parent.mkdir(parents=True, exist_ok=True)
            if enabled:
                marker.write_text(
                    json.dumps(
                        {
                            "created_at": iso_now(),
                            "reason": finding.code,
                            "message": finding.message,
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                finding.repaired = True
                finding.repair_message = f"Created suspension marker: {marker}"
            elif marker.exists():
                marker.unlink()
        except OSError as exc:
            finding.repair_message = f"Could not update suspension marker: {exc}"

    # -------------------------
    # Log health
    # -------------------------

    def candidate_log_roots(self) -> list[Path]:
        roots = [
            self.config.memory_root / "logs",
            self.config.repo_root / "logs",
        ]
        return [path for path in roots if path.exists()]

    def rotate_file(self, path: Path) -> None:
        for index in range(self.config.max_rotated_logs, 0, -1):
            source = path.with_name(f"{path.name}.{index}")
            target = path.with_name(f"{path.name}.{index + 1}")
            if index == self.config.max_rotated_logs and source.exists():
                source.unlink()
            elif source.exists():
                source.replace(target)

        first = path.with_name(f"{path.name}.1")
        path.replace(first)
        path.touch()

    def check_logs(self) -> None:
        oversized: list[dict[str, Any]] = []
        for root in self.candidate_log_roots():
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                try:
                    size = path.stat().st_size
                except OSError:
                    continue
                if size >= self.config.log_rotate_bytes:
                    oversized.append({"path": str(path), "bytes": size})

        if not oversized:
            self.add("healthy", "LOGS_OK", "No oversized logs found.")
            return

        finding = self.add(
            "warning",
            "OVERSIZED_LOGS",
            f"Found {len(oversized)} oversized log or status files.",
            {"files": oversized[:100]},
        )

        if self.apply_repairs and self.config.auto_rotate_logs:
            rotated = 0
            failed: list[str] = []
            for row in oversized:
                path = Path(row["path"])
                try:
                    self.rotate_file(path)
                    rotated += 1
                except OSError as exc:
                    failed.append(f"{path}: {exc}")
            finding.repaired = rotated > 0 and not failed
            finding.repair_message = (
                f"Rotated {rotated} files."
                + (f" Failures: {failed[:10]}" if failed else "")
            )

    # -------------------------
    # Git health
    # -------------------------

    def git(self, *args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
        return self.run(["git", *args], timeout=timeout)

    def check_repository(self) -> None:
        if not (self.config.repo_root / ".git").exists():
            self.add(
                "critical",
                "NOT_A_GIT_REPOSITORY",
                f"No .git directory found at {self.config.repo_root}.",
            )
            return

        self.check_git_lock()
        self.check_git_status()
        self.check_git_divergence()
        self.check_git_objects()
        self.check_tracked_generated_paths()

    def git_processes(self) -> list[str]:
        result = self.run(["pgrep", "-af", "git|pack-objects"], timeout=10, cwd=Path.home())
        if result.returncode not in (0, 1):
            return []
        current_pid = str(os.getpid())
        return [
            line
            for line in result.stdout.splitlines()
            if line.strip() and not line.lstrip().startswith(current_pid + " ")
        ]

    def check_git_lock(self) -> None:
        lock = self.config.repo_root / ".git/index.lock"
        if not lock.exists():
            self.add("healthy", "GIT_LOCK_OK", "No Git index lock exists.")
            return

        processes = self.git_processes()
        try:
            age_seconds = time.time() - lock.stat().st_mtime
        except OSError:
            age_seconds = 0

        finding = self.add(
            "critical",
            "GIT_INDEX_LOCK",
            "Git index.lock exists.",
            {
                "path": str(lock),
                "age_seconds": round(age_seconds, 1),
                "git_processes": processes,
            },
        )

        safe_to_remove = not processes and age_seconds >= 300
        if (
            self.apply_repairs
            and self.config.auto_remove_stale_locks
            and safe_to_remove
        ):
            try:
                lock.unlink()
                finding.repaired = True
                finding.repair_message = "Removed stale index.lock after verifying no Git process."
            except OSError as exc:
                finding.repair_message = f"Could not remove lock: {exc}"

    def check_git_status(self) -> None:
        branch_result = self.git("branch", "--show-current")
        branch = branch_result.stdout.strip() or "(detached)"

        status_result = self.git("status", "--porcelain=v1", "-uno", timeout=120)
        if status_result.returncode != 0:
            self.add(
                "critical",
                "GIT_STATUS_FAILED",
                "git status failed.",
                {"stderr": status_result.stderr[-2000:]},
            )
            return

        lines = [line for line in status_result.stdout.splitlines() if line]
        details = {
            "branch": branch,
            "tracked_changes": len(lines),
            "sample": lines[:25],
        }

        if lines:
            self.add(
                "warning",
                "WORKTREE_DIRTY",
                f"Working tree has {len(lines)} tracked changes.",
                details,
            )
        else:
            self.add("healthy", "WORKTREE_CLEAN", "Working tree is clean.", details)

    def check_git_divergence(self) -> None:
        fetch = self.git("fetch", "--quiet", "origin", timeout=180)
        if fetch.returncode != 0:
            self.add(
                "critical",
                "GIT_FETCH_FAILED",
                "Could not fetch origin.",
                {"stderr": fetch.stderr[-2000:]},
            )
            return

        branch = self.git("branch", "--show-current").stdout.strip()
        if not branch:
            self.add("critical", "DETACHED_HEAD", "Repository is in detached HEAD state.")
            return

        upstream = f"origin/{branch}"
        verify = self.git("rev-parse", "--verify", "--quiet", upstream)
        if verify.returncode != 0:
            self.add(
                "warning",
                "UPSTREAM_MISSING",
                f"No remote branch found for {upstream}.",
            )
            return

        counts = self.git("rev-list", "--left-right", "--count", f"HEAD...{upstream}")
        if counts.returncode != 0:
            self.add(
                "critical",
                "DIVERGENCE_CHECK_FAILED",
                "Could not calculate branch divergence.",
                {"stderr": counts.stderr[-2000:]},
            )
            return

        try:
            ahead, behind = map(int, counts.stdout.strip().split())
        except ValueError:
            self.add(
                "critical",
                "DIVERGENCE_PARSE_FAILED",
                "Could not parse Git divergence counts.",
                {"output": counts.stdout},
            )
            return

        details = {
            "branch": branch,
            "upstream": upstream,
            "ahead": ahead,
            "behind": behind,
            "head": self.git("rev-parse", "--short", "HEAD").stdout.strip(),
            "remote": self.git("rev-parse", "--short", upstream).stdout.strip(),
        }

        if ahead and behind:
            self.add(
                "critical",
                "GIT_DIVERGED",
                f"Branch is ahead {ahead} and behind {behind}; human merge required.",
                details,
            )
        elif behind:
            self.add(
                "critical",
                "GIT_BEHIND",
                f"Branch is behind origin by {behind} commit(s).",
                details,
            )
        elif ahead:
            finding = self.add(
                "warning",
                "GIT_AHEAD",
                f"Branch is ahead of origin by {ahead} commit(s).",
                details,
            )
            self.maybe_push(finding, branch)
        else:
            self.add(
                "healthy",
                "GIT_SYNCED",
                "Local and remote branch tips match.",
                details,
            )

    def maybe_push(self, finding: Finding, branch: str) -> None:
        if not (self.apply_repairs and self.config.auto_push_when_safe):
            return

        dirty = self.git("status", "--porcelain=v1", "-uno", timeout=120)
        if dirty.stdout.strip():
            finding.repair_message = "Automatic push skipped because working tree is dirty."
            return

        push = self.git("push", "origin", branch, timeout=300)
        if push.returncode == 0:
            finding.repaired = True
            finding.repair_message = "Pushed local commits to origin."
        else:
            finding.repair_message = f"Push failed: {push.stderr[-1000:]}"

    def check_git_objects(self) -> None:
        result = self.git("count-objects", "-vH")
        if result.returncode != 0:
            self.add(
                "critical",
                "GIT_OBJECT_CHECK_FAILED",
                "git count-objects failed.",
                {"stderr": result.stderr[-2000:]},
            )
            return

        parsed: dict[str, str] = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                parsed[key.strip()] = value.strip()

        try:
            loose_count = int(parsed.get("count", "0"))
        except ValueError:
            loose_count = 0

        git_size = self.directory_size(self.config.repo_root / ".git")
        details = {
            "git_directory_bytes": git_size,
            "loose_object_count": loose_count,
            "git_count_objects": parsed,
        }

        severity = "healthy"
        code = "GIT_OBJECTS_OK"
        message = "Git object storage is within thresholds."

        if git_size >= self.config.git_dir_warn_bytes:
            severity, code = "warning", "GIT_DIRECTORY_LARGE"
            message = f".git is {git_size / 1024**2:.1f} MiB."
        if loose_count >= self.config.loose_object_warn_count:
            severity, code = "warning", "TOO_MANY_LOOSE_OBJECTS"
            message = f"Git has {loose_count} loose objects."

        finding = self.add(severity, code, message, details)

        if (
            self.apply_repairs
            and self.config.auto_repack_loose_objects
            and loose_count >= self.config.loose_object_warn_count
        ):
            self.safe_low_memory_repack(finding)

    def safe_low_memory_repack(self, finding: Finding) -> None:
        home_bytes = self.directory_size(Path.home())
        free_quota = max(0, self.config.quota_bytes - home_bytes)
        git_size = self.directory_size(self.config.repo_root / ".git")

        required_free = max(1024**3, int(git_size * 0.75))
        if free_quota < required_free:
            finding.repair_message = (
                f"Repack skipped: {free_quota / 1024**2:.1f} MiB quota space free; "
                f"requires at least {required_free / 1024**2:.1f} MiB."
            )
            return

        command = [
            "git",
            "-c", "pack.threads=1",
            "-c", "pack.windowMemory=32m",
            "-c", "pack.window=10",
            "-c", "pack.depth=20",
            "repack", "-d", "-l",
        ]
        result = self.run(command, timeout=1800)
        if result.returncode != 0:
            finding.repair_message = f"Low-memory repack failed: {result.stderr[-1500:]}"
            return

        prune = self.git("prune-packed", timeout=600)
        if prune.returncode == 0:
            finding.repaired = True
            finding.repair_message = "Completed low-memory repack and prune-packed."
        else:
            finding.repair_message = f"Repack succeeded but prune-packed failed: {prune.stderr[-1000:]}"

    def check_tracked_generated_paths(self) -> None:
        result = self.git("ls-files", "-z", timeout=180)
        if result.returncode != 0:
            self.add(
                "critical",
                "GIT_LS_FILES_FAILED",
                "Could not enumerate tracked files.",
                {"stderr": result.stderr[-2000:]},
            )
            return

        tracked = result.stdout.split("\0")
        offenders: list[str] = []
        for path in tracked:
            if not path:
                continue
            normalized = path.replace("\\", "/")
            if (
                "/node_modules/" in f"/{normalized}"
                or "/__pycache__/" in f"/{normalized}"
                or normalized.endswith(".pyc")
                or "/.pytest_cache/" in f"/{normalized}"
                or "/.mypy_cache/" in f"/{normalized}"
                or "/.ruff_cache/" in f"/{normalized}"
            ):
                offenders.append(path)

        if offenders:
            self.add(
                "critical",
                "TRACKED_GENERATED_FILES",
                f"Git tracks {len(offenders)} generated or dependency files.",
                {"sample": offenders[:100], "count": len(offenders)},
            )
        else:
            self.add(
                "healthy",
                "TRACKED_FILES_OK",
                "No tracked dependency/cache files were detected.",
            )

    # -------------------------
    # Reporting and notification
    # -------------------------

    def severity_rank(self, severity: str) -> int:
        return {"healthy": 0, "warning": 1, "critical": 2}.get(severity, 3)

    def overall_severity(self) -> str:
        worst = max((self.severity_rank(item.severity) for item in self.findings), default=0)
        return {0: "healthy", 1: "warning", 2: "critical"}.get(worst, "critical")

    def write_reports(self) -> dict[str, Any]:
        payload = {
            "version": VERSION,
            "started_at": self.started_at,
            "finished_at": iso_now(),
            "overall_status": self.overall_severity(),
            "apply_repairs": self.apply_repairs,
            "repo_root": str(self.config.repo_root),
            "memory_root": str(self.config.memory_root),
            "findings": [asdict(item) for item in self.findings],
        }

        temporary = self.status_path.with_name(
            f".{self.status_path.name}.tmp-{os.getpid()}"
        )
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, self.status_path)

        incidents = [
            asdict(item)
            for item in self.findings
            if item.severity in {"warning", "critical"}
        ]
        if incidents:
            with self.incident_path.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "timestamp": iso_now(),
                            "overall_status": payload["overall_status"],
                            "incidents": incidents,
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )

        return payload

    def notify(self, payload: dict[str, Any]) -> None:
        command = self.config.notification_command
        if not command or payload["overall_status"] == "healthy":
            return

        summary = {
            "status": payload["overall_status"],
            "critical": [
                item["message"]
                for item in payload["findings"]
                if item["severity"] == "critical"
            ],
            "warnings": [
                item["message"]
                for item in payload["findings"]
                if item["severity"] == "warning"
            ],
            "status_file": str(self.status_path),
        }

        env = os.environ.copy()
        env["INFRA_GUARDIAN_EVENT"] = json.dumps(summary)
        try:
            subprocess.run(
                command,
                shell=True,
                cwd=str(self.config.repo_root),
                env=env,
                timeout=60,
                check=False,
            )
        except Exception as exc:
            self.log(f"WARNING NOTIFICATION_FAILED: {exc}")

    def execute(self) -> int:
        try:
            self.acquire_lock()
            self.log(
                f"START version={VERSION} apply_repairs={self.apply_repairs} "
                f"repo={self.config.repo_root}"
            )
            self.check_disk()
            self.check_logs()
            self.check_repository()
            payload = self.write_reports()
            self.notify(payload)
            self.log(f"FINISH status={payload['overall_status']}")
            return {"healthy": 0, "warning": 1, "critical": 2}[payload["overall_status"]]
        except Exception as exc:
            self.log(f"FAIL guardian_execution_error={type(exc).__name__}: {exc}")
            failure = {
                "version": VERSION,
                "started_at": self.started_at,
                "finished_at": iso_now(),
                "overall_status": "execution_failure",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            self.status_path.write_text(
                json.dumps(failure, indent=2) + "\n",
                encoding="utf-8",
            )
            return 3
        finally:
            self.release_lock()


def load_json_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_config(raw: dict[str, Any]) -> Config:
    repo_root = Path(
        os.getenv(
            "CONSENSUS_REPO_ROOT",
            raw.get("repo_root", str(Path.home() / "consensus-project")),
        )
    ).expanduser().resolve()

    memory_root = Path(
        os.getenv(
            "CONSENSUS_MEMORY_ROOT",
            raw.get("memory_root", str(Path.home() / "memory")),
        )
    ).expanduser().resolve()

    state_dir = Path(
        raw.get(
            "state_dir",
            str(memory_root / "logs/system"),
        )
    ).expanduser().resolve()

    quota_gb = float(
        os.getenv(
            "CONSENSUS_HOME_QUOTA_GB",
            str(raw.get("quota_gb", 5.0)),
        )
    )

    marker_raw = raw.get(
        "suspend_nonessential_marker",
        str(memory_root / "logs/system/.suspend_nonessential_jobs"),
    )

    return Config(
        repo_root=repo_root,
        memory_root=memory_root,
        state_dir=state_dir,
        quota_bytes=int(quota_gb * 1024**3),
        disk_warn_percent=float(raw.get("disk_warn_percent", 80)),
        disk_critical_percent=float(raw.get("disk_critical_percent", 90)),
        disk_emergency_percent=float(raw.get("disk_emergency_percent", 95)),
        git_dir_warn_bytes=int(float(raw.get("git_dir_warn_mb", 500)) * 1024**2),
        loose_object_warn_count=int(raw.get("loose_object_warn_count", 10_000)),
        log_rotate_bytes=int(float(raw.get("log_rotate_mb", 25)) * 1024**2),
        max_rotated_logs=int(raw.get("max_rotated_logs", 2)),
        auto_rotate_logs=bool(raw.get("auto_rotate_logs", True)),
        auto_remove_stale_locks=bool(raw.get("auto_remove_stale_locks", True)),
        auto_repack_loose_objects=bool(raw.get("auto_repack_loose_objects", False)),
        auto_push_when_safe=bool(raw.get("auto_push_when_safe", False)),
        suspend_nonessential_marker=Path(marker_raw).expanduser().resolve()
        if marker_raw
        else None,
        notification_command=os.getenv(
            "INFRA_GUARDIAN_NOTIFICATION_COMMAND",
            raw.get("notification_command"),
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor and conservatively repair PythonAnywhere/GitHub infrastructure."
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON configuration file.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply only explicitly enabled safe repairs.",
    )
    parser.add_argument(
        "--print-status",
        action="store_true",
        help="Print the resulting JSON status document.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = load_json_config(args.config)
    config = build_config(raw)
    guardian = InfrastructureGuardian(config, apply_repairs=args.apply)
    exit_code = guardian.execute()

    if args.print_status and guardian.status_path.exists():
        print(guardian.status_path.read_text(encoding="utf-8"))

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
