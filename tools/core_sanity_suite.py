#!/usr/bin/env python3
# ACS_READ_ONLY_SANITY_V1
"""Read-only AI Consensus health and source-integrity checks."""

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "tools/core_sanity_suite.py",
    "tools/git_auto_commit.py",
    "tools/verify_logs_tree.py",
    "agents/absorb_runner.py",
    "tools/master_control_loop.py",
]

def git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )

def main():
    failed = False

    for name in FILES:
        path = ROOT / name
        try:
            ast.parse(path.read_text(), filename=name)
            print(f"PASS syntax: {name}")
        except (OSError, SyntaxError, UnicodeError) as exc:
            print(f"FAIL syntax: {name}: {exc}")
            failed = True

    try:
        result = git("rev-parse", "--is-inside-work-tree")
        ok = result.returncode == 0 and result.stdout.strip() == "true"
        print(f'{"PASS" if ok else "FAIL"} Git repository accessible')
        failed |= not ok

        if ok:
            result = git("status", "--porcelain", "--untracked-files=no")
            if result.returncode:
                print("FAIL Git status check")
                failed = True
            else:
                changes = result.stdout.splitlines()
                staged = sum(
                    bool(line) and line[0] not in (" ", "?")
                    for line in changes
                )
                print(
                    f"INFO tracked changes: {len(changes)}; "
                    f"staged: {staged}"
                )
                if staged:
                    print("WARN staged files require manual review")

    except (subprocess.SubprocessError, OSError) as exc:
        print(f"FAIL Git health check: {exc}")
        failed = True

    kb = ROOT / "memory/centralized_knowledge_base.txt"

    try:
        ok = kb.is_file() and kb.stat().st_size > 0
    except OSError:
        ok = False

    print(
        f'{"PASS" if ok else "FAIL"} '
        "Knowledge base exists and is nonempty"
    )
    failed |= not ok

    print("OVERALL:", "FAIL" if failed else "PASS")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
