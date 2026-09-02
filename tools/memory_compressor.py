#!/usr/bin/env python3
"""
memory_compressor.py
AI Consensus System — safe non-destructive memory summarizer.

Rules:
- NEVER moves, renames, or deletes source logs.
- Runs at most once per 20 hours unless --force is supplied.
- Rotates ONLY compressed_memory.md at 40 MB.
- Bounded reads prevent giant logs from exhausting resources.
- Fatal failures return non-zero.
"""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

BASE = Path("/home/rafa1215/consensus-project/memory/logs")
ARCHIVE_DIR = BASE / "archive"
SUMMARY_FILE = BASE / "compressed_memory.md"
HEARTBEAT_FILE = BASE / "system" / "heartbeat.md"
STATE_FILE = BASE / "system" / "memory_compressor_state.json"

MAX_SUMMARY_BYTES = 40 * 1024 * 1024
MAX_SOURCE_READ_BYTES = 256 * 1024
MIN_INTERVAL_SECONDS = 20 * 60 * 60

ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def heartbeat_log(status: str):
    ts = now().strftime("%Y-%m-%d %H:%M:%S UTC")
    with HEARTBEAT_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] MEMORY-COMPRESS: {status}\n")


def load_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(data):
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


def due(force=False):
    if force:
        return True

    state = load_state()
    last = state.get("last_success_utc")
    if not last:
        return True

    try:
        previous = datetime.datetime.fromisoformat(
            last.replace("Z", "+00:00")
        )
        return (now() - previous).total_seconds() >= MIN_INTERVAL_SECONDS
    except Exception:
        return True


def rotate_summary_if_needed():
    if (
        SUMMARY_FILE.exists()
        and SUMMARY_FILE.stat().st_size >= MAX_SUMMARY_BYTES
    ):
        ts = now().strftime("%Y%m%d_%H%M%S")
        destination = ARCHIVE_DIR / f"compressed_memory_{ts}.md"
        SUMMARY_FILE.rename(destination)
        heartbeat_log(
            f"Rotated summary to {destination.name}"
        )


def bounded_text(path: Path):
    size = path.stat().st_size

    if size <= MAX_SOURCE_READ_BYTES:
        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    half = MAX_SOURCE_READ_BYTES // 2

    with path.open("rb") as f:
        first = f.read(half)
        f.seek(max(0, size - half))
        last = f.read(half)

    return (
        first.decode("utf-8", errors="ignore")
        + "\n...[bounded read of large file]...\n"
        + last.decode("utf-8", errors="ignore")
    )


def summarize_text(text: str, max_lines=5):
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return "- (empty log)"

    if len(lines) <= max_lines:
        return "\n".join(lines)

    return "\n".join(
        lines[:2] + ["..."] + lines[-2:]
    )


def candidate_files():
    for path in BASE.rglob("*.md"):
        if not path.is_file():
            continue

        if path == SUMMARY_FILE:
            continue

        # Archive is historical storage, not active input.
        if ARCHIVE_DIR in path.parents:
            continue

        yield path


def compress_logs(force=False):
    if not due(force):
        heartbeat_log(
            "Skipped; successful compression performed within 20 hours"
        )
        return

    rotate_summary_if_needed()

    today = now().strftime("%Y-%m-%d")
    count = 0
    errors = 0

    with SUMMARY_FILE.open("a", encoding="utf-8") as output:
        output.write(
            f"\n# Memory Compression {today}\n"
        )

        for log_file in candidate_files():
            try:
                text = bounded_text(log_file)
                summary = summarize_text(text)

                output.write(
                    f"\n## {log_file.relative_to(BASE)}\n"
                )
                output.write(summary + "\n")

                count += 1

            except Exception as exc:
                errors += 1
                output.write(
                    f"\n- ERROR summarizing "
                    f"{log_file}: {exc}\n"
                )

    save_state({
        "last_success_utc": now().isoformat(),
        "files_summarized": count,
        "file_errors": errors,
    })

    heartbeat_log(
        f"Memory compression complete; "
        f"files={count} errors={errors}; "
        f"sources preserved"
    )


def main():
    force = "--force" in sys.argv

    try:
        compress_logs(force=force)
        return 0

    except Exception as exc:
        heartbeat_log(
            f"ERROR: Memory compressor crashed — {exc}"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
