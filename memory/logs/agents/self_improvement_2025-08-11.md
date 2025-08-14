# Self-improvement suggestions

- Add alert: if heartbeat_error.log has entries today, page with guard.
- Add exponential backoff + jitter to heartbeat tasks; track consecutive failures.
- Refine Twilio guard: classify blocked texts; add tag-based allowlist.
- Expose blocked/sent counters in /metrics to spot spikes.
- Keep rolling logs untracked; rotate per-day everywhere (done—verify weekly).
- Add unit tests for /voice_trigger and /geo; fail CI on regression.
