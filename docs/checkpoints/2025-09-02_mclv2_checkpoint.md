# Consensus Project — Checkpoint (2025-09-02)

## What worked (evidence-based)
- Guard thrash eliminated with mcl_guard_rc0safe.py; no respawn on rc=0.
- Single child via launch_mcl.py; stray main.py PIDs cleared; PIDs stable post-restart.
- Heartbeat file fresh (0–10s) during checks.
- Child stdout/err captured to memory/logs/system/mcl_child.{out,err}.
- Scheduler FNF warnings cleared by stubs (daily_voice_reminder & heartbeat_logger).
- Hivemind: 55 prompts generated; aggregator emits merged recs/report.
- Queue exercised; SMS job moved to done without crash.
- SMS safety on: ledger shows SKIP_DISABLED while Twilio is unwired.
- Log rotation via mcl_v2/logging_setup.py active.
- Tag set: stable-mclv2-bootstrap.

## Current wiring
- Supervisor: mcl_guard_rc0safe.py (backoff+cap; no respawn on rc=0)
- Entrypoint: launch_mcl.py → mcl_v2.main
- Env pass-through: guard → child (SMS_* vars supported)
- Defaults: SMS disabled; ledger at memory/logs/system/sms_ledger.jsonl

## Notable artifacts
mcl_guard_rc0safe.py, launch_mcl.py, start_guard.sh, hivemind/* (55 prompts), mcl_v2/logging_setup.py

## Open items
- SmsPolicy: define/use stable key consistently; verify from_env toggles (A/B tests).
- Ensure "sms decision" logs per job; add unit/integration tests for A/B/C paths.
- Twilio send path: implement guarded delivery once intentionally enabled.
