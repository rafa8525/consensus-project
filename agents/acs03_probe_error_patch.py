#!/usr/bin/env python3
"""Patch only the existing ACS-03 cloud-cycle ProbeFailure classification map.

Defaults to --check (read-only). --apply requires an exact, recognizable
allowed.get(str(exc), "UNCLASSIFIED") handler and preserves a one-time backup.
No probes, OAuth operations, fitness reads, schedules, or network calls.
"""
from __future__ import annotations

import argparse
import ast
import os
import shutil
import tempfile
from pathlib import Path

CLOUD = Path.home() / "acs-runtime/repairs/acs03/cloud/health_connect_cloud_cycle.py"
PROBE_CODES = {
    "No private OAuth token": "OAUTH_TOKEN_MISSING",
    "Token has no refresh authorization": "OAUTH_REFRESH_MISSING",
    "OAuth token unavailable": "OAUTH_UNAVAILABLE",
    "Ambiguous Drive query": "DRIVE_QUERY_AMBIGUOUS",
    "Expected one accessible private backup folder": "BACKUP_FOLDER_NOT_FOUND",
    "Expected one accessible Health Connect ZIP": "HEALTH_EXPORT_NOT_FOUND",
    "Drive object relationship mismatch": "DRIVE_RELATIONSHIP_MISMATCH",
    "Drive file media type mismatch": "DRIVE_MEDIA_TYPE_MISMATCH",
    "Export size outside expected limit": "EXPORT_SIZE_INVALID",
    "Export is stale or timestamp unexpected": "EXPORT_STALE",
}


class UnsafeLayout(ValueError):
    """Cloud cycle does not match the previously reviewed handler."""


def _byte_offset(lines: list[bytes], lineno: int, col: int) -> int:
    return sum(map(len, lines[:lineno - 1])) + col


def patch_source(source: str) -> tuple[str, int]:
    tree = ast.parse(source)
    candidates = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        assigns = [
            stmt for stmt in node.body
            if isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and stmt.targets[0].id == "allowed"
            and isinstance(stmt.value, ast.Dict)
        ]
        has_fallback = any(
            isinstance(item, ast.Call)
            and ast.unparse(item).replace(" ", "")
            == "allowed.get(str(exc),'UNCLASSIFIED')"
            for stmt in node.body for item in ast.walk(stmt)
        )
        if len(assigns) == 1 and has_fallback:
            candidates.append(assigns[0])
    if len(candidates) != 1:
        raise UnsafeLayout("Expected exactly one matching fallback handler")
    mapping = candidates[0].value
    if not mapping.keys or any(
        k is None or not isinstance(k, ast.Constant) or not isinstance(k.value, str)
        or not isinstance(v, ast.Constant) or not isinstance(v.value, str)
        for k, v in zip(mapping.keys, mapping.values)
    ):
        raise UnsafeLayout("Existing error map has unexpected structure")
    existing = {k.value: v.value for k, v in zip(mapping.keys, mapping.values)}
    conflicting = [k for k, v in PROBE_CODES.items() if k in existing and existing[k] != v]
    if conflicting:
        raise UnsafeLayout("Existing probe category conflicts with proposed mapping")
    missing = {k: v for k, v in PROBE_CODES.items() if k not in existing}
    if not missing:
        return source, 0

    encoded = source.encode("utf-8")
    lines = encoded.splitlines(keepends=True)
    start = _byte_offset(lines, mapping.lineno, mapping.col_offset)
    first_key = _byte_offset(lines, mapping.keys[0].lineno, mapping.keys[0].col_offset)
    brace = encoded.find(b"{", start, first_key)
    if brace < 0:
        raise UnsafeLayout("Cannot locate original mapping opening brace")

    indent = b" " * mapping.keys[0].col_offset
    addition = b"".join(
        b"\n" + indent + (repr(k) + ": " + repr(v) + ",").encode("utf-8")
        for k, v in missing.items()
    )
    changed = (encoded[:brace + 1] + addition + encoded[brace + 1:]).decode("utf-8")
    ast.parse(changed)
    return changed, len(missing)


def apply(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise UnsafeLayout("Expected a regular cloud-cycle file (no symlink)")
    before = path.read_text(encoding="utf-8")
    after, count = patch_source(before)
    if not count:
        return "ALREADY_PATCHED"
    backup = path.with_name(path.name + ".pre_acs03_probe_codes")
    if backup.exists():
        raise UnsafeLayout("Backup already exists: refusing to overwrite it")
    mode = path.stat().st_mode & 0o777
    shutil.copy2(path, backup)
    fd, tmp = tempfile.mkstemp(prefix=".acs03-probe-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(after)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, mode)
        ast.parse(Path(tmp).read_text(encoding="utf-8"))
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return "PATCHED_%d_PROBE_CATEGORIES" % count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--file", type=Path, default=CLOUD)
    args = parser.parse_args()
    try:
        if args.apply:
            print(apply(args.file))
        else:
            if args.file.is_symlink() or not args.file.is_file():
                raise UnsafeLayout("Cloud-cycle file missing or symlinked")
            _, count = patch_source(args.file.read_text(encoding="utf-8"))
            print("CHECK_OK: %d known probe categories absent" % count)
        return 0
    except (OSError, SyntaxError, UnicodeError, UnsafeLayout) as exc:
        print("FAIL_CLOSED:", type(exc).__name__)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
