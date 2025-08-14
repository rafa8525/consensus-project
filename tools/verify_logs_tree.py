#!/usr/bin/env python3
# tools/verify_logs_tree.py
import argparse
import os
import sys
import subprocess
import shlex
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
PREFERRED = ROOT / "memory" / "logs"
FALLBACK  = ROOT / "logs"
SANITY    = PREFERRED / "sanity"
TS        = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
REPORT    = SANITY / f"logs_tree_verify_{TS}.md"
NEEDED    = ["heartbeat","github_sync","fitness","finance","reminders","sanity"]
GIT_BRANCH_DEFAULT = "v1.1-dev"

def run(cmd: str, cwd: Path = ROOT) -> Tuple[int, str, str]:
    p = subprocess.run(shlex.split(cmd), cwd=str(cwd), capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def ensure_logs_root() -> Path:
    # Prefer memory/logs if it exists or can be created, else logs/
    target = PREFERRED if PREFERRED.exists() or not FALLBACK.exists() else FALLBACK
    target.mkdir(parents=True, exist_ok=True)
    return target

def ensure_structure(logs_root: Path) -> List[Path]:
    created = []
    (logs_root / "sanity").mkdir(parents=True, exist_ok=True)
    for d in NEEDED:
        p = logs_root / d
        p.mkdir(parents=True, exist_ok=True)
        gk = p / ".gitkeep"
        if not gk.exists():
            gk.touch()
            created.append(gk)
    return created

def build_tree(root: Path, show_files: bool = True) -> Tuple[List[str], int, int]:
    """
    Render a 'tree'-like view. Returns (lines, dir_count, file_count).
    """
    lines: List[str] = []
    dir_count = 0
    file_count = 0

    def rel(p: Path) -> str:
        try:
            return p.relative_to(ROOT).as_posix()
        except ValueError:
            return str(p)

    def walker(base: Path, prefix: str = ""):
        nonlocal dir_count, file_count
        entries = sorted([e for e in base.iterdir() if not e.name.startswith(".") or e.name == ".gitkeep"],
                         key=lambda p: (p.is_file(), p.name.lower()))
        for i, entry in enumerate(entries):
            connector = "└── " if i == len(entries) - 1 else "├── "
            line = f"{prefix}{connector}{entry.name}"
            if entry.is_dir():
                lines.append(line + "/")
                dir_count += 1
                extension = "    " if i == len(entries) - 1 else "│   "
                walker(entry, prefix + extension)
            else:
                if show_files:
                    lines.append(line)
                    file_count += 1

    header = rel(root)
    lines.append(header + "/")
    walker(root, "")
    return lines, dir_count, file_count

def generate_report(logs_root: Path, created: List[Path], branch_hint: str) -> str:
    rel_root = logs_root.relative_to(ROOT)
    tree_lines, dcnt, fcnt = build_tree(logs_root, show_files=True)
    created_rel = [p.relative_to(ROOT).as_posix() for p in created]
    lines = [
        "# Logs Tree Verify",
        f"- UTC: {datetime.now(timezone.utc).isoformat()}",
        f"- Logs root: `{rel_root.as_posix()}`",
        f"- Created .gitkeep: {len(created_rel)}",
        *(f"  - `{x}`" for x in created_rel),
        f"- Totals: {dcnt} dirs, {fcnt} files",
        f"- Git branch (hint): {branch_hint}",
        "",
        "```",
        *tree_lines,
        "```",
        "",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return REPORT.relative_to(ROOT).as_posix()

def maybe_git_publish(rel_report: str, branch: str, dry_run: bool) -> Tuple[bool, str]:
    if dry_run:
        return False, "Dry run: not committing."
    rc, _, _ = run(f"git rev-parse --abbrev-ref HEAD")
    # Add/commit/push on the specified branch regardless of current HEAD
    run(f"git add {rel_report}")
    rc, out, err = run(f"git commit -m 'Verify logs tree {TS}'")
    if rc != 0 and "nothing to commit" in err.lower():
        return False, "Nothing new to commit."
    rc, out, err = run(f"git push origin {branch}")
    if rc != 0:
        return False, f"Push failed: {err or out}".strip()
    return True, "Committed and pushed."

def main():
    ap = argparse.ArgumentParser(description="Verify and report logs tree.")
    ap.add_argument("--branch", default=GIT_BRANCH_DEFAULT, help="Branch to push to (default: v1.1-dev)")
    ap.add_argument("--no-push", action="store_true", help="Generate report but do not commit/push")
    args = ap.parse_args()

    logs_root = ensure_logs_root()
    created = ensure_structure(logs_root)
    rel_report = generate_report(logs_root, created, args.branch)

    pushed, msg = maybe_git_publish(rel_report, args.branch, dry_run=args.no_push)
    print(f"Report: {rel_report}")
    print(msg if msg else ("Pushed" if pushed else "Not pushed"))

if __name__ == "__main__":
    sys.exit(main())
