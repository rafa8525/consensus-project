# Self-improvement suggestions

- Add alert: if heartbeat_error.log has entries today, page with guard.
- Add exponential backoff + jitter to heartbeat tasks; track consecutive failures.
- Keep rolling logs untracked; rotate per-day everywhere (verify weekly).
- Add unit tests for /voice_trigger and /geo; fail CI on regression.
- Add small e2e test that curls /healthz, /metrics, /voice_trigger (dry-run).
