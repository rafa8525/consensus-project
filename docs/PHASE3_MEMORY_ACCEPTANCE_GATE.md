# Phase 3: memory + execution development gates

Created 2026-11-12. Status: development only; not production certified.

## Dependency baseline
Phase 3 branches from `phase2-agent-coordination` so the latest isolated task protocol, mock router, SQLite journal, and mocked reconciliation can be reused. The Phase 2 code is not yet certified for production.

## Implemented prototype
- `agents/phase3_memory.py`: simulated SQLite evidence memory with immutable evidence IDs, task binding, agent attribution, source reference, deterministic lookup, restart persistence and corruption failure.
- `tests/test_phase3_memory.py`: isolated regression tests.
- `.github/workflows/phase3-memory-tests.yml`: intended to run Phase 2 dependency tests plus Phase 3 tests on this branch.
- No personal data, production scheduling, network calls, third-party API calls, or runtime integration.

## Acceptance gates
- [ ] CI must pass against the exact candidate commit with recorded workflow run ID.
- [ ] Explicitly test two-process concurrent inserts, duplicates and lock behavior.
- [ ] Verify provenance with trusted external sources; current free-form `source_ref` is an identifier, not cryptographic proof.
- [ ] Add authorization *per task and read principal*; the current prototype allows reading any task ID and is not suitable for real personal information.
- [ ] Add retention and deletion controls, backup, schema migration, secure file permissions and storage encryption policy.
- [ ] Connect memory and execution only via mock adapters first; validate idempotency and crash boundaries.
- [ ] Validate actual crash-and-restart behavior with independent evidence, not just reopening a journal.
- [ ] Security review, dependency verification, rollback and data handling review before production promotion.

## Rule from Phase 1
A green automated test suite establishes tested simulation behavior only. Production reliability and autonomy require separately observed evidence and explicit certification. No phase advancement based solely on a successful GitHub run.
