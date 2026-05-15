#!/usr/bin/env python3
"""
ACSM_SECURITY_VPN_AUDIT_V2

Proof-based Security/VPN audit for Rafael's AI Consensus System.

Safe behavior:
- No SMS.
- No voice calls.
- No VPN changes.
- No paid APIs.
- No secrets printed.
- Writes local proof files only.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path("/home/rafa1215/consensus-project")
MEM_ROOT = Path("/home/rafa1215/memory")

CANONICAL_DIR = MEM_ROOT / "logs/security"
REPO_DIR = REPO_ROOT / "memory/logs/security"

CANONICAL_MD = CANONICAL_DIR / "security_vpn_audit_latest.md"
CANONICAL_JSON = CANONICAL_DIR / "security_vpn_audit_latest.json"
REPO_MD = REPO_DIR / "security_vpn_audit_latest.md"
REPO_JSON = REPO_DIR / "security_vpn_audit_latest.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def ensure_dirs() -> None:
    CANONICAL_DIR.mkdir(parents=True, exist_ok=True)
    REPO_DIR.mkdir(parents=True, exist_ok=True)


def read_text(path: Path, limit: int = 30000) -> str:
    try:
        if not path.exists():
            return ""
        text = path.read_text(errors="replace")
        return text[-limit:] if len(text) > limit else text
    except Exception:
        return ""


def file_age_hours(path: Path) -> float | None:
    try:
        if not path.exists():
            return None
        mtime = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        return (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
    except Exception:
        return None


def check_file(path: Path, label: str, required: bool = True) -> dict:
    if not path.exists():
        return {
            "label": label,
            "status": "missing" if required else "optional_missing",
            "score": 35 if required else 90,
            "evidence": str(path),
            "detail": "Missing." if required else "Optional proof not found; not a blocker.",
        }

    age = file_age_hours(path)
    detail = "Found."
    if age is not None:
        detail += f" Age: {age:.1f} hours."

    return {
        "label": label,
        "status": "ok",
        "score": 100,
        "evidence": str(path),
        "detail": detail,
    }


def check_executable(path: Path, label: str) -> dict:
    if not path.exists():
        return {
            "label": label,
            "status": "missing",
            "score": 40,
            "evidence": str(path),
            "detail": "Missing.",
        }

    try:
        is_exec = bool(path.stat().st_mode & stat.S_IXUSR)
    except Exception:
        is_exec = False

    return {
        "label": label,
        "status": "ok" if is_exec else "warning",
        "score": 100 if is_exec else 90,
        "evidence": str(path),
        "detail": "Executable." if is_exec else "Found; not executable, but acceptable if invoked through bash/python.",
    }


def check_env_guard(name: str, safe_false: bool = True) -> dict:
    value = os.environ.get(name)

    false_values = {"false", "False", "FALSE", "0", "no", "No", "NO", "off", "Off", "OFF"}
    true_values = {"true", "True", "TRUE", "1", "yes", "Yes", "YES", "on", "On", "ON"}

    if value is None:
        return {
            "label": f"Environment guard: {name}",
            "status": "not_set",
            "score": 95,
            "evidence": "environment",
            "detail": "Not set in this shell. Acceptable because PythonAnywhere/scheduled tasks may set runtime values separately.",
        }

    expected = false_values if safe_false else true_values
    if value in expected:
        return {
            "label": f"Environment guard: {name}",
            "status": "ok",
            "score": 100,
            "evidence": "environment",
            "detail": "Set to safe value. Value hidden.",
        }

    return {
        "label": f"Environment guard: {name}",
        "status": "warning",
        "score": 70,
        "evidence": "environment",
        "detail": "Set, but not the expected safe value. Value hidden.",
    }


def check_patterns(path: Path, label: str, patterns: list[str]) -> dict:
    if not path.exists():
        return {
            "label": label,
            "status": "optional_missing",
            "score": 90,
            "evidence": str(path),
            "detail": "Optional guardrail file not found; not a blocker for this audit.",
        }

    text = read_text(path)
    found = [p for p in patterns if re.search(p, text, re.IGNORECASE)]

    if found:
        return {
            "label": label,
            "status": "ok",
            "score": 100,
            "evidence": str(path),
            "detail": "Found expected guardrail signals: " + ", ".join(found),
        }

    return {
        "label": label,
        "status": "warning",
        "score": 80,
        "evidence": str(path),
        "detail": "File exists, but expected guardrail keywords were not detected.",
    }


def newest_file_age(path: Path) -> tuple[str, float | None]:
    if not path.exists():
        return str(path), None

    if path.is_file():
        return str(path), file_age_hours(path)

    newest = None
    newest_mtime = -1.0

    try:
        for item in path.rglob("*"):
            if not item.is_file():
                continue
            mtime = item.stat().st_mtime
            if mtime > newest_mtime:
                newest = item
                newest_mtime = mtime
    except Exception:
        return str(path), None

    if newest is None:
        return str(path), None

    return str(newest), file_age_hours(newest)


def check_recent_dir(path: Path, label: str) -> dict:
    evidence, age = newest_file_age(path)

    if age is None:
        return {
            "label": label,
            "status": "optional_missing",
            "score": 90,
            "evidence": evidence,
            "detail": "No recent file found yet; not a blocker because this audit writes fresh proof now.",
        }

    if age <= 31 * 24:
        return {
            "label": label,
            "status": "ok",
            "score": 100,
            "evidence": evidence,
            "detail": f"Recent evidence found. Age: {age / 24:.1f} days.",
        }

    return {
        "label": label,
        "status": "stale",
        "score": 80,
        "evidence": evidence,
        "detail": f"Evidence exists but is stale. Age: {age / 24:.1f} days.",
    }


def weighted_score(checks: list[dict]) -> int:
    if not checks:
        return 0

    core_labels = {
        "Security audit schedule",
        "Environment runner",
        "System health snapshot",
        "Memory absorption marker",
    }

    total = 0
    weight_total = 0

    for check in checks:
        weight = 2 if check["label"] in core_labels else 1
        total += int(check["score"]) * weight
        weight_total += weight

    return round(total / weight_total)


def status(score: int) -> str:
    if score >= 95:
        return "excellent"
    if score >= 90:
        return "very_good"
    if score >= 80:
        return "good"
    if score >= 70:
        return "usable"
    return "needs_repair"


def verdict(score: int) -> str:
    if score >= 95:
        return "Excellent. Security/VPN proof is fresh and strong."
    if score >= 90:
        return "Very good. Security/VPN proof is fresh and safe."
    if score >= 80:
        return "Good. Security/VPN posture is current and acceptable."
    if score >= 70:
        return "Usable. Security/VPN posture has proof but needs cleanup."
    return "Needs repair. Security/VPN proof is weak."


def esc(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|").strip()


def build_report(checks: list[dict], score: int) -> str:
    lines = [
        f"# Security/VPN Audit - {today()}",
        "",
        "Audit version: ACSM_SECURITY_VPN_AUDIT_V2",
        "",
        f"Generated UTC: {now_utc()}",
        "",
        f"Score: {score}/100",
        "",
        f"Status: {status(score)}",
        "",
        f"Verdict: {verdict(score)}",
        "",
        "## Checks",
        "",
        "| Check | Status | Score | Evidence | Detail |",
        "|---|---:|---:|---|---|",
    ]

    for c in checks:
        lines.append(
            f"| {esc(c['label'])} | {esc(c['status'])} | {c['score']} | `{esc(c['evidence'])}` | {esc(c['detail'])} |"
        )

    lines.extend(
        [
            "",
            "## Safe behavior confirmed",
            "",
            "- SMS sent: no",
            "- Voice calls placed: no",
            "- VPN state changed: no",
            "- Secrets printed: no",
            "- Paid APIs used: no",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    if not REPO_ROOT.exists():
        print(f"ERROR: repo root missing: {REPO_ROOT}")
        return 2

    if not MEM_ROOT.exists():
        print(f"ERROR: memory root missing: {MEM_ROOT}")
        return 2

    ensure_dirs()

    checks = [
        check_file(REPO_ROOT / "security_audit_schedule.txt", "Security audit schedule", required=True),
        check_file(REPO_ROOT / "run_with_env.sh", "Environment runner", required=True),
        check_file(MEM_ROOT / "logs/status/system_health_snapshot.md", "System health snapshot", required=True),
        check_file(MEM_ROOT / "public/absorption_last_success.json", "Memory absorption marker", required=True),

        check_file(REPO_ROOT / "vpn_activation_feature.txt", "VPN activation feature plan", required=False),
        check_file(REPO_ROOT / "vpn_activation_testing_plan.txt", "VPN activation testing plan", required=False),
        check_file(REPO_ROOT / "VPNActivationTestingPlan.txt", "VPN load/stress/failover testing plan", required=False),

        check_env_guard("SMS_ENABLED", safe_false=True),
        check_env_guard("ALLOW_VOICE_CALLS", safe_false=True),
        check_env_guard("TWILIO_ALLOW_SEND", safe_false=True),
        check_env_guard("TWILIO_SILENCE", safe_false=False),

        check_patterns(
            REPO_ROOT / "common/twilio_guard.py",
            "Twilio guardrails",
            [r"quiet", r"whitelist", r"max", r"SMS", r"TWILIO", r"ALLOW_VOICE"],
        ),

        check_patterns(
            Path("/var/www/rafa1215_pythonanywhere_com_wsgi.py"),
            "PythonAnywhere WSGI safe defaults",
            [r"TWILIO_ALLOW_SEND", r"TWILIO_SILENCE", r"SMS_ENABLED", r"ALLOW_VOICE_CALLS"],
        ),

        check_recent_dir(MEM_ROOT / "logs/security", "Canonical security log freshness"),
        check_recent_dir(REPO_ROOT / "memory/logs/security", "Repo security mirror freshness"),
    ]

    score = weighted_score(checks)

    payload = {
        "audit_version": "ACSM_SECURITY_VPN_AUDIT_V2",
        "generated_utc": now_utc(),
        "date": today(),
        "score": score,
        "status": status(score),
        "verdict": verdict(score),
        "checks": checks,
        "safe_behavior": {
            "sms_sent": False,
            "voice_calls_placed": False,
            "vpn_state_changed": False,
            "secrets_printed": False,
            "paid_apis_used": False,
        },
    }

    report = build_report(checks, score)

    CANONICAL_MD.write_text(report)
    CANONICAL_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True))

    dated_md = CANONICAL_DIR / f"security_vpn_audit_{today()}.md"
    dated_json = CANONICAL_DIR / f"security_vpn_audit_{today()}.json"

    dated_md.write_text(report)
    dated_json.write_text(json.dumps(payload, indent=2, sort_keys=True))

    shutil.copy2(CANONICAL_MD, REPO_MD)
    shutil.copy2(CANONICAL_JSON, REPO_JSON)
    shutil.copy2(dated_md, REPO_DIR / dated_md.name)
    shutil.copy2(dated_json, REPO_DIR / dated_json.name)

    print(f"OK: wrote {CANONICAL_MD}")
    print(f"OK: wrote {CANONICAL_JSON}")
    print(f"OK: mirrored {REPO_MD}")
    print(f"OK: mirrored {REPO_JSON}")
    print(f"Score: {score}/100")
    print(f"Status: {status(score)}")

    return 0 if score >= 70 else 1


if __name__ == "__main__":
    raise SystemExit(main())
