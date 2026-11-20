# Research-only agent role dispatcher (Milestone 2)
All 55 roles are loaded from `agents_registry.json`. **No actual AI agent is instantiated or executed.** The runtime provides a deterministic, static simulation of task assignment and evidence-record formats.

## Local run
From this directory:
```sh
python3 -m unittest -v test_runtime.py
python3 runtime.py --tasks demo_tasks.json --out run_record.json
```
The output is a JSON proposal record. It is NOT research evidence, real agent collaboration, or model training.

## Controls
- Only three operations: `review_hypothesis`, `design_experiment`, `evaluate_evidence`
- No shell command execution, network calls, cloud access, model API calls, or production writes
- At most 55 tasks per invocation, 500 characters per objective
- Rejects production-enabled definitions and unknown IDs
- Refuses to overwrite an existing output record
- Deterministic records with per-record SHA-256 content checksums

Eight local standard-library tests passed on 2026-11-19. Independent CI and environment verification are still required.

## Existing code audit (read-only)
Current `consensus/main.py` calls `planner.generate_plan()` and `researcher.enrich()` while the corresponding classes define `plan()` and `enrich_tasks()`. The caller also passes each task individually to `executor.execute(task)`, while the class expects a task collection. These are suspected interface faults; they are NOT established causes of ACS-03 or ACS-05 errors. Fix in a separate scoped patch after a regression test.

## Activation milestone
Agent roles remain `PROPOSED_UNVERIFIED`. Implement actual isolated worker adapters and evidence-backed execution later, after compute inventory, security limits and Phase 1 stability review. Do not merge this research branch into production or modify ACS-01 through ACS-05.
