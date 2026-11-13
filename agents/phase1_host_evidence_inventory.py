#!/usr/bin/env python3
"""One-time, read-only Phase 1 host inventory. No secrets, personal data or writes.

This is an evidence *inventory*, never a production recovery proof.
Run explicitly on PythonAnywhere; no scheduled execution or agent imports.
"""
import hashlib
import json
import subprocess
from pathlib import Path

KEYS = ("failure_detection", "automatic_retry", "recovery_verified", "bounded_escalation")
ROOT = Path.home() / ".config/ai-consensus"
REPO = Path.home() / "consensus-project"
PROOF = ROOT / "phase1_recovery_evidence.json"
EVIDENCE = ROOT / "evidence"


def inspect_proofs(manifest=PROOF, directory=EVIDENCE):
    if not manifest.is_file():
        return {"manifest": "missing", "tests": {k: "absent" for k in KEYS}}
    try:
        raw = manifest.read_bytes()
        if len(raw) > 1024 * 1024:
            return {"manifest": "oversized"}
        doc = json.loads(raw)
        tests = doc.get("tests") if isinstance(doc, dict) else None
        if not isinstance(tests, dict):
            return {"manifest": "invalid_schema"}
    except (OSError, ValueError, UnicodeDecodeError):
        return {"manifest": "invalid_or_unreadable"}
    findings = {}
    for key in KEYS:
        item = tests.get(key)
        if not isinstance(item, dict):
            findings[key] = "absent"
            continue
        filename = item.get("artifact_path")
        digest = item.get("artifact_sha256")
        if not isinstance(filename, str) or not filename or not isinstance(digest, str):
            findings[key] = "invalid_metadata"
            continue
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            findings[key] = "invalid_digest"
            continue
        try:
            base = directory.resolve()
            target = (base / filename).resolve()
            if not target.is_relative_to(base) or not target.is_file():
                findings[key] = "missing_or_unsafe_path"
                continue
            if target.stat().st_size > 1024 * 1024:
                findings[key] = "oversized"
                continue
            verified_digest = hashlib.sha256(target.read_bytes()).hexdigest() == digest
        except (OSError, ValueError):
            findings[key] = "unreadable"
            continue
        # Metadata alone is not authoritative evidence of a production incident.
        scope = item.get("execution_scope")
        findings[key] = {
            "digest_matches": verified_digest,
            "production_scope_claimed": scope == "production",
            "passed_claimed": item.get("passed") is True,
            "timestamp_present": isinstance(item.get("executed_at_utc"), str),
            "independently_verified": False,
        }
    return {"manifest": "present", "tests": findings}


def inspect_worktree(repo=REPO):
    if not repo.is_dir():
        return {"status": "repository_missing"}
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=no"],
            cwd=repo, capture_output=True, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "git_unavailable"}
    if result.returncode:
        return {"status": "git_failed", "returncode": result.returncode}
    entries = [e for e in result.stdout.split(b"\\0") if e]
    groups = {}
    for entry in entries:
        # Only category totals, never private filenames or file contents.
        raw = entry[3:] if len(entry) >= 4 else b""
        name = raw.split(b"/", 1)[0].decode("utf-8", errors="replace")
        group = name if name in ("agents", "logs", "memory", "docs", ".github", "tools", "tests") else "other"
        groups[group] = groups.get(group, 0) + 1
    return {"status": "read_only", "tracked_changes": len(entries), "groups": groups}


def inspect_host():
    state = Path.home() / ".local/state/ai-consensus"
    return {
        "kind": "READ_ONLY_EVIDENCE_INVENTORY_NOT_CERTIFICATION",
        "proofs": inspect_proofs(),
        "worktree": inspect_worktree(),
        "known_host_files_present": {
            "supervisor_retry": (state / "phase1_supervisor_retry_result.json").is_file(),
            "controlled_escalation": (state / "phase1_host_controlled_escalation.json").is_file(),
            "schedule_backup": (state / "phase1_original_acs01_schedule.json").is_file(),
        },
    }


if __name__ == "__main__":
    print(json.dumps(inspect_host(), indent=2, sort_keys=True))
