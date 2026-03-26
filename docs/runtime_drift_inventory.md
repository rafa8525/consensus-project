# Runtime Drift Inventory

## Purpose
Track runtime path drift risks, intentional split-path behavior, repaired issues, and items that still need review.

## Status legend
- `intentional` = current behavior is by design
- `fixed` = issue was confirmed and repaired
- `review` = still needs inspection or later validation
- `legacy-risk` = likely future regression point if not watched

## Project baseline
As of 2026-03-23, the runtime is healthy and the health snapshot returned:

- `Overall: ok`

That healthy state was restored after fixing launcher drift, monitor drift, and refreshing stale writers.

## Current inventory

| Item | Current behavior | Status | Notes |
|---|---|---|---|
| `start_all.sh` | Launches `tools/master_control_loop.py` | fixed | Repaired on 2026-03-23 |
| `tools/master_control_loop.py` | Writes runtime logs to `~/consensus-project/memory/logs/system` | intentional | Repo-local runtime writer |
| `tools/core_monitors_bundle.py` | Checks both repo-local and canonical/shared paths where needed | fixed | Updated to remove false warnings |
| `weekly_status_report` monitor expectation | Monitor now recognizes `weekly_status_report.txt` in `memory/logs/system` | fixed | Old `.md` expectation was false |
| `knowledge_base_status.log` writer | Refreshed successfully by `tools/verify_knowledge_base.py` | fixed | Was stale, then recovered manually |
| `movies_monitor_status.json` writer | Refreshed successfully by `tools/movies_monitor.py` | fixed | Was stale, then recovered manually |
| Repo-local runtime memory | `~/consensus-project/memory/...` used by active orchestration | intentional | Do not rewrite blindly |
| Canonical/shared memory | `/home/rafa1215/memory/...` used by some shared scripts and markers | intentional | Do not rewrite blindly |
| Root-level `master_control_loop.py` references | Legacy path risk | legacy-risk | Audit periodically |
| Broad `/home/rafa1215/memory` references across repo | Mixed usage | review | Must be classified surgically, not mass-replaced |

## Incident summary: 2026-03-23 runtime recovery
The runtime incident was driven by several overlapping issues:

1. launcher drift
   - a launcher still pointed at the old root-level `master_control_loop.py`

2. monitor drift
   - the monitor expected paths or filenames that did not match live runtime output

3. path-root confusion
   - repo-local runtime files were fresh while canonical/shared-memory copies were stale

4. stale writers
   - `knowledge_base_status.log`
   - `movies_monitor_status.json`

## Repairs completed during recovery
The following repairs were completed and verified:

- fixed `start_all.sh` to use `tools/master_control_loop.py`
- updated `tools/core_monitors_bundle.py` so health checks matched real live files
- manually refreshed `knowledge_base_status.log`
- manually refreshed `movies_monitor_status.json`
- reran the health monitor and confirmed `Overall: ok`
- committed and pushed the runtime repair changes

## Verified Git checkpoint
Verified repair commit:

- `7b46079d2` — `Fix master control loop startup path and sync health monitor paths`

## Remaining review targets
These are not active failures, but they are future audit targets:

1. any remaining launcher or watchdog using the legacy root-level `master_control_loop.py`
2. any monitor that assumes `.md` when the live file is `.txt`
3. any script that reads canonical/shared memory when the live runtime writer is repo-local
4. any writer that repeatedly requires manual refresh and should be scheduled or supervised more clearly
5. any new runtime file introduced without path policy documentation

## Review method
For each future review target:

1. inspect the live writer path
2. compare to the runtime path policy
3. classify as:
   - intentional
   - fixed
   - review
   - legacy-risk
4. make the smallest safe correction only if needed
5. rerun health monitoring
6. update this inventory

## Rules for future updates to this inventory
Whenever a runtime issue is found, record:

- item name
- actual path behavior
- whether it is intentional or drift
- repair date if fixed
- proof of verification
- whether the issue is likely to recur

## Operating principle
This inventory exists to stop one-off troubleshooting from repeating.

If a runtime issue appears again:
- check this file first
- check `runtime_path_policy.md`
- check `runtime_recovery_playbook.md`
- only then change code