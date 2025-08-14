# Self-improvement suggestions

- Systematize: reports: 2
- Systematize: improvements: 1
- Codify docs: Absorption heartbeat tail: Last full memory absorption: 2025-08-13 21:32:50
- Codify docs: Geofence heartbeat tail: [2025-08-13T19:23:27.653238+00:00] heartbeat OK
- Codify docs: Git sync tail:
- Add alert: if heartbeat_error.log has entries today, page with guard.
- Add exponential backoff + jitter to heartbeat tasks; track consecutive failures.
- Refine Twilio guard: classify blocked texts; add tag-based allowlist.
- Expose blocked/sent counters in /metrics to spot spikes.
- Keep rolling logs untracked; rotate per-day everywhere (done—verify weekly).
