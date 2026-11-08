# AI Consensus Project Memory

Purpose: persistent, evidence-based record of decisions, experiments, failures, and verified repairs. This is a documentation-only foundation; it does not activate any agent or scheduler.

## Read-before-write workflow
1. Read `current_status.md`, `repair_history.md`, `failed_attempts.md`, `verified_solutions.md`, `lessons_learned.md`, and `decisions.md` before proposing a repair.
2. Search existing records for the affected component and symptom; do not repeat a failed approach without a documented reason.
3. Record a hypothesis and a simulation/test plan before production changes.
4. After testing, append evidence and classify outcome as PROPOSED, TESTED, VERIFIED, FAILED, or UNKNOWN. Never equate a successful command with verified autonomous recovery.
5. Keep secrets, credentials, private personal information, and raw personal exports out of this repository. Link to safe issue/commit references instead.
6. Commit changes on a review branch; do not merge to `main` without approval.

## Entry template
Date (UTC):
Component:
Issue / symptoms:
Prior attempt references:
Hypothesis:
Change / command (redacted):
Simulation / test:
Evidence (safe path, commit, timestamp):
Outcome: PROPOSED | TESTED | VERIFIED | FAILED | UNKNOWN
Rollback / next action:

## Maintenance
Use append-only entries for history. Update `current_status.md` as evidence changes. A file written by an assistant is not proof that autonomous agents are reading or updating it.
