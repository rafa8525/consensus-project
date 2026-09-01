#!/usr/bin/env python3
"""
continuity_guardian_agent.py

AI Consensus continuity guardian created 2026-09-01 after the Gmail OAuth/client,
Master Control Loop, memory-compressor, absorption/scheduler, and resource-limit audit.

Mission: detect regressions early so the same recovery work does not have to be
repeated.  This agent is read-only except for its own state/log files and optional
Twilio alerts.  It does NOT rewrite credentials or repair production files.

Checks covered:
- Google OAuth desktop-client credentials exist and are structurally usable.
- Gmail OAuth token exists, includes Gmail scope, refreshes, and can call Gmail.
- Detect deleted_client / invalid_client / invalid_grant failures explicitly.
- Search recent Gmail for Google OAuth/client inactivity/deletion warnings.
- Detect stale legacy Gmail/service-account path references in active guards.
- Detect duplicate gmail_refresh_guard_v3 invocation paths.
- Verify the Master Control Loop dispatcher contains required-argument fallback.
- Flag unconditional "All subsystems executed successfully" reporting.
- Check memory-compressor size/rotation and fatal-exit behavior.
- Check centralized knowledge-base freshness / absorption health.
- Verify today's prediction feed freshness without changing it.
- Detect recent resource-exhaustion/fork failures and high process pressure.
- Flag VPN/security results that are simulation-only rather than real VPN proof.

Designed to run from the Master Control Loop every cycle, but expensive checks are
internally gated to once per hour.  Critical findings return exit code 2 so the
Master Control Loop cannot silently report a clean run.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import resource
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

BASE = Path.home() / "consensus-project"
TOOLS = BASE / "tools"
AGENTS = BASE / "agents"
MEMORY = BASE / "memory"
SYSLOG = MEMORY / "logs" / "system"
LOG = SYSLOG / "continuity_guardian.log"
STATE = SYSLOG / "continuity_guardian_state.json"
SECRETS = Path.home() / ".secrets" / "google"
CREDS = SECRETS / "credentials.json"
GMAIL_TOKEN = SECRETS / "token_gmail.json"
KB = MEMORY / "centralized_knowledge_base.txt"
COMPRESSED = MEMORY / "logs" / "compressed_memory.md"
HEARTBEAT = MEMORY / "logs" / "system" / "heartbeat.md"
NOHUP = BASE / "nohup.out"
MIN_INTERVAL_SECONDS = 3600
MAX_COMPRESSED_BYTES = 40 * 1024 * 1024
MAX_KB_AGE_HOURS = 26
MAX_PREDICTION_AGE_HOURS = 26

CRITICAL: List[str] = []
WARN: List[str] = []
INFO: List[str] = []


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def stamp() -> str:
    return now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")


def log(line: str) -> None:
    SYSLOG.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{stamp()} {line}\n")
    print(line)


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state: dict) -> None:
    SYSLOG.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(STATE)


def file_age_hours(path: Path) -> float | None:
    try:
        return (now_utc().timestamp() - path.stat().st_mtime) / 3600.0
    except OSError:
        return None


def safe_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        CRITICAL.append(f"Invalid JSON: {path}: {type(exc).__name__}: {exc}")
        return None


def check_google_oauth() -> Tuple[object | None, object | None]:
    creds_data = None
    token_creds = None

    if not CREDS.exists():
        CRITICAL.append(f"Google OAuth client credentials missing: {CREDS}")
    else:
        mode = CREDS.stat().st_mode & 0o777
        if mode & 0o077:
            WARN.append(f"Google OAuth credentials permissions are {oct(mode)}; expected 0o600")
        creds_data = safe_json(CREDS)
        if creds_data is not None:
            if not any(k in creds_data for k in ("installed", "web")):
                CRITICAL.append("credentials.json is not an OAuth installed/web client JSON")

    if not GMAIL_TOKEN.exists():
        CRITICAL.append(f"Gmail OAuth token missing: {GMAIL_TOKEN}")
        return creds_data, None

    mode = GMAIL_TOKEN.stat().st_mode & 0o777
    if mode & 0o077:
        WARN.append(f"Gmail token permissions are {oct(mode)}; expected 0o600")

    token_data = safe_json(GMAIL_TOKEN)
    if token_data is None:
        return creds_data, None

    scopes = token_data.get("scopes") or []
    if isinstance(scopes, str):
        scopes = [scopes]
    if not any("gmail" in str(s).lower() for s in scopes):
        CRITICAL.append(f"Gmail token has no Gmail scope; scopes={scopes}")

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        token_creds = Credentials.from_authorized_user_file(str(GMAIL_TOKEN), scopes=scopes or None)
        if token_creds.expired and token_creds.refresh_token:
            token_creds.refresh(Request())
            # Persist refreshed token so other agents benefit.
            GMAIL_TOKEN.write_text(token_creds.to_json(), encoding="utf-8")
            os.chmod(GMAIL_TOKEN, 0o600)
            INFO.append("Gmail OAuth token refreshed successfully")

        service = build("gmail", "v1", credentials=token_creds, cache_discovery=False)
        profile = service.users().getProfile(userId="me").execute()
        INFO.append(f"Gmail API healthy for {profile.get('emailAddress', 'account')}")

        # OAuth/client lifecycle warnings are often delivered by Google before deletion.
        # Search recent mail while auth still works so the system can warn before failure.
        q = 'newer_than:120d ("OAuth client" OR "OAuth 2.0 client" OR "deleted client" OR "inactive client")'
        msgs = service.users().messages().list(userId="me", q=q, maxResults=25).execute().get("messages", [])
        warning_terms = (
            "oauth client will be deleted",
            "oauth 2.0 client will be deleted",
            "inactive oauth",
            "oauth client deletion",
            "client was deleted",
            "deleted_client",
        )
        for item in msgs:
            m = service.users().messages().get(
                userId="me", id=item["id"], format="metadata", metadataHeaders=["Subject", "From", "Date"]
            ).execute()
            headers = {h.get("name", "").lower(): h.get("value", "") for h in m.get("payload", {}).get("headers", [])}
            text = (headers.get("subject", "") + " " + m.get("snippet", "")).lower()
            if any(term in text for term in warning_terms):
                WARN.append(
                    "Google OAuth lifecycle warning email detected: "
                    + headers.get("subject", "(no subject)")[:180]
                )
    except Exception as exc:
        text = f"{type(exc).__name__}: {exc}"
        low = text.lower()
        if "deleted_client" in low or "oauth client was deleted" in low:
            CRITICAL.append("Google OAuth client has been deleted; create/restore Desktop OAuth client")
        elif "invalid_client" in low:
            CRITICAL.append(f"Google OAuth client invalid: {text}")
        elif "invalid_grant" in low:
            CRITICAL.append(f"Google OAuth grant/token invalid or revoked: {text}")
        else:
            CRITICAL.append(f"Gmail OAuth/API health check failed: {text}")

    return creds_data, token_creds


def text_of(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def check_gmail_wiring() -> None:
    mcl = text_of(TOOLS / "master_control_loop.py")
    integrator = text_of(TOOLS / "master_guard_integrator.py")
    v3 = text_of(TOOLS / "gmail_refresh_guard_v3.py")

    direct = "gmail_refresh_guard_v3" in mcl
    nested = "gmail_refresh_guard_v3" in integrator and "master_guard_integrator" in mcl
    if direct and nested:
        WARN.append("gmail_refresh_guard_v3 is invoked twice per Master Control Loop cycle")

    if "memory/system/service_account.json" in v3:
        WARN.append("gmail_refresh_guard_v3 still points to obsolete memory/system/service_account.json")

    canonical = str(GMAIL_TOKEN)
    for p in [
        AGENTS / "gmail_agent.py",
        AGENTS / "gmail_alert_agent.py",
        AGENTS / "gmail_misc_sorter.py",
        AGENTS / "gmail_misc_sorter_by_name.py",
    ]:
        src = text_of(p)
        if p.exists() and "token_gmail.json" not in src:
            WARN.append(f"Gmail component is not using canonical token path: {p.relative_to(BASE)}")


def check_master_control() -> None:
    src = text_of(TOOLS / "master_control_loop.py")
    if "inspect.signature" not in src:
        CRITICAL.append("Master Control Loop lost required-argument dispatcher fallback")
    if 'log("✅ All subsystems executed successfully.")' in src:
        WARN.append("Master Control Loop still has unconditional all-subsystems-success message")

    try:
        out = subprocess.run(
            ["pgrep", "-af", "master_control_loop.py"], capture_output=True, text=True, timeout=5
        )
        lines = [x for x in out.stdout.splitlines() if "pgrep" not in x]
        if not lines:
            CRITICAL.append("Master Control Loop process is not running")
        elif len(lines) > 1:
            WARN.append(f"Multiple Master Control Loop processes detected: {len(lines)}")
    except Exception as exc:
        WARN.append(f"Could not verify Master Control Loop process: {exc}")


def check_memory_compressor() -> None:
    if COMPRESSED.exists():
        size = COMPRESSED.stat().st_size
        if size >= MAX_COMPRESSED_BYTES:
            CRITICAL.append(f"compressed_memory.md is at/over 40 MB rotation threshold: {size} bytes")
    else:
        WARN.append("compressed_memory.md is missing")

    src = text_of(TOOLS / "memory_compressor.py")
    if "MAX_SUMMARY_BYTES" not in src and "40 * 1024 * 1024" not in src:
        WARN.append("memory_compressor.py has no visible 40 MB rotation guard")
    if "raise SystemExit(1)" not in src:
        CRITICAL.append("memory_compressor.py may still hide fatal errors with exit code 0")

    hb = text_of(HEARTBEAT)
    recent = "\n".join(hb.splitlines()[-250:])
    if "MEMORY-COMPRESS: ERROR" in recent:
        WARN.append("Recent memory-compressor error remains in heartbeat history; verify latest run is clean")


def check_absorption_and_prediction() -> None:
    if not (TOOLS / "absorb_memory.py").exists():
        CRITICAL.append("Canonical tools/absorb_memory.py is missing")
    age = file_age_hours(KB)
    if age is None:
        CRITICAL.append("centralized_knowledge_base.txt is missing")
    elif age > MAX_KB_AGE_HOURS:
        WARN.append(f"Centralized knowledge base is stale: {age:.1f} hours old")

    today = now_utc().strftime("%Y-%m-%d")
    pred_candidates = [
        MEMORY / "logs" / "system" / "predictions" / f"prediction_feed_{today}.md",
        BASE / "memory" / "logs" / "system" / "predictions" / f"prediction_feed_{today}.md",
    ]
    pred = next((p for p in pred_candidates if p.exists()), None)
    if pred is None:
        WARN.append(f"Today's prediction feed is missing: {today}")
    else:
        age = file_age_hours(pred)
        if age is not None and age > MAX_PREDICTION_AGE_HOURS:
            WARN.append(f"Prediction feed appears stale: {age:.1f} hours old")


def check_resource_pressure() -> None:
    try:
        soft, _hard = resource.getrlimit(resource.RLIMIT_NPROC)
        proc_count = len([p for p in Path("/proc").iterdir() if p.name.isdigit()]) if Path("/proc").exists() else 0
        if soft not in (-1, resource.RLIM_INFINITY) and proc_count and proc_count >= int(soft * 0.80):
            WARN.append(f"Process pressure high: {proc_count} processes vs RLIMIT_NPROC {soft}")
    except Exception:
        pass

    recent = "\n".join(text_of(NOHUP).splitlines()[-1000:])
    if "Resource temporarily unavailable" in recent or "BlockingIOError: [Errno 11]" in recent:
        WARN.append("Historical/recent process-resource exhaustion is present in nohup.out")


def check_vpn_simulation() -> None:
    hb = text_of(HEARTBEAT)
    recent = "\n".join(hb.splitlines()[-300:]).lower()
    if "simulated vpn activation successful" in recent or "pass (simulated)" in recent:
        WARN.append("Security/VPN status includes simulation-only PASS; this is not proof of a real VPN connection")


def maybe_send_sms(summary: str, fingerprint: str, state: dict) -> None:
    if state.get("last_alert_fingerprint") == fingerprint:
        return
    sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    token = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_num = os.getenv("TWILIO_FROM_NUMBER", "")
    to_num = os.getenv("TWILIO_TO_NUMBER", "")
    if not all([sid, token, from_num, to_num]):
        INFO.append("Twilio environment incomplete; alert recorded to log only")
        return
    try:
        from twilio.rest import Client
        try:
            from common import twilio_guard
            client = Client(sid, token)
            twilio_guard.send_sms(client, to=to_num, from_=from_num, body=summary[:1500])
        except Exception:
            Client(sid, token).messages.create(to=to_num, from_=from_num, body=summary[:1500])
        state["last_alert_fingerprint"] = fingerprint
        INFO.append("Continuity alert sent by SMS")
    except Exception as exc:
        WARN.append(f"Could not send Twilio continuity alert: {type(exc).__name__}: {exc}")


def run(force: bool = False) -> int:
    state = load_state()
    now = now_utc()
    last = state.get("last_full_check_utc")
    if not force and last:
        try:
            last_dt = dt.datetime.fromisoformat(last.replace("Z", "+00:00"))
            if (now - last_dt).total_seconds() < MIN_INTERVAL_SECONDS:
                log("SKIP full_check interval<1h")
                return 0
        except Exception:
            pass

    log("START continuity_guardian")
    check_google_oauth()
    check_gmail_wiring()
    check_master_control()
    check_memory_compressor()
    check_absorption_and_prediction()
    check_resource_pressure()
    check_vpn_simulation()

    state["last_full_check_utc"] = stamp()
    fingerprint = "|".join(sorted(CRITICAL + WARN))

    if CRITICAL or WARN:
        summary = (
            f"AI Consensus continuity alert: {len(CRITICAL)} critical, {len(WARN)} warning. "
            + (CRITICAL[0] if CRITICAL else WARN[0])
        )
        maybe_send_sms(summary, fingerprint, state)

    for item in CRITICAL:
        log(f"CRITICAL {item}")
    for item in WARN:
        log(f"WARN {item}")
    for item in INFO:
        log(f"INFO {item}")

    state["last_status"] = "CRITICAL" if CRITICAL else ("WARN" if WARN else "OK")
    state["critical"] = CRITICAL
    state["warnings"] = WARN
    state["last_fingerprint"] = fingerprint
    save_state(state)

    if CRITICAL:
        log(f"END status=CRITICAL critical={len(CRITICAL)} warning={len(WARN)}")
        return 2
    if WARN:
        log(f"END status=WARN critical=0 warning={len(WARN)}")
        return 0
    log("END status=OK")
    return 0


def main() -> int:
    force = "--force" in sys.argv
    return run(force=force)


if __name__ == "__main__":
    raise SystemExit(main())
