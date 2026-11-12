# Phase 2 integration and certification gate

Created 2026-11-12. This checklist is a promotion gate, not an assertion of production certification.

## Verified evidence
- Isolated development branch: `phase2-agent-coordination`.
- Acceptance commit: `be60ec9915d64a1ee7a75a8668c87c54bdd5a52d`.
- GitHub Actions run: https://github.com/rafa8525/consensus-project/actions/runs/43296535957 — completed successfully.
- The test suite covers protocol, legacy Planner/Executor adapter, mock multi-agent router, SQLite journal, safe restart behavior, mock evidence reconciliation, and end-to-end simulated interruption.
- Tests run in a separate GitHub Actions job with no secrets or write permission (`contents: read`).

## Not yet proven — BLOCKERS to production
- [ ] Review ownership, actual schema, and authorization mapping for real ACS-01..ACS-05 agents. Current mock identities and trust model are not production authentication.
- [ ] Test independently caused real process termination and clean restart in a non-production sandbox, with external timestamps and evidence artifacts.
- [ ] Test atomicity and concurrent-process claims, including SQLite database locks and partial transactions.
- [ ] Validate verifiers against trusted external evidence rather than injected mock functions. A self-reported proof string is not independent evidence.
- [ ] Prove safe semantics for tasks where a handler may have executed externally but crashed before recording success.
- [ ] Define durable storage location, backup, recovery, retention, access controls and sensitive-data policy.
- [ ] Assess error classification: programming/validation failures should not receive automatic blind retries.
- [ ] Test performance, backpressure, race conditions, journal corruption, and rollback strategy.
- [ ] Run production-readiness review against exact candidate commit; require independent reviewer signoff and artifacted results.
- [ ] Check Phase 1 certification and compatibility gates before any production wiring.

## Release principles
- Phase 1 remains an independent critical path. No production scheduler, credentials, or agent configuration changes from this branch.
- Mock-only simulation pass does NOT certify production behavior.
- Every deployment requires staged rollout, telemetry, bounded permissions, explicit rollback, and post-deploy evidence.
- Keep the original `main` branch and Phase 1 PR #37 undisturbed.
- Phase 3 may build on this tested contract **in an isolated branch only**, acknowledging that the dependency is not yet released.
