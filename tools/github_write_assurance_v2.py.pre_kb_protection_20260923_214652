#!/usr/bin/env python3
"""
github_write_assurance.py

Purpose:
  Make the AI Consensus System's important files reliably visible on GitHub by
  mirroring canonical memory into the repo, staging safe project paths, committing,
  pushing to v1.1-dev, verifying the remote, and writing a proof report.

Default paths:
  Canonical memory: /home/rafa1215/memory
  Repo root:        /home/rafa1215/consensus-project
  Branch:           v1.1-dev

Design goals:
  - Source of truth stays /home/rafa1215/memory.
  - Repo mirror stays /home/rafa1215/consensus-project/memory.
  - GitHub branch v1.1-dev becomes the verified remote mirror.
  - Broken symlinks, secrets, caches, databases, archives, and large files are skipped.
  - Final proof is committed and pushed, so a successful run ends clean.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

VERSION = "github_write_assurance.py v2026-05-15-v2-clean-proof"

DEFAULT_REPO_ROOT = Path("/home/rafa1215/consensus-project")
DEFAULT_MEMORY_ROOT = Path("/home/rafa1215/memory")
DEFAULT_BRANCH = "v1.1-dev"

STATUS_REL = Path("logs/status/github_write_assurance.md")
STATUS_JSON_REL = Path("logs/status/github_write_assurance.json")
REPO_STATUS_REL = Path("memory/logs/status/github_write_assurance.md")
REPO_STATUS_JSON_REL = Path("memory/logs/status/github_write_assurance.json")

MAX_FILE_BYTES_DEFAULT = 10 * 1024 * 1024

EXCLUDE_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".envdir",
    "site-packages",
    "dist",
    "build",
}

EXCLUDE_GLOBS = [
    ".env",
    ".env.*",
    "*.env",
    "*secret*",
    "*secrets*",
    "*credential*",
    "*credentials*",
    "*token*",
    "*apikey*",
    "*api_key*",
    "*private_key*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "*.db-wal",
    "*.db-shm",
    "*.pyc",
    "*.pyo",
    "*.zip",
    "*.tar",
    "*.tar.gz",
    "*.tgz",
    "*.7z",
    "*.rar",
    "*.log.tmp",
    "tmp_*",
]

DEFAULT_STAGE_PATHS = [
    "agents",
    "tools",
    "memory",
    "docs",
    "public",
    "config.yaml",
    "requirements.txt",
    "run_with_env.sh",
    "start_github_sync.sh",
]


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class AssuranceReport:
    version: str
    generated_utc: str
    repo_root: str
    memory_root: str
    branch_expected: str
    branch_actual: str = "unknown"
    dry_run: bool = False
    push_enabled: bool = True
    status: str = "unknown"
    mirror_files_copied: int = 0
    mirror_files_skipped: int = 0
    mirror_symlinks_skipped: int = 0
    mirror_errors: List[str] = field(default_factory=list)
    git_dirty_before: str = ""
    git_dirty_after: str = ""
    sync_commit_created: bool = False
    sync_commit_hash: str = ""
    proof_commit_created: bool = False
    proof_commit_hash: str = ""
    final_head: str = ""
    push_ok: bool = False
    remote_verified: bool = False
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_cmd(args: Sequence[str], cwd: Optional[Path] = None, timeout: int = 120, check: bool = False) -> CommandResult:
    proc = subprocess.run(
        list(args),
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    result = CommandResult(
        command=" ".join(args),
        returncode=proc.returncode,
        stdout=(proc.stdout or "").strip(),
        stderr=(proc.stderr or "").strip(),
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {result.command}\n"
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
    return result


def is_git_repo(repo_root: Path) -> bool:
    return (repo_root / ".git").exists()


def lower_name(path: Path) -> str:
    return path.name.lower()


def should_exclude(rel: Path, max_file_bytes: int, src_path: Optional[Path] = None) -> bool:
    parts_lower = [part.lower() for part in rel.parts]
    if any(part in EXCLUDE_DIR_NAMES for part in parts_lower):
        return True

    rel_s = rel.as_posix().lower()
    name = lower_name(rel)
    for pattern in EXCLUDE_GLOBS:
        pattern_lower = pattern.lower()
        if fnmatch.fnmatch(name, pattern_lower) or fnmatch.fnmatch(rel_s, pattern_lower):
            return True

    if src_path and src_path.is_file():
        try:
            if src_path.stat().st_size > max_file_bytes:
                return True
        except OSError:
            return True

    return False


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def files_differ(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return True
    try:
        if src.stat().st_size != dst.stat().st_size:
            return True
    except OSError:
        return True
    return sha256_file(src) != sha256_file(dst)


def mirror_memory(memory_root: Path, repo_root: Path, dry_run: bool, max_file_bytes: int) -> Tuple[int, int, int, List[str]]:
    copied = 0
    skipped = 0
    symlinks_skipped = 0
    errors: List[str] = []
    repo_memory = repo_root / "memory"

    if not memory_root.exists():
        errors.append(f"memory root missing: {memory_root}")
        return copied, skipped, symlinks_skipped, errors

    for src in memory_root.rglob("*"):
        try:
            rel = src.relative_to(memory_root)

            # Critical fix: do not try to copy symlinks. Broken quarantine symlinks
            # previously produced ACTION REQUIRED even when the GitHub push worked.
            if src.is_symlink():
                symlinks_skipped += 1
                continue

            if src.is_dir():
                if should_exclude(rel, max_file_bytes):
                    skipped += 1
                continue

            if should_exclude(rel, max_file_bytes, src):
                skipped += 1
                continue

            dst = repo_memory / rel
            if files_differ(src, dst):
                copied += 1
                if not dry_run:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"mirror error for {src}: {exc}")

    return copied, skipped, symlinks_skipped, errors


def git_status_porcelain(repo_root: Path) -> str:
    result = run_cmd(["git", "status", "--short"], cwd=repo_root, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or "git status failed")
    return result.stdout


def current_branch(repo_root: Path) -> str:
    result = run_cmd(["git", "branch", "--show-current"], cwd=repo_root, timeout=60)
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "detached"


def git_head(repo_root: Path) -> str:
    result = run_cmd(["git", "rev-parse", "HEAD"], cwd=repo_root, timeout=60)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def git_add_whitelist(repo_root: Path, stage_paths: Iterable[str]) -> None:
    existing_paths = [p for p in stage_paths if (repo_root / p).exists()]
    if not existing_paths:
        return
    # Critical fix: -A stages deletions too. That clears stale deleted-file status
    # such as memory/logs/fitness/*.md that remained after the prior version.
    run_cmd(["git", "add", "-A", "--"] + existing_paths, cwd=repo_root, timeout=180, check=True)


def git_add_specific(repo_root: Path, paths: Iterable[Path]) -> None:
    existing = []
    for p in paths:
        full = repo_root / p
        if full.exists() or full.parent.exists():
            existing.append(p.as_posix())
    if existing:
        run_cmd(["git", "add", "-A", "--"] + existing, cwd=repo_root, timeout=120, check=True)


def staged_diff_exists(repo_root: Path) -> bool:
    result = run_cmd(["git", "diff", "--cached", "--quiet"], cwd=repo_root, timeout=60)
    return result.returncode == 1


def commit_changes(repo_root: Path, message: str) -> str:
    run_cmd(["git", "commit", "-m", message], cwd=repo_root, timeout=240, check=True)
    return git_head(repo_root)


def push_branch(repo_root: Path, branch: str) -> Tuple[bool, str]:
    result = run_cmd(["git", "push", "origin", branch], cwd=repo_root, timeout=300)
    output = "\n".join(x for x in [result.stdout, result.stderr] if x)
    return result.returncode == 0, output.strip()


def verify_remote_head(repo_root: Path, branch: str, expected_head: str) -> bool:
    if not expected_head:
        return False
    result = run_cmd(["git", "ls-remote", "origin", f"refs/heads/{branch}"], cwd=repo_root, timeout=120)
    if result.returncode != 0 or not result.stdout:
        return False
    remote_hash = result.stdout.split()[0].strip()
    return remote_hash == expected_head


def render_markdown(report: AssuranceReport) -> str:
    status_label = "OK" if report.status == "ok" else "ACTION REQUIRED"
    lines = [
        "# GitHub Write Assurance",
        "",
        f"- Status: {status_label}",
        f"- Generated UTC: {report.generated_utc}",
        f"- Agent: {report.version}",
        f"- Repo root: `{report.repo_root}`",
        f"- Memory root: `{report.memory_root}`",
        f"- Expected branch: `{report.branch_expected}`",
        f"- Actual branch: `{report.branch_actual}`",
        f"- Dry run: `{str(report.dry_run).lower()}`",
        f"- Push enabled: `{str(report.push_enabled).lower()}`",
        "",
        "## Proof",
        "",
        f"- Mirrored files copied: {report.mirror_files_copied}",
        f"- Mirrored files skipped by safety rules: {report.mirror_files_skipped}",
        f"- Symlinks skipped safely: {report.mirror_symlinks_skipped}",
        f"- Sync commit created: `{str(report.sync_commit_created).lower()}`",
        f"- Sync commit hash: `{report.sync_commit_hash or 'none'}`",
        f"- Proof commit created: `{str(report.proof_commit_created).lower()}`",
        f"- Proof commit hash: `{report.proof_commit_hash or 'none'}`",
        f"- Final HEAD: `{report.final_head or 'none'}`",
        f"- Push OK: `{str(report.push_ok).lower()}`",
        f"- Remote verified: `{str(report.remote_verified).lower()}`",
        "",
        "## Git status after run",
        "",
        "```text",
        report.git_dirty_after or "clean",
        "```",
    ]
    if report.warnings:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in report.warnings]
    if report.errors or report.mirror_errors:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in report.errors + report.mirror_errors]
    lines.append("")
    return "\n".join(lines)


def write_status(report: AssuranceReport, memory_root: Path, repo_root: Path, dry_run: bool) -> None:
    if dry_run:
        return
    md = render_markdown(report)
    js = json.dumps(asdict(report), indent=2, sort_keys=True) + "\n"
    targets = [
        (memory_root / STATUS_REL, md),
        (memory_root / STATUS_JSON_REL, js),
        (repo_root / REPO_STATUS_REL, md),
        (repo_root / REPO_STATUS_JSON_REL, js),
    ]
    for path, content in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def commit_status_proof(report: AssuranceReport, repo_root: Path, memory_root: Path) -> None:
    write_status(report, memory_root, repo_root, dry_run=False)
    git_add_specific(repo_root, [REPO_STATUS_REL, REPO_STATUS_JSON_REL])
    if staged_diff_exists(repo_root):
        message = f"GitHub write assurance proof {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        report.proof_commit_hash = commit_changes(repo_root, message)
        report.proof_commit_created = True
    else:
        report.proof_commit_hash = git_head(repo_root)
        report.proof_commit_created = False


def run_assurance(
    repo_root: Path,
    memory_root: Path,
    branch: str,
    dry_run: bool,
    push_enabled: bool,
    max_file_bytes: int,
    stage_paths: Sequence[str],
) -> AssuranceReport:
    report = AssuranceReport(
        version=VERSION,
        generated_utc=utc_now(),
        repo_root=str(repo_root),
        memory_root=str(memory_root),
        branch_expected=branch,
        dry_run=dry_run,
        push_enabled=push_enabled,
    )

    try:
        if not repo_root.exists():
            report.errors.append(f"repo root missing: {repo_root}")
            report.status = "action_required"
            write_status(report, memory_root, repo_root, dry_run)
            return report
        if not is_git_repo(repo_root):
            report.errors.append(f"not a git repo: {repo_root}")
            report.status = "action_required"
            write_status(report, memory_root, repo_root, dry_run)
            return report

        report.branch_actual = current_branch(repo_root)
        if report.branch_actual != branch:
            report.errors.append(f"wrong branch: expected {branch}, got {report.branch_actual}")

        report.git_dirty_before = git_status_porcelain(repo_root)

        copied, skipped, symlinks_skipped, mirror_errors = mirror_memory(
            memory_root=memory_root,
            repo_root=repo_root,
            dry_run=dry_run,
            max_file_bytes=max_file_bytes,
        )
        report.mirror_files_copied = copied
        report.mirror_files_skipped = skipped
        report.mirror_symlinks_skipped = symlinks_skipped
        report.mirror_errors = mirror_errors

        if dry_run:
            report.git_dirty_after = git_status_porcelain(repo_root)
            report.final_head = git_head(repo_root)
            report.status = "ok" if not report.errors and not report.mirror_errors else "action_required"
            return report

        git_add_whitelist(repo_root, stage_paths)

        if staged_diff_exists(repo_root):
            message = f"GitHub write assurance sync {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
            report.sync_commit_hash = commit_changes(repo_root, message)
            report.sync_commit_created = True
        else:
            report.sync_commit_hash = git_head(repo_root)
            report.sync_commit_created = False

        # Prepare the proof report as OK before committing it. If push or remote
        # verification fails, we rewrite the local proof as ACTION REQUIRED.
        if report.errors or report.mirror_errors:
            report.status = "action_required"
        elif push_enabled and report.branch_actual != branch:
            report.status = "action_required"
            report.errors.append("push skipped because branch mismatch")
        elif not push_enabled:
            report.status = "ok"
            report.warnings.append("push disabled by --no-push")
        else:
            report.status = "ok"
            report.push_ok = True
            report.remote_verified = True

        commit_status_proof(report, repo_root, memory_root)
        report.final_head = git_head(repo_root)

        if push_enabled and report.branch_actual == branch:
            push_ok, push_output = push_branch(repo_root, branch)
            report.push_ok = push_ok
            if not push_ok:
                report.status = "action_required"
                report.errors.append(f"git push failed: {push_output or 'no output'}")
            else:
                report.remote_verified = verify_remote_head(repo_root, branch, report.final_head)
                if not report.remote_verified:
                    report.status = "action_required"
                    report.errors.append("remote verification failed or unavailable")
        elif not push_enabled:
            report.remote_verified = False

        if report.status != "ok":
            # Failure proof is local and repo-working-tree visible. It may be dirty
            # by design because the push could not be trusted.
            write_status(report, memory_root, repo_root, dry_run=False)

        report.git_dirty_after = git_status_porcelain(repo_root)
        return report

    except Exception as exc:  # noqa: BLE001
        report.errors.append(str(exc))
        report.status = "action_required"
        try:
            report.git_dirty_after = git_status_porcelain(repo_root)
        except Exception:
            pass
        try:
            write_status(report, memory_root, repo_root, dry_run=dry_run)
        except Exception:
            pass
        return report


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="gwa_selftest_") as tmp:
        base = Path(tmp)
        memory = base / "memory"
        repo = base / "repo"
        remote = base / "remote.git"
        memory.mkdir(parents=True)
        repo.mkdir(parents=True)

        run_cmd(["git", "init", "--bare", str(remote)], check=True)
        run_cmd(["git", "init"], cwd=repo, check=True)
        run_cmd(["git", "config", "user.email", "selftest@example.invalid"], cwd=repo, check=True)
        run_cmd(["git", "config", "user.name", "GWA Self Test"], cwd=repo, check=True)
        run_cmd(["git", "checkout", "-b", "v1.1-dev"], cwd=repo, check=True)
        run_cmd(["git", "remote", "add", "origin", str(remote)], cwd=repo, check=True)

        (repo / "memory" / "logs" / "fitness").mkdir(parents=True)
        (repo / "tools").mkdir()
        (repo / "tools" / ".keep").write_text("keep\n", encoding="utf-8")
        stale = repo / "memory" / "logs" / "fitness" / "old_deleted_file.md"
        stale.write_text("old\n", encoding="utf-8")
        run_cmd(["git", "add", "tools/.keep", "memory/logs/fitness/old_deleted_file.md"], cwd=repo, check=True)
        run_cmd(["git", "commit", "-m", "initial"], cwd=repo, check=True)
        run_cmd(["git", "push", "-u", "origin", "v1.1-dev"], cwd=repo, check=True)

        # Simulate a pre-existing local deletion that the prior version left dirty.
        stale.unlink()

        (memory / "logs" / "status").mkdir(parents=True)
        (memory / "logs" / "status" / "sample_status.md").write_text("sample ok\n", encoding="utf-8")
        (memory / ".env").write_text("SECRET=do_not_copy\n", encoding="utf-8")
        (memory / "logs" / "status" / "api_token.txt").write_text("do_not_copy\n", encoding="utf-8")
        broken = memory / "quarantine_symlinks" / "broken_link.md"
        broken.parent.mkdir(parents=True)
        broken.symlink_to(memory / "missing_target.md")

        report = run_assurance(
            repo_root=repo,
            memory_root=memory,
            branch="v1.1-dev",
            dry_run=False,
            push_enabled=True,
            max_file_bytes=MAX_FILE_BYTES_DEFAULT,
            stage_paths=DEFAULT_STAGE_PATHS,
        )

        checks = [
            report.status == "ok",
            (repo / "memory" / "logs" / "status" / "sample_status.md").exists(),
            not (repo / "memory" / ".env").exists(),
            not (repo / "memory" / "logs" / "status" / "api_token.txt").exists(),
            not stale.exists(),
            report.mirror_symlinks_skipped >= 1,
            (memory / STATUS_REL).exists(),
            (repo / REPO_STATUS_REL).exists(),
            report.push_ok,
            report.remote_verified,
            git_status_porcelain(repo) == "",
        ]
        if all(checks):
            print("SELF-TEST OK")
            print(render_markdown(report))
            return 0

        print("SELF-TEST FAILED")
        print(render_markdown(report))
        return 1


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mirror, commit, push, verify, and prove GitHub write health.")
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--memory-root", default=str(DEFAULT_MEMORY_ROOT))
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-push", action="store_true", help="Commit locally but do not push.")
    parser.add_argument("--max-file-mb", type=int, default=10)
    parser.add_argument("--stage-path", action="append", default=None, help="Repo path to stage; may be repeated.")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()

    repo_root = Path(args.repo_root).expanduser().resolve()
    memory_root = Path(args.memory_root).expanduser().resolve()
    max_file_bytes = max(1, args.max_file_mb) * 1024 * 1024
    stage_paths = args.stage_path if args.stage_path else DEFAULT_STAGE_PATHS

    report = run_assurance(
        repo_root=repo_root,
        memory_root=memory_root,
        branch=args.branch,
        dry_run=args.dry_run,
        push_enabled=not args.no_push,
        max_file_bytes=max_file_bytes,
        stage_paths=stage_paths,
    )
    print(render_markdown(report))
    return 0 if report.status == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
