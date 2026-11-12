# ACS-03 fault localization — 2026-11-12

Read-only code inspection plus tested diagnostic utility. No production edits.
Branch: `repair/acs03-readonly-diagnosis-20261112`.
Test commit: `61beb51667862c38bc8c95582f00e1f20c1d424f`.
Passing test job: https://github.com/rafa8525/consensus-project/actions/runs/43327699804

## Observed from published evidence
The latest fetched `main:logs/system/pythonanywhere_health.json` generated 2026-11-12T18:03:06Z shows ACS-03 `execution_failure`:
- unknown component, returncode 2 (cannot determine actual source until local state inspected)
- fitness_tracking_verifier, returncode 1
- health_master, returncode 0
- backup_fitness, returncode 0

`v1.1-dev:agents/run_acs_cycle.py` requests:
1. `~/acs-runtime/repairs/acs03/cloud/health_connect_cloud_cycle.py`
2. `~/consensus-project/tools/fitness_tracking_verifier.py`
3. `~/consensus-project/tools/health_master.py`
4. `~/consensus-project/tools/backup_fitness.py`

The health-cycle first script is outside the repository; its presence cannot be inferred from GitHub. The `unknown` label may indicate a missing component key or a different runtime version. Do not infer its identity.

The verifier reads `~/consensus-project/memory/logs/fitness/daily_metrics.jsonl` by default. It fails closed on missing/symlink input, lack of valid timestamped numeric measurements, measurements older than 24 hours, or future-only records.

## Next inspection
Need authorized, read-only PythonAnywhere console inspection to execute a privacy-safe *copy of the tested diagnostic*, or its equivalent, on the runtime. Never publish or paste full fitness measurements or the raw ACS-03 state; output only redacted status, component identifiers, exit codes, source-file presence, coarse age, and source size.

## Phase 1 certification separately blocked
PR #37 is open, draft and mergeable_state=`dirty`, meaning conflicts. No production merge or modification should occur until conflict resolution is reviewed; achieving a mergeable PR is not certification. Production recovery proofs and three distinct qualifying reports remain required.

## Policy
Do not fabricate fitness data or touch timestamps to make the verifier green. Do not alter health results to hide the defect. Do not install or schedule new tasks merely to generate apparent healthy evidence.
