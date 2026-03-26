# Runtime Path Policy

## Purpose
Prevent path drift, false health warnings, and restart failures in the AI Consensus Project runtime.

## Current architecture
The project currently uses two memory roots:

1. Repo-local runtime memory:
   - `~/consensus-project/memory/...`

2. Canonical/shared memory:
   - `/home/rafa1215/memory/...`

This split is currently intentional in parts of the system and must not be changed blindly.

## Canonical runtime rules

### Main runtime entrypoint
The correct main loop entrypoint is:

- `tools/master_control_loop.py`

Do not use the legacy root-level path:

- `~/consensus-project/master_control_loop.py`

### Repo-local runtime memory
Use `~/consensus-project/memory/...` for repo-local runtime artifacts produced by project orchestration, including files such as:

- `memory/logs/system/master_control_loop.log`
- `memory/logs/system/heartbeat.md`
- `memory/logs/system/weekly_status_report.txt`
- `memory/logs/system/movies_monitor_status.json`
- `memory/logs/system/knowledge_base_status.log`
- other runtime logs written by `tools/master_control_loop.py` and related repo-local writers

### Canonical/shared memory
Use `/home/rafa1215/memory/...` for canonical shared or user-facing memory, including files such as:

- long-lived shared memory artifacts
- public markers intended for external reading
- exports intended to be consumed outside repo-local runtime behavior
- scripts explicitly designed around canonical memory

## Monitor policy
`tools/core_monitors_bundle.py` must remain truthful.

That means it must:
- check actual live writer paths
- avoid false warnings caused by filename mismatches
- avoid false warnings caused by root mismatches
- check both memory roots when the architecture is intentionally split

## Launcher policy
All launchers, watchdogs, restart helpers, and recovery scripts must use:

- `tools/master_control_loop.py`

Any legacy references to the old root-level `master_control_loop.py` path must be treated as drift or a regression risk.

## Change policy
Before changing any runtime path:

1. Inspect the live writer path first.
2. Determine whether the current path is intentional or drift.
3. Do not mass-replace `/home/rafa1215/memory` references.
4. Use the smallest safe patch.
5. Run preflight validation.
6. Re-run health monitoring.
7. Record the result in the runtime drift inventory.

## Preflight validation standard
Before any runtime path or launcher change:

### For Python files
- `python3 -m py_compile <file>`

### For shell files
- `bash -n <file>`

### After changes
- run `tools/core_monitors_bundle.py`
- read `system_health_snapshot.md`
- confirm the warning state reflects reality

## Operating principle
Healthy writers should not be rewritten just because a monitor or launcher assumes a different path.

When possible:
- patch the incorrect monitor
- patch the incorrect launcher
- preserve working writers unless there is a strong reason to move them

## Verified lesson from 2026-03-23
The runtime outage was primarily caused by:
- a broken launcher path
- false monitor assumptions
- a repo-memory vs canonical-memory mismatch
- a stale-writer situation that became visible only after the false warnings were removed

The correct response pattern is:
- inspect
- patch surgically
- verify
- document