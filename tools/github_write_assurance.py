#!/usr/bin/env python3
"""
github_write_assurance.py
One-time durable GitHub write/mirror assurance agent for Rafael's AI Consensus System.

Flow:
  canonical memory (/home/rafa1215/memory)
  -> repo mirror (/home/rafa1215/consensus-project/memory)
  -> git add -A
  -> commit
  -> push origin v1.1-dev
  -> verify remote
  -> write committed proof files

Safe by default:
  - skips secrets, env files, keys, caches, databases, zips, venvs, and large files
  - skips broken symlinks as warnings, not failures
  - never follows symlink directories
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

AGENT_VERSION = "github_write_assurance.py v2026-05-15-clean-final-proof-v3"
DEFAULT_REPO = Path("/home/rafa1215/consensus-project")
DEFAULT_MEMORY = Path("/home/rafa1215/memory")
DEFAULT_BRANCH = "v1.1-dev"
MAX_FILE_BYTES = 10 * 1024 * 1024

SKIP_DIR_NAMES = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".venv", "venv", "env", "node_modules", ".cache", "cache", "tmp", "temp",
    "backups", "backup_zips",
}
SKIP_SUFFIXES = {
    ".env", ".key", ".pem", ".p12", ".pfx", ".crt", ".cer", ".sqlite",
    ".sqlite3", ".db", ".zip", ".tar", ".gz", ".7z", ".rar", ".pyc",
}
SKIP_NAME_PARTS = {
    "secret", "secrets", "credential", "credentials", "token", "tokens",
    "private_key", "client_secret", "oauth", "password", "passwd",
    "twilio_auth", "api_key",
}


@dataclass
class Result:
    status: str
    generated_utc: str
    agent: str
    repo_root: str
    memory_root: str
    expected_branch: str
    actual_branch: str
    dry_run: bool
    push_enabled: bool
    mirrored_files_copied: int = 0
    mirrored_files_skipped_safety: int = 0
    mirrored_broken_symlinks_skipped: int = 0
    stale_repo_files_removed: int = 0
    commit_created: bool = False
    commit_hash: str = ""
    final_proof_commit_hash: str = ""
    push_ok: bool = False
    remote_verified: bool = False
    git_status_after_run: str = ""
    warnings: list[str] | None = None
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run(cmd: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p


def git_output(repo: Path, args: list[str], check: bool = False) -> str:
    p = run(["git", *args], repo, check=check)
    return (p.stdout or p.stderr or "").strip()


def current_branch(repo: Path) -> str:
    return git_output(repo, ["rev-parse", "--abbrev-ref", "HEAD"]) or "UNKNOWN"


def git_status(repo: Path) -> str:
    out = git_output(repo, ["status", "--short"])
    return out if out else "clean"


def unsafe_path(rel: Path, src: Path) -> bool:
    parts_lower = [p.lower() for p in rel.parts]
    name_lower = src.name.lower()

    if any(part in SKIP_DIR_NAMES for part in parts_lower[:-1]):
        return True
    if name_lower in {".env", ".env.local", ".env.production", ".netrc"}:
        return True
    if src.suffix.lower() in SKIP_SUFFIXES:
        return True
    if any(marker in name_lower for marker in SKIP_NAME_PARTS):
        return True

    try:
        if src.is_file() and src.stat().st_size > MAX_FILE_BYTES:
            return True
    except OSError:
        return True

    return False


def iter_memory_files(memory_root: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(memory_root, topdown=True, followlinks=False):
        root_path = Path(root)

        kept_dirs = []
        for d in dirs:
            p = root_path / d
            rel = p.relative_to(memory_root)
            if p.is_symlink() or unsafe_path(rel, p):
                continue
            kept_dirs.append(d)
        dirs[:] = kept_dirs

        for f in files:
            yield root_path / f


def mirror_memory(memory_root: Path, repo_root: Path, res: Result) -> None:
    repo_memory = repo_root / "memory"
    repo_memory.mkdir(parents=True, exist_ok=True)

    for src in iter_memory_files(memory_root):
        try:
            rel = src.relative_to(memory_root)
        except ValueError:
            continue

        if src.is_symlink():
            if not src.exists():
                res.mirrored_broken_symlinks_skipped += 1
                res.warnings.append(f"skipped broken symlink: {src}")
                continue
            res.mirrored_files_skipped_safety += 1
            res.warnings.append(f"skipped symlink file: {src}")
            continue

        if unsafe_path(rel, src):
            res.mirrored_files_skipped_safety += 1
            continue

        dst = repo_memory / rel
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            res.mirrored_files_copied += 1
        except FileNotFoundError as e:
            res.warnings.append(f"skipped disappearing file: {src}: {e}")
        except Exception as e:
            res.errors.append(f"mirror error for {src}: {e}")

    for dst in list(repo_memory.rglob("*")):
        if not dst.is_file() or dst.is_symlink():
            continue
        try:
            rel = dst.relative_to(repo_memory)
        except ValueError:
            continue
        if unsafe_path(rel, dst):
            continue
        src = memory_root / rel
        if not src.exists():
            try:
                dst.unlink()
                res.stale_repo_files_removed += 1
            except Exception as e:
                res.warnings.append(f"could not remove stale repo mirror file {dst}: {e}")


def render_markdown(res: Result) -> str:
    lines = [
        "# GitHub Write Assurance",
        "",
        f"- Status: {res.status}",
        f"- Generated UTC: {res.generated_utc}",
        f"- Agent: {res.agent}",
        f"- Repo root: `{res.repo_root}`",
        f"- Memory root: `{res.memory_root}`",
        f"- Expected branch: `{res.expected_branch}`",
        f"- Actual branch: `{res.actual_branch}`",
        f"- Dry run: `{str(res.dry_run).lower()}`",
        f"- Push enabled: `{str(res.push_enabled).lower()}`",
        "",
        "## Proof",
        f"- Mirrored files copied: {res.mirrored_files_copied}",
        f"- Mirrored files skipped by safety rules: {res.mirrored_files_skipped_safety}",
        f"- Broken symlinks skipped safely: {res.mirrored_broken_symlinks_skipped}",
        f"- Stale repo mirror files removed: {res.stale_repo_files_removed}",
        f"- Commit created: `{str(res.commit_created).lower()}`",
        f"- Commit hash: `{res.commit_hash}`",
        f"- Final proof commit hash: `{res.final_proof_commit_hash}`",
        f"- Push OK: `{str(res.push_ok).lower()}`",
        f"- Remote verified: `{str(res.remote_verified).lower()}`",
        "",
        "## Git status after run",
        "```text",
        res.git_status_after_run or "unknown",
        "```",
    ]

    if res.warnings:
        lines += ["", "## Warnings"]
        lines += [f"- {w}" for w in res.warnings[:50]]
        if len(res.warnings) > 50:
            lines.append(f"- ... {len(res.warnings) - 50} more warnings omitted from markdown; see JSON.")

    if res.errors:
        lines += ["", "## Errors"]
        lines += [f"- {e}" for e in res.errors]

    return "\n".join(lines) + "\n"


def write_proof_files(repo_root: Path, memory_root: Path, res: Result) -> None:
    status_dir = memory_root / "logs" / "status"
    repo_status_dir = repo_root / "memory" / "logs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    repo_status_dir.mkdir(parents=True, exist_ok=True)

    md = render_markdown(res)
    js = json.dumps(asdict(res), indent=2, sort_keys=True) + "\n"

    for base in (status_dir, repo_status_dir):
        (base / "github_write_assurance.md").write_text(md, encoding="utf-8")
        (base / "github_write_assurance.json").write_text(js, encoding="utf-8")


def commit_if_needed(repo: Path, message: str) -> tuple[bool, str]:
    run(["git", "add", "-A"], repo)

    if git_status(repo) == "clean":
        return False, git_output(repo, ["rev-parse", "HEAD"])

    p = run(["git", "commit", "-m", message], repo)
    if p.returncode != 0:
        raise RuntimeError(f"git commit failed\nstdout={p.stdout}\nstderr={p.stderr}")

    return True, git_output(repo, ["rev-parse", "HEAD"], check=True)


def push_and_verify(repo: Path, branch: str, push_enabled: bool, dry_run: bool) -> tuple[bool, bool, str]:
    head = git_output(repo, ["rev-parse", "HEAD"], check=True)

    if dry_run or not push_enabled:
        return False, False, head

    p = run(["git", "push", "origin", f"HEAD:{branch}"], repo)
    if p.returncode != 0:
        raise RuntimeError(f"git push failed\nstdout={p.stdout}\nstderr={p.stderr}")

    remote = git_output(repo, ["ls-remote", "origin", f"refs/heads/{branch}"], check=True)
    verified = bool(remote.split()) and remote.split()[0] == head
    return True, verified, head


def run_agent(repo_root: Path, memory_root: Path, branch: str, dry_run: bool, push_enabled: bool) -> Result:
    repo_root = repo_root.resolve()
    memory_root = memory_root.resolve()

    res = Result(
        status="ACTION REQUIRED",
        generated_utc=utc_now(),
        agent=AGENT_VERSION,
        repo_root=str(repo_root),
        memory_root=str(memory_root),
        expected_branch=branch,
        actual_branch="UNKNOWN",
        dry_run=dry_run,
        push_enabled=push_enabled,
    )

    if not repo_root.exists():
        res.errors.append(f"repo root missing: {repo_root}")
        return res

    if not memory_root.exists():
        res.errors.append(f"memory root missing: {memory_root}")
        return res

    try:
        res.actual_branch = current_branch(repo_root)

        if res.actual_branch != branch:
            res.errors.append(f"wrong branch: expected {branch}, got {res.actual_branch}")

        mirror_memory(memory_root, repo_root, res)

        if dry_run:
            res.git_status_after_run = git_status(repo_root)
            res.status = "OK" if not res.errors else "ACTION REQUIRED"
            write_proof_files(repo_root, memory_root, res)
            return res

        created, commit_hash = commit_if_needed(repo_root, "GitHub write assurance sync")
        res.commit_created = created
        res.commit_hash = commit_hash

        pushed, verified, _ = push_and_verify(repo_root, branch, push_enabled, dry_run)
        res.push_ok = pushed
        res.remote_verified = verified

        res.git_status_after_run = "pending final proof commit"
        res.status = "OK" if (not res.errors and res.push_ok and res.remote_verified) else "ACTION REQUIRED"
        write_proof_files(repo_root, memory_root, res)

        proof_created, proof_hash = commit_if_needed(repo_root, "Update GitHub write assurance proof")
        if proof_created:
            res.final_proof_commit_hash = proof_hash
            pushed2, verified2, _ = push_and_verify(repo_root, branch, push_enabled, dry_run)
            res.push_ok = res.push_ok and pushed2
            res.remote_verified = verified2

        res.git_status_after_run = git_status(repo_root)
        res.status = "OK" if (
            not res.errors
            and res.push_ok
            and res.remote_verified
            and res.git_status_after_run == "clean"
        ) else "ACTION REQUIRED"

        print(render_markdown(res), end="")
        return res

    except Exception as e:
        res.errors.append(str(e))
        res.git_status_after_run = git_status(repo_root) if repo_root.exists() else "unknown"
        res.status = "ACTION REQUIRED"
        try:
            write_proof_files(repo_root, memory_root, res)
        except Exception:
            pass
        print(render_markdown(res), end="")
        return res


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="gwa_selftest_") as td:
        base = Path(td)
        memory = base / "memory"
        repo = base / "repo"
        remote = base / "remote.git"

        memory.mkdir()
        repo.mkdir()

        (memory / "logs" / "status").mkdir(parents=True)
        (memory / "logs" / "status" / "ok.md").write_text("ok\n", encoding="utf-8")
        (memory / ".env").write_text("SECRET=1\n", encoding="utf-8")
        (memory / "token_file.txt").write_text("secret\n", encoding="utf-8")

        broken_dir = memory / "quarantine_symlinks"
        broken_dir.mkdir()

        try:
            (broken_dir / "broken.md").symlink_to(memory / "missing_target.md")
        except OSError:
            pass

        run(["git", "init", "--bare", str(remote)], base, check=True)
        run(["git", "init", "-b", "v1.1-dev"], repo, check=True)
        run(["git", "config", "user.email", "selftest@example.com"], repo, check=True)
        run(["git", "config", "user.name", "GWA Self Test"], repo, check=True)
        run(["git", "remote", "add", "origin", str(remote)], repo, check=True)

        (repo / "README.md").write_text("self test\n", encoding="utf-8")
        run(["git", "add", "README.md"], repo, check=True)
        run(["git", "commit", "-m", "init"], repo, check=True)
        run(["git", "push", "-u", "origin", "v1.1-dev"], repo, check=True)

        res = run_agent(repo, memory, "v1.1-dev", dry_run=False, push_enabled=True)

        assert res.status == "OK", render_markdown(res)
        assert res.push_ok, render_markdown(res)
        assert res.remote_verified, render_markdown(res)
        assert res.git_status_after_run == "clean", render_markdown(res)
        assert (repo / "memory" / "logs" / "status" / "ok.md").exists()
        assert not (repo / "memory" / ".env").exists()
        assert not res.errors, render_markdown(res)

        print("SELF-TEST OK")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Mirror canonical memory to repo, commit, push, and verify GitHub write assurance."
    )
    ap.add_argument("--repo", default=str(DEFAULT_REPO))
    ap.add_argument("--memory", default=str(DEFAULT_MEMORY))
    ap.add_argument("--branch", default=DEFAULT_BRANCH)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    if args.self_test:
        self_test()
        return 0

    res = run_agent(
        Path(args.repo),
        Path(args.memory),
        args.branch,
        args.dry_run,
        not args.no_push,
    )
    return 0 if res.status == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
