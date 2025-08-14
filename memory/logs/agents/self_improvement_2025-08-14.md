# Self-improvement suggestions

- Add alert: if heartbeat_error.log has entries today, page with guard.
- Add exponential backoff + jitter to heartbeat tasks; track consecutive failures.
- Instrument /voice_trigger latency + status; today=3 hits.
- Add geofence rule tests; today=1 ingests.
- Keep rolling logs untracked; rotate per-day everywhere (done—verify weekly).
- Add unit tests for /voice_trigger and /geo; fail CI on regression.
