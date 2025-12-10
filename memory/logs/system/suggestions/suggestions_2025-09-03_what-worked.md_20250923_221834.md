# Consensus Project — What Worked (2025-09-03)

## Supervisor & Process Control
- **rc0-safe guard** (`mcl_guard_rc0safe.py`) stops respawning on clean exit; guard log shows single spawn and “child exited 0 — not respawning” behavior.
- **Single child** enforced via `launch_mcl.py`; stray `mcl_v2/main.py` PIDs eliminated. Lock (`memory/logs/system/mcl_v2.lock`) handled cleanly.
- **Heartbeat healthy** — `memory/logs/heartbeat/last_heartbeat.txt` stays fresh (0–10s age in checks).
- **Child stdout/err captured** to `memory/logs/system/mcl_child.{out,err}` for post-mortems.

## Logging & Hygiene
- **Rotating logs** via `mcl_v2/logging_setup.py` (file rotation active).
- Large system logs vacuumed/rotated to prevent disk bloat.

## Queue & Worker
- Queue jobs flow from `memory/queue/` → `processing/` → `done/` without crashes.
- **Worker return normalization** added in `mcl_v2/main.py` so the loop tolerates historical return shapes (bool / tuple / `.ok` objects) and no longer throws `"'tuple' object has no attribute 'ok'"`.

## SMS Policy (Safety First)
- **Corrected `SmsPolicy`** in `mcl_v2/sms_policy.py`:
  - `from_env()` reads `SMS_ENABLED`, `SMS_WHITELIST`, `SMS_QUIET_HOURS`.
  - **Whitelist required**: empty whitelist blocks; non-member numbers are skipped.
  - **Quiet hours** respected (observed `SKIP_QUIET_HOURS` with `00-23`).
  - `stable_key()` present; `record()` writes JSONL ledger with truncated bodies.
  - `decide()` accepts `**kwargs` to tolerate legacy callers (e.g., `body_preview`).
- **Legacy calls removed/redirected**: `should_send(...)` replaced with `decide(...)` across the queue path.
- **Ledger writes** to `memory/logs/system/sms_ledger.jsonl` showing `SKIP_*` outcomes while delivery remains intentionally disabled (no Twilio send path wired yet).

## Hivemind Toolkit
- **55 agent prompts generated**; aggregator produces merged recommendations/report.
- Repo contains prompts and merged artifacts under `hivemind/`.

## Source Control
- Branch **pushed to GitHub** (`git push -u origin HEAD`) with upstream set; prior checkpoint for 2025-09-02 added under `docs/checkpoints/`.

---

### Files & Artifacts (non-exhaustive)
- `mcl_guard_rc0safe.py`, `launch_mcl.py`, `start_guard.sh`
- `mcl_v2/sms_policy.py`, `mcl_v2/logging_setup.py`, `mcl_v2/main.py`
- `memory/logs/system/` (guard/child/app logs, SMS ledger)
- `hivemind/` (prompts, merged report)

### Notes
- Delivery remains **guarded** (no Twilio send) by design; current expected statuses are `SKIP_NOT_WHITELISTED` / `SKIP_QUIET_HOURS` until an explicit enable + whitelist + quiet-hours off is provided and a send path is intentionally wired.
