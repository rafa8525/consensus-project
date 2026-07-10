# Prediction Feed – 2026-07-10
Generated: 2026-07-10T17:43:13.198998+00:00
Agent: prediction_feed_agent.py v2026-07-10-smart-feed-v1

## Health/Fitness
1. [HIGH] Today's fitness log was found (activity data).
   - Reason: At least one current-day fitness source was detected, so the missing-log warning was suppressed.
   - Evidence: /home/rafa1215/consensus-project/memory/logs/status/system_health_snapshot.md; /home/rafa1215/memory/logs/status/system_health_snapshot.md; /home/rafa1215/consensus-project/memory/logs/system/fitness_integration.log; /home/rafa1215/consensus-project/memory/logs/archive/system_health_snapshot.md

## Errands & Geofences
1. [LOW] No actionable errands were detected.
   - Reason: No grounded shopping-list, calendar, delivery, geofence, or task item was found; the old 'pick one small errand' filler was intentionally removed.

## Media & Fun
1. [LOW] Media summary: tracked=0, watched=0, suppressed/removed=0, maybe=0, candidates=0, unknown=0; last watched=Not available.
   - Reason: The feed now exposes meaningful status totals instead of only reporting that the list is unchanged.
   - Action: Refresh the verified U.S. streaming catalog only when candidates reach zero.
2. [MEDIUM] No verified streaming candidate is currently available.
   - Reason: The recommendation gate correctly rejects rent/buy-only, ambiguous, watched, suppressed, or unverified titles.
   - Action: Run the streaming-verification source refresh; do not bypass the gate with an unverified title.

## Family/Events
1. [MEDIUM] Next dated family event: [2026-07-10 17:37:35] Created missing log file: event_sync_guard.md
   - Reason: A current or future dated event was found.
   - Evidence: /home/rafa1215/consensus-project/memory/logs/archive/event_sync_guard.md

## System/Project
1. [MEDIUM] System health: WARN (0 minutes old). Details: | absorb_runner | warn | stale (10.5d old): /home/rafa1215/consensus-project/memory/logs/system/absorb_runner.log |; Overall: warn
   - Reason: The prediction feed now extracts warning details from the health snapshot instead of emitting only WARN/RECENT.
   - Action: Open the snapshot and latest monitor log; repair the first failing upstream component, then rerun this feed.
   - Evidence: /home/rafa1215/memory/logs/status/system_health_snapshot.md

## 24–72 Hour Predictions
1. [HIGH] The next movie recommendation run will likely return no pick.
   - Reason: There are zero verified candidates and the streaming gate is correctly blocking unsupported choices.
   - Action: Refresh verified U.S. streaming availability before the next recommendation cycle.
2. [MEDIUM] Prediction quality may remain degraded until the upstream health warning is cleared.
   - Reason: At least one current system-health finding is not OK.
   - Action: Resolve the first named health failure and rerun the health snapshot before relying on forecasts.
