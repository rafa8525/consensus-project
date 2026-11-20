# ACS-03 / ACS-05 diagnosis from read-only public evidence

The public GitHub snapshot generated **2026-11-19T18:03:09Z** reports ACS-03 `execution_failure` and ACS-05 `critical`. This document is a research safety gate, **not a production repair**.

## ACS-03
The authoritative `v1.1-dev:agents/run_acs_cycle.py` runs:
- `health_connect_cloud_cycle`: `~/acs-runtime/repairs/acs03/cloud/health_connect_cloud_cycle.py` (private external script; exit 2 in public snapshot). Exact stderr and code cannot be established from the public repository.
- `fitness_tracking_verifier`: `tools/fitness_tracking_verifier.py` (exit 1). It requires genuine `memory/logs/fitness/daily_metrics.jsonl` records with a valid timestamp and numeric fitness measurement no older than 24 hours. Distinguish missing, stale, invalid and permission failures using private logs. Never synthesize records or touch timestamps to force success.
- `health_master` and `backup_fitness`: exit 0 in published snapshot.

## ACS-05
`agents/continuity_guardian_agent.py` inspects Master Control Loop wiring, Gmail/OAuth, Twilio notifications, recent successful run evidence, memory, prediction and security checks. The public health bridge converts sensitive messages to allowlisted categories; its published report includes `ORCHESTRATION_WIRING_WARNING` and `ALERT_DELIVERY_WARNING`. Category alone is **not a root-cause diagnosis**. Private guardian diagnostics, with secrets redacted, are required before modifying wiring or sending alerts.

## Safe verification gate
`acs_public_triage.py` reads a local copy of the public snapshot, never contacts production or reads secrets, calculates freshness using UTC, and returns categorized next investigations. The seven unit tests cover freshness, invalid timestamps, unhealthy components and disclosure boundaries.

To reproduce:
```sh
python3 -m unittest -v test_acs_public_triage.py
python3 acs_public_triage.py /path/to/pythonanywhere_health.json
```

Do not edit production until exact errors are collected, an independently tested patch is prepared, rollback is documented, and permission for production-critical modifications is confirmed. No new paid services, Slack or spammy healthy emails. Phase 1 remains uncertified until all gates are proven.
