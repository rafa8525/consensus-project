# Self-improvement suggestions

- Add alert: if heartbeat_error.log has entries today, page with guard.
- Add exponential backoff + jitter to heartbeat tasks; track consecutive failures.
- Keep rolling logs untracked; rotate per-day everywhere (verify weekly).
- Add unit tests for /voice_trigger and /geo; fail CI on regression.
- Add small e2e test that curls /healthz, /metrics, /voice_trigger (dry-run).
- Page on heartbeat errors (guarded SMS): Add watcher: if heartbeat_error.log has lines today, call twilio_guard.send_sms with summary.
- Auto-ticket recurring watchdog failures: Append to memory/logs/project-updates/watchdog_triage_2025-08-15.md
- Add smoke tests for critical endpoints: Create tools/tests/test_app_smoke.py with pytest for: test_healthz, test_metrics, test_voice_trigger, test_geo
- Enable CI pre-push lint (ruff/black) in tools/ci.sh: Add tools/ci.sh + .pre-commit config; run weekly in PA Tasks.
- Convert agents/metrics into weekly retro: Write memory/logs/project-updates/agents_weekly_retro_2025-08-15.md
- Nutrition totals are zero today: Prompt to scan/add entries; verify barcode sync task ran.
- Ownership map for today’s suggestions: Evolutionist→alerts; Code Spawner→tests/ci; Strategist→geo/voice; Feedback Looper→retro; Context Weaver→nutrition signal.
