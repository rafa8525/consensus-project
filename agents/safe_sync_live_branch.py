#!/usr/bin/env python3
"""Canonical safe synchronization for the live PythonAnywhere v1.1-dev checkout.

This is the single branch-sync implementation used by ACS-01 and the health
bridge. It never rebases, force-resets, force-pushes, or overwrites genuine
local source/config edits.

Expected runtime-generated tracked changes are preserved exactly across a
fast-forward by stashing them, advancing the branch, then restoring their
working-tree contents from the stash snapshot.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "consensus-project"
BRANCH = "v1.1-dev"
REMOTE = f"origin/{BRANCH}"

RUNTIME_PREFIXES = (
    "memory/logs/",
    "memory/agents/",
    "memory/exports/",
)
RUNTIME_FILES = {
    "memory/centralized_knowledge_base.txt",
    "memory/security_audit_schedule.txt",
}


def run(*args: str, timeout: int = 180, text: bool = True):
    return subprocess.run(
        list(args),
        cwd=REPO,
        capture_output=True,
        text=text,
        timeout=timeout,
        check=False,
    )


def classify_changes():
    status = run("git", "status", "--porcelain=v1", "-uno", timeout=120)
    if status.returncode != 0:
        raise RuntimeError(status.stderr.strip() or "git status failed")

    runtime = []
    meaningful = []

    for raw in status.stdout.splitlines():
        if not raw:
            continue
        path = raw[3:].strip()
        if path in RUNTIME_FILES or any(path.startswith(p) for p in RUNTIME_PREFIXES):
            runtime.append(path)
        else:
            meaningful.append(path)

    return sorted(set(runtime)), sorted(set(meaningful))


def blob_sha(ref: str, path: str) -> str | None:
    p = run("git", "rev-parse", "--verify", f"{ref}:{path}", timeout=60)
    return p.stdout.strip() if p.returncode == 0 else None


def local_blob_sha(path: str) -> str | None:
    p = REPO / path
    if not p.exists():
        return None
    r = run("git", "hash-object", "--", path, timeout=60)
    return r.stdout.strip() if r.returncode == 0 else None


def divergence():
    p = run("git", "rev-list", "--left-right", "--count", f"HEAD...{REMOTE}")
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "divergence check failed")
    ahead, behind = map(int, p.stdout.strip().split())
    return ahead, behind


def restore_runtime_from_stash(stash_ref: str, paths: list[str]):
    restored = []
    deleted = []

    for path in paths:
        show = run("git", "show", f"{stash_ref}:{path}", timeout=60, text=False)
        target = REPO / path
        if show.returncode == 0:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(show.stdout)
            restored.append(path)
        else:
            try:
                target.unlink()
                deleted.append(path)
            except FileNotFoundError:
                deleted.append(path)

    return restored, deleted


def main() -> int:
    result = {
        "ok": False,
        "status": "unknown",
        "branch": BRANCH,
        "remote": REMOTE,
        "timestamp": time.time(),
    }

    try:
        branch = run("git", "branch", "--show-current")
        current_branch = branch.stdout.strip()
        if current_branch != BRANCH:
            result.update({
                "status": "wrong_branch",
                "current_branch": current_branch or "(detached)",
            })
            print(json.dumps(result))
            return 2

        fetch = run("git", "fetch", "--quiet", "origin", BRANCH, timeout=180)
        if fetch.returncode != 0:
            result.update({
                "status": "fetch_failed",
                "stderr": fetch.stderr[-1200:],
            })
            print(json.dumps(result))
            return 3

        ahead, behind = divergence()
        result["ahead_before"] = ahead
        result["behind_before"] = behind

        if ahead > 0:
            result.update({
                "status": "local_commits_present",
                "message": "Automatic sync blocked because live branch has local commits.",
            })
            print(json.dumps(result))
            return 2

        runtime_changes, meaningful_changes = classify_changes()
        result["runtime_changes_preserved"] = runtime_changes

        safe_refresh = []
        unsafe = []

        for path in meaningful_changes:
            remote_sha = blob_sha(REMOTE, path)
            local_sha = local_blob_sha(path)

            if remote_sha is None:
                unsafe.append(path)
            elif local_sha is None or local_sha == remote_sha:
                # Missing local tracked source, or file already copied from
                # remote while HEAD remained behind. Both are safe to clean
                # back to HEAD before the fast-forward.
                safe_refresh.append(path)
            else:
                unsafe.append(path)

        if unsafe:
            result.update({
                "status": "blocked_local_source_changes",
                "unsafe_paths": unsafe[:50],
                "safe_refresh_paths": safe_refresh,
            })
            print(json.dumps(result))
            return 2

        for path in safe_refresh:
            restore = run("git", "restore", "--source=HEAD", "--", path, timeout=60)
            if restore.returncode != 0:
                result.update({
                    "status": "source_restore_failed",
                    "path": path,
                    "stderr": restore.stderr[-1200:],
                })
                print(json.dumps(result))
                return 3

        stash_ref = None
        if runtime_changes:
            message = f"acs-safe-sync-{int(time.time())}"
            stash = run(
                "git", "stash", "push", "-m", message, "--",
                *runtime_changes,
                timeout=300,
            )
            if stash.returncode != 0:
                result.update({
                    "status": "runtime_stash_failed",
                    "stderr": stash.stderr[-1200:],
                })
                print(json.dumps(result))
                return 3

            top = run("git", "stash", "list", "-1", "--format=%gd")
            stash_ref = top.stdout.strip() or None
            if not stash_ref:
                result.update({
                    "status": "runtime_stash_missing",
                })
                print(json.dumps(result))
                return 3

        try:
            if behind > 0:
                ff = run("git", "merge", "--ff-only", REMOTE, timeout=300)
                if ff.returncode != 0:
                    result.update({
                        "status": "fast_forward_failed",
                        "stderr": ff.stderr[-1500:],
                    })
                    print(json.dumps(result))
                    return 3
        finally:
            if stash_ref:
                restored, deleted = restore_runtime_from_stash(stash_ref, runtime_changes)
                result["runtime_restored"] = restored
                result["runtime_deleted"] = deleted
                drop = run("git", "stash", "drop", stash_ref, timeout=60)
                if drop.returncode != 0:
                    result["stash_drop_warning"] = drop.stderr[-1000:]

        ahead_after, behind_after = divergence()
        head = run("git", "rev-parse", "--short", "HEAD").stdout.strip()
        remote_head = run("git", "rev-parse", "--short", REMOTE).stdout.strip()

        result.update({
            "ok": ahead_after == 0 and behind_after == 0,
            "status": "synced" if ahead_after == 0 and behind_after == 0 else "sync_incomplete",
            "safe_refresh_paths": safe_refresh,
            "ahead_after": ahead_after,
            "behind_after": behind_after,
            "head": head,
            "remote_head": remote_head,
        })
        print(json.dumps(result))
        return 0 if result["ok"] else 3

    except Exception as exc:
        result.update({
            "status": "execution_failure",
            "error_type": type(exc).__name__,
            "error": str(exc)[:1200],
        })
        print(json.dumps(result))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
