#!/usr/bin/env python3
"""
tools/console_guard.py

Goal:
  Prevent PythonAnywhere consoles from crashing due to output flooding.

Behavior:
  - Runs a command.
  - Streams combined stdout+stderr to a logfile (FULL output).
  - Prints ONLY a bounded tail to the console.
  - Optional heartbeat so "silent" commands don’t look stuck.
  - Enforces a hard timeout and kills the whole process group on timeout.

Usage:
  python3 tools/console_guard.py -- python3 tools/core_monitors_bundle.py --dry-run

  python3 tools/console_guard.py --timeout 40 --max-bytes 12000 \
    --log /home/rafa1215/memory/logs/system/exec/guarded.log -- \
    bash -lc 'git grep -nEi "geofence|absorb|gmail" -- . || true'
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import fcntl  # POSIX (PythonAnywhere)
except Exception:  # pragma: no cover
    fcntl = None  # type: ignore


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(15):
        if (cur / ".git").exists() or (cur / "pyproject.toml").exists() or (cur / "setup.cfg").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()


def default_log_path() -> Path:
    root = find_project_root(Path.cwd())
    log_dir = root / "memory" / "logs" / "system" / "exec"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / f"console_guard_{ts}.log"
    except Exception:
        return Path("/tmp") / f"console_guard_{ts}.log"


class TailBuffer:
    """Keep last N bytes appended (raw bytes)."""

    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max(0, int(max_bytes))
        self._chunks: deque[bytes] = deque()
        self._size = 0

    def append(self, b: bytes) -> None:
        if self.max_bytes <= 0 or not b:
            return
        self._chunks.append(b)
        self._size += len(b)
        while self._size > self.max_bytes and self._chunks:
            left = self._chunks[0]
            overflow = self._size - self.max_bytes
            if overflow >= len(left):
                self._chunks.popleft()
                self._size -= len(left)
            else:
                self._chunks[0] = left[overflow:]
                self._size -= overflow
                break

    def get(self) -> bytes:
        if not self._chunks:
            return b""
        if len(self._chunks) == 1:
            return self._chunks[0]
        return b"".join(self._chunks)


def write_log_header(lf, cmd: list[str], cwd: str) -> None:
    lf.write(b"\n" + (b"=" * 80) + b"\n")
    lf.write(f"[{utc_iso()}] console_guard START\n".encode("utf-8"))
    lf.write(f"cmd: {cmd}\n".encode("utf-8"))
    lf.write(f"cwd: {cwd}\n".encode("utf-8"))
    lf.flush()


def write_log_footer(lf, rc: int, timed_out: bool) -> None:
    lf.write((b"=" * 80) + b"\n")
    lf.write(f"[{utc_iso()}] console_guard END rc={rc} timed_out={timed_out}\n".encode("utf-8"))
    lf.flush()


def set_nonblocking(fileobj) -> None:
    if fcntl is None:
        return
    try:
        fd = fileobj.fileno()
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    except Exception:
        return


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--log", default=None, help="Log file path (default: auto under memory/logs/system/exec)")
    ap.add_argument("--max-bytes", type=int, default=int(os.getenv("CONSOLE_GUARD_MAX_BYTES", "120000")))
    ap.add_argument("--timeout", type=int, default=int(os.getenv("CONSOLE_GUARD_TIMEOUT", "900")))
    ap.add_argument("--heartbeat", type=float, default=float(os.getenv("CONSOLE_GUARD_HEARTBEAT", "0")))
    ap.add_argument("--cwd", default=None, help="Working directory (default: current directory)")
    ap.add_argument("--no-tail", action="store_true", help="Do not print tail to console")
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="Command after --")
    return ap.parse_args(argv)


def normalize_cmd(cmd: list[str]) -> list[str]:
    if not cmd:
        return []
    if cmd[0] == "--":
        return cmd[1:]
    return cmd


def kill_process_group(proc: subprocess.Popen) -> None:
    """Best-effort kill of the entire process group."""
    try:
        pgid = os.getpgid(proc.pid)
        os.killpg(pgid, signal.SIGTERM)
        time.sleep(0.3)
        os.killpg(pgid, signal.SIGKILL)
    except Exception:
        try:
            proc.terminate()
            time.sleep(0.2)
            proc.kill()
        except Exception:
            pass


def main() -> int:
    args = parse_args(sys.argv[1:])
    cmd = normalize_cmd(args.cmd)
    if not cmd:
        print("Usage: python3 tools/console_guard.py -- <command> [args...]", file=sys.stderr)
        return 2

    cwd = args.cwd or os.getcwd()
    log_path = Path(args.log) if args.log else default_log_path()
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    print(f"[console_guard] start {utc_iso()}")
    print(f"[console_guard] log={log_path}")
    print(f"[console_guard] timeout={args.timeout}s tail_max={args.max_bytes}B heartbeat={args.heartbeat}s cmd={cmd}")

    tail = TailBuffer(args.max_bytes)
    timed_out = False

    # Start in a new session so we can kill the whole group on timeout.
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
        start_new_session=True,
    )

    assert proc.stdout is not None
    set_nonblocking(proc.stdout)
    fd = proc.stdout.fileno()

    start = time.monotonic()
    last_beat = start
    last_read = start

    with open(log_path, "ab") as lf:
        write_log_header(lf, cmd, cwd)

        try:
            while True:
                now = time.monotonic()

                # Heartbeat
                if args.heartbeat and (now - last_beat) >= args.heartbeat:
                    msg = f"[console_guard] heartbeat {utc_iso()} rc={proc.poll()}\n"
                    # keep heartbeat small and safe
                    if not args.no_tail:
                        sys.stdout.write(msg)
                        sys.stdout.flush()
                    lf.write(msg.encode("utf-8"))
                    lf.flush()
                    last_beat = now

                # Timeout
                if args.timeout > 0 and (now - start) > args.timeout:
                    timed_out = True
                    kill_process_group(proc)
                    break

                # Read available bytes (nonblocking)
                try:
                    data = os.read(fd, 65536)
                except BlockingIOError:
                    data = b""
                except OSError:
                    data = b""

                if data:
                    last_read = now
                    lf.write(data)
                    lf.flush()
                    tail.append(data)
                else:
                    rc = proc.poll()
                    # If process ended and we've had a short quiet period, stop.
                    if rc is not None and (now - last_read) > 0.2:
                        break
                    time.sleep(0.02)

        except KeyboardInterrupt:
            # Forward Ctrl-C style stop to the group, then exit 130
            kill_process_group(proc)
            write_log_footer(lf, 130, False)
            if not args.no_tail:
                print("\n[console_guard] interrupted (Ctrl-C). Log kept at:", log_path)
            return 130

        rc = proc.poll()
        if timed_out:
            rc = rc if rc is not None else 124  # timeout-style code
        elif rc is None:
            rc = 1

        write_log_footer(lf, int(rc), timed_out)

    if not args.no_tail:
        print("---- console_guard (safe tail) ----")
        out = tail.get().decode("utf-8", errors="replace")
        # Ensure tail ends with newline for clean prompt
        sys.stdout.write(out if out.endswith("\n") or out == "" else out + "\n")
        print(f"[log saved at] {log_path}")
        print(f"[status] exit={int(rc)} timed_out={timed_out}")

    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())
