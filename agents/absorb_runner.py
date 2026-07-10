#!/usr/bin/env python3
"""
AI Consensus System Absorb Runner
Version: v2026-07-10-absorb-runner-v1

Purpose
-------
Run the project's real absorption/import worker reliably and maintain:

    memory/logs/system/absorb_runner.log

The runner does NOT fake a healthy result by merely touching the log. It marks
a run successful only when a real worker command exits with status 0.

Configuration
-------------
Preferred:
    export CONSENSUS_ABSORB_COMMAND='python3 agents/absorb_agent.py'

Optional:
    CONSENSUS_REPO_ROOT
    CONSENSUS_MEMORY_ROOT
    CONSENSUS_ABSORB_TIMEOUT_SECONDS   default: 900
    CONSENSUS_ABSORB_RETRIES           default: 3
    CONSENSUS_ABSORB_RETRY_DELAY       default: 15
    CONSENSUS_ABSORB_MAX_LOG_BYTES     default: 1000000

When CONSENSUS_ABSORB_COMMAND is not set, the runner searches for a supported
worker script in common project locations. It refuses to report success when no
worker can be found.
"""

from __future__ import annotations

import fcntl
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

VERSION = "v2026-07-10-absorb-runner-v1"


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    memory_root: Path
    log_path: Path
    status_path: Path
    lock_path: Path
    timeout_seconds: int
    retries: int
    retry_delay: int
    max_log_bytes: int


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def discover_repo_root() -> Path:
    configured = os.getenv("CONSENSUS_REPO_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()

    start = Path(__file__).resolve().parent
    try:
        root = subprocess.check_output(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).strip()
        if root:
            return Path(root).resolve()
    except Exception:
        pass

    cwd = Path.cwd().resolve()
    if (cwd / "agents").is_dir():
        return cwd
    return start.parent


def discover_memory_root(repo_root: Path) -> Path:
    configured = os.getenv("CONSENSUS_MEMORY_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()

    home_memory = Path.home() / "memory"
    if home_memory.exists():
        return home_memory.resolve()

    repo_memory = repo_root / "memory"
    if repo_memory.exists():
        return repo_memory.resolve()

    return home_memory.resolve()


def positive_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError:
        value = default
    return max(minimum, value)


def load_settings() -> Settings:
    repo_root = discover_repo_root()
    memory_root = discover_memory_root(repo_root)
    system_dir = memory_root / "logs/system"

    return Settings(
        repo_root=repo_root,
        memory_root=memory_root,
        log_path=system_dir / "absorb_runner.log",
        status_path=system_dir / "absorb_runner_status.json",
        lock_path=system_dir / ".absorb_runner.lock",
        timeout_seconds=positive_int(
            "CONSENSUS_ABSORB_TIMEOUT_SECONDS", 900
        ),
        retries=positive_int("CONSENSUS_ABSORB_RETRIES", 3),
        retry_delay=positive_int(
            "CONSENSUS_ABSORB_RETRY_DELAY", 15, minimum=0
        ),
        max_log_bytes=positive_int(
            "CONSENSUS_ABSORB_MAX_LOG_BYTES", 1_000_000
        ),
    )


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def rotate_log(path: Path, max_bytes: int) -> None:
    try:
        if not path.exists() or path.stat().st_size < max_bytes:
            return
        rotated = path.with_suffix(path.suffix + ".1")
        if rotated.exists():
            rotated.unlink()
        path.replace(rotated)
    except OSError:
        pass


def append_log(settings: Settings, message: str) -> None:
    ensure_parent(settings.log_path)
    rotate_log(settings.log_path, settings.max_log_bytes)
    line = f"{iso_now()} {message.rstrip()}\n"
    with settings.log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def atomic_json_write(path: Path, payload: dict[str, object]) -> None:
    ensure_parent(path)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def executable_command_for_python(script: Path) -> list[str]:
    return [sys.executable, str(script)]


def discover_worker(settings: Settings) -> list[str] | None:
    configured = os.getenv("CONSENSUS_ABSORB_COMMAND", "").strip()
    if configured:
        return shlex.split(configured)

    candidates = [
        settings.repo_root / "agents/absorb_agent.py",
        settings.repo_root / "agents/absorption_agent.py",
        settings.repo_root / "agents/memory_absorb_agent.py",
        settings.repo_root / "agents/memory_absorber.py",
        settings.repo_root / "agents/absorb.py",
        settings.repo_root / "scripts/absorb_runner.sh",
        settings.repo_root / "scripts/absorb.sh",
        settings.repo_root / "scripts/run_absorb.sh",
        settings.repo_root / "bin/absorb",
    ]

    this_file = Path(__file__).resolve()

    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue

        if resolved == this_file or not candidate.is_file():
            continue

        if candidate.suffix == ".py":
            return executable_command_for_python(candidate)

        if os.access(candidate, os.X_OK):
            return [str(candidate)]

        if candidate.suffix == ".sh":
            return ["bash", str(candidate)]

    return None


def command_display(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def validate_command(command: Sequence[str], settings: Settings) -> str | None:
    if not command:
        return "The absorption command is empty."

    first = command[0]
    if "/" in first:
        executable = Path(first).expanduser()
        if not executable.exists():
            return f"Executable does not exist: {executable}"
    elif shutil.which(first) is None:
        return f"Executable is not available on PATH: {first}"

    if len(command) >= 2 and command[1].endswith((".py", ".sh")):
        candidate = Path(command[1]).expanduser()
        if not candidate.is_absolute():
            candidate = settings.repo_root / candidate
        if not candidate.exists():
            return f"Worker script does not exist: {candidate}"

    return None


def run_once(
    command: Sequence[str],
    settings: Settings,
    attempt: int,
) -> tuple[bool, int | None, str, float]:
    started = time.monotonic()
    append_log(
        settings,
        f"START version={VERSION} attempt={attempt}/{settings.retries} "
        f"command={command_display(command)}",
    )

    try:
        completed = subprocess.run(
            list(command),
            cwd=settings.repo_root,
            text=True,
            capture_output=True,
            timeout=settings.timeout_seconds,
            env=os.environ.copy(),
            check=False,
        )
        duration = time.monotonic() - started

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()

        if stdout:
            for line in stdout.splitlines():
                append_log(settings, f"STDOUT {line}")
        if stderr:
            for line in stderr.splitlines():
                append_log(settings, f"STDERR {line}")

        if completed.returncode == 0:
            append_log(
                settings,
                f"SUCCESS attempt={attempt} exit=0 "
                f"duration_seconds={duration:.2f}",
            )
            return True, 0, "", duration

        error = (
            f"Worker exited with status {completed.returncode}."
            + (f" Last stderr: {stderr.splitlines()[-1]}" if stderr else "")
        )
        append_log(
            settings,
            f"FAIL attempt={attempt} exit={completed.returncode} "
            f"duration_seconds={duration:.2f} error={error}",
        )
        return False, completed.returncode, error, duration

    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - started
        error = (
            f"Worker timed out after {settings.timeout_seconds} seconds."
        )
        append_log(
            settings,
            f"TIMEOUT attempt={attempt} "
            f"duration_seconds={duration:.2f} error={error}",
        )
        if exc.stdout:
            for line in str(exc.stdout).splitlines():
                append_log(settings, f"STDOUT {line}")
        if exc.stderr:
            for line in str(exc.stderr).splitlines():
                append_log(settings, f"STDERR {line}")
        return False, None, error, duration

    except OSError as exc:
        duration = time.monotonic() - started
        error = f"Unable to launch worker: {exc}"
        append_log(
            settings,
            f"ERROR attempt={attempt} "
            f"duration_seconds={duration:.2f} error={error}",
        )
        return False, None, error, duration


def write_status(
    settings: Settings,
    *,
    status: str,
    command: Sequence[str] | None,
    attempts: int,
    exit_code: int | None,
    duration_seconds: float,
    error: str,
) -> None:
    payload: dict[str, object] = {
        "version": VERSION,
        "generated_utc": iso_now(),
        "status": status,
        "repo_root": str(settings.repo_root),
        "memory_root": str(settings.memory_root),
        "log_path": str(settings.log_path),
        "command": list(command) if command else None,
        "attempts": attempts,
        "exit_code": exit_code,
        "duration_seconds": round(duration_seconds, 3),
        "error": error or None,
    }
    atomic_json_write(settings.status_path, payload)


def acquire_lock(settings: Settings):
    ensure_parent(settings.lock_path)
    lock_handle = settings.lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_handle.close()
        return None
    return lock_handle


def main() -> int:
    settings = load_settings()
    ensure_parent(settings.log_path)

    lock_handle = acquire_lock(settings)
    if lock_handle is None:
        append_log(
            settings,
            "SKIP another absorb runner instance already holds the lock",
        )
        print("Another absorb runner instance is already running.")
        return 0

    try:
        command = discover_worker(settings)

        if command is None:
            error = (
                "No absorption worker was found. Set "
                "CONSENSUS_ABSORB_COMMAND to the real project command, for "
                "example: export CONSENSUS_ABSORB_COMMAND="
                "'python3 agents/absorb_agent.py'"
            )
            append_log(settings, f"ERROR {error}")
            write_status(
                settings,
                status="ERROR",
                command=None,
                attempts=0,
                exit_code=None,
                duration_seconds=0.0,
                error=error,
            )
            print(error, file=sys.stderr)
            return 2

        validation_error = validate_command(command, settings)
        if validation_error:
            append_log(settings, f"ERROR {validation_error}")
            write_status(
                settings,
                status="ERROR",
                command=command,
                attempts=0,
                exit_code=None,
                duration_seconds=0.0,
                error=validation_error,
            )
            print(validation_error, file=sys.stderr)
            return 2

        total_duration = 0.0
        final_exit_code: int | None = None
        final_error = ""

        for attempt in range(1, settings.retries + 1):
            success, exit_code, error, duration = run_once(
                command, settings, attempt
            )
            total_duration += duration
            final_exit_code = exit_code
            final_error = error

            if success:
                write_status(
                    settings,
                    status="OK",
                    command=command,
                    attempts=attempt,
                    exit_code=0,
                    duration_seconds=total_duration,
                    error="",
                )
                print(
                    f"Absorption completed successfully in "
                    f"{total_duration:.2f} seconds."
                )
                print(f"Log: {settings.log_path}")
                return 0

            if attempt < settings.retries and settings.retry_delay:
                append_log(
                    settings,
                    f"RETRY sleeping_seconds={settings.retry_delay}",
                )
                time.sleep(settings.retry_delay)

        write_status(
            settings,
            status="ERROR",
            command=command,
            attempts=settings.retries,
            exit_code=final_exit_code,
            duration_seconds=total_duration,
            error=final_error,
        )
        print(
            f"Absorption failed after {settings.retries} attempts: "
            f"{final_error}",
            file=sys.stderr,
        )
        print(f"Log: {settings.log_path}", file=sys.stderr)
        return 1

    finally:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        finally:
            lock_handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
