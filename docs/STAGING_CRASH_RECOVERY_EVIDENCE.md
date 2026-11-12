# Disposable staging process-crash acceptance evidence

Date: 2026-11-12. Branch: `phase2-5-system-demo`.
Verified test commit: `e1875773f638a58f77ae76603cd3fe02a2793262`.
GitHub Actions run: https://github.com/rafa8525/consensus-project/actions/runs/43314554042
Observed CI job `isolated-system-acceptance`: SUCCESS, including:
- inherited Phase 2-5 regression suites;
- combined system synthetic acceptance suite;
- separately supervised staging process termination suite.

## Observed isolated test cases
- Ordinary child workflow completion: task `completed`, one persisted memory record, delivery `delivered`.
- Child terminated with OS exit code 71 from task mock handler: separate observer reads `running` in SQLite, zero persisted success evidence and zero notifications; restart maps task to `uncertain` and suppresses re-execution.
- Child terminated with OS exit code 72 from mock notification handler: separate observer reads completed task and evidence, `claimed` delivery; restart does not execute delivery again.
- Observation program opens SQLite mode=ro and is separate from the agent process; it does not import or execute agent functions.

## Boundaries — no release certification
The tested observer is independent **as a process**, not an independent external source or authenticated auditor. It does not prove a notification actually reached a real third-party system. An interrupted `claimed` event can stay unresolved and must be reconciled against trusted external receipts before it is retried or marked delivered.

This sandbox did not use:
- external services / API credentials, personal data, production schedules;
- cloud staging VM or live deployment;
- actual ACS-01..ACS-05 process authentication or complete 55-agent coordination;
- operational monitoring, hardened secrets, replicated data, full cross-process stress.

## Next release gates
- [ ] Independent trustable receipts for external tasks, with scoped read-only credentials.
- [ ] Staging runner with hardened OS permissions, backup and rollback.
- [ ] Simulated concurrent supervisor starts and SQLite lock contention chaos tests.
- [ ] Clear policy for reconciliation, retry approval and escalation of `uncertain` events.
- [ ] Phase 1 signoff and production readiness review with real external evidence.

**Do not merge or deploy this branch merely because CI is green.**
