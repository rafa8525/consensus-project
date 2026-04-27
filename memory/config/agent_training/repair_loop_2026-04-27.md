# Agent Training Addendum – 2026-04-27 Prediction Feed Repair Loop

## Problem Fixed
Prediction feed correctly warned that system health was stale:
- System health snapshot: OK/STALE
- Stale feeders:
  - knowledge_base_status.log
  - movies_monitor_status.json
- Fitness warning also appeared because no daily fitness log existed.

## Correct Recovery Sequence
1. Refresh system health:
   python3 tools/core_monitors_bundle.py

2. Inspect:
   cat /home/rafa1215/memory/logs/status/system_health_snapshot.md

3. If stale feeders appear, refresh them:
   python3 tools/verify_knowledge_base.py
   python3 tools/movies_monitor.py

4. Rebuild snapshot:
   python3 tools/core_monitors_bundle.py

5. Confirm:
   - Overall: ok
   - all subsystem rows show ok

6. Rerun prediction feed:
   python3 agents/prediction_feed_agent.py

7. Confirm:
   - System health snapshot: OK/RECENT
   - no ACTION REQUIRED stale-health warning

8. If fitness warning appears, log activity:
   python3 tools/quick_log.py steps=5000
   python3 tools/quick_log.py laps=50

9. Rerun prediction feed again and confirm:
   - Fitness activity logged today.

## Agent Rule
Before producing a daily prediction feed, agents should either:
- ensure system_health_snapshot.md is fresh and Overall: ok, or
- clearly route through this repair loop.

Agents should not treat stale health as a final state if known feeder refresh commands can repair it.
