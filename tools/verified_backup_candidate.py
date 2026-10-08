#!/usr/bin/env python3
"""Candidate local ACS backup engine. No network, scheduler, or production changes.

Only explicitly listed sources are archived. Never upload this archive unencrypted:
agent state and memory can contain personal information.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

SOURCES = (
    "memory/agents",
    "memory/state",
    "memory/knowledge",
    "memory/consensus",
    "registry",
    "memory/centralized_knowledge_base.txt",
)
MANIFEST = "__acs_manifest__.json"
DENY_NAMES = {".env", "credentials.json", "service_account.json", "vault.key",
              "id_rsa", "id_ed25519", ".netrc"}
DENY_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".sqlite", ".db"}
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
# High-confidence secret patterns; not an exhaustive DLP solution.
SENSITIVE_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(rb'(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)\\s*["\\\']?\\s*[:=]\\s*["\\\']?[^\\s"\\\']{12,}'),
)


def reject_obvious_secrets(name: str, content: bytes) -> None:
    """Fail closed on common credentials prior to staging any archive."""
    if any(pattern.search(content) for pattern in SENSITIVE_PATTERNS):
        raise ValueError("potential credential content found: " + name)



def disallowed(path: Path) -> bool:
    return (any(part.startswith(".") for part in path.parts)
            or path.name.lower() in DENY_NAMES
            or path.suffix.lower() in DENY_SUFFIXES)


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def collect(root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    total = 0
    for source_name in SOURCES:
        source = root / source_name
        if not source.exists() or source.is_symlink():
            raise ValueError("missing or symlinked required source: " + source_name)
        candidates = [source] if source.is_file() else sorted(source.rglob("*"))
        accepted = 0
        for file in candidates:
            if file.is_symlink() or not file.is_file():
                continue
            rel = file.relative_to(root)
            if disallowed(rel):
                continue
            if file.stat().st_size > MAX_FILE_BYTES:
                raise ValueError("oversized file: " + rel.as_posix())
            content = file.read_bytes()
            reject_obvious_secrets(rel.as_posix(), content)
            total += len(content)
            if total > MAX_TOTAL_BYTES:
                raise ValueError("backup exceeds maximum permitted size")
            result[rel.as_posix()] = content
            accepted += 1
        if not accepted:
            raise ValueError("required source has no permitted files: " + source_name)
    return result


def verify(archive_path: Path) -> dict:
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("archive integrity failure")
        names = archive.namelist()
        if len(names) != len(set(names)) or MANIFEST not in names:
            raise ValueError("missing manifest or duplicate archive paths")
        manifest = json.loads(archive.read(MANIFEST))
        expected = manifest["files"]
        if set(names) != set(expected) | {MANIFEST} or not expected:
            raise ValueError("missing/unexpected files")
        for name, sha in expected.items():
            p = PurePosixPath(name)
            if p.is_absolute() or ".." in p.parts or disallowed(Path(name)):
                raise ValueError("unsafe archive entry")
            if digest(archive.read(name)) != sha:
                raise ValueError("content checksum mismatch: " + name)
        if not set(SOURCES).issubset(set(manifest.get("sources", []))):
            raise ValueError("source manifest incomplete")
        return {"file_count": len(expected), "archive_bytes": archive_path.stat().st_size,
                "sha256": digest(archive_path.read_bytes())}


def create(root: Path, output: Path) -> dict:
    root = root.resolve(strict=True)
    if output.exists() or output.is_symlink():
        raise FileExistsError("refusing to overwrite existing backup")
    files = collect(root)
    manifest = {
        "schema": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "sources": list(SOURCES),
        "files": {name: digest(content) for name, content in files.items()},
    }
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = None
    try:
        fd, temp = tempfile.mkstemp(prefix=".acs-backup-", suffix=".tmp", dir=output.parent)
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as handle:
            with zipfile.ZipFile(handle, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
                for name, content in files.items():
                    archive.writestr(name, content)
                archive.writestr(MANIFEST, json.dumps(manifest, sort_keys=True))
        result = verify(Path(temp))
        os.link(temp, output)  # atomic no-overwrite publication
        return result
    finally:
        if temp is not None:
            Path(temp).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Local-only verified ACS backup candidate")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps({"status": "ok", **create(args.root, args.output)}))
        return 0
    except Exception as error:
        print(json.dumps({"status": "failed", "reason": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
