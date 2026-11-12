# Phase 1 Lessons and Delivery Rules for Phases 2–5

Status: adopted as development guidance, not a claim of Phase 1 certification.
Created: 2026-11-12
Scope: isolated development and test branches; no production deployment without gates.

## What we learned from Phase 1
1. A successful command or green CI run does not itself prove end-to-end autonomous operation. Demand independently observed scheduled runs, published evidence, and a repeatable acceptance test.
2. Separate the actual production execution path from redundant or imagined schedules. ACS-01 is the integrated parent for PythonAnywhere health publishing; avoid requiring an unnecessary standalone health scheduler.
3. Treat evidence freshness explicitly. Use timestamp validation and clear thresholds, and distinguish source execution time from publication time and watchdog check time.
4. Health must be judged per agent and per component, not by a single aggregate 'success'. ACS-03 fitness_tracking_verifier still reports an execution failure as of the 2026-11-12 18:03 UTC health snapshot.
5. A repository worktree with tracked changes is an investigation/housekeeping signal, not automatic proof of failure. Separate Git cleanliness, sync status, and runtime functionality.
6. A recovery feature is not certified by a healthy no-op. Test a safely induced failure and externally verify recovery, including proof that a watchdog can run without a manual trigger.
7. All acceptance scripts must run against the exact commit under review and reject malformed, missing, stale, or contradictory evidence (fail closed).
8. Preserve working production behavior; make a small reversible change, test in isolation, and avoid cascading repairs or premature merges.
9. Alert with actionable context and deduplication rather than repeated banners. Do not integrate Slack (not used).
10. Report accurately: distinguish implemented, tested, observed in production, and certified. Never promote a phase on assumptions.

## Required workflow for every later-phase feature
1. Establish a single written feature contract: owner agent, inputs, outputs, permissions, dependencies, and what 'done' means.
2. Prefer existing code (planner, executor, researcher, memory manager) after inspection; do not build duplicates.
3. Implement in an isolated branch, with free tools, no credentials in Git, and production writes disabled by default.
4. Add unit and contract tests first, plus negative tests for invalid inputs, retries, duplicate messages, stale data, timeouts, and partial failures.
5. Run a simulated end-to-end test and capture run IDs, timestamps, commit SHA, and evidence artifacts.
6. Validate actual automation separately: externally observed scheduled execution and data publication, not just a one-off manual execution.
7. Require idempotency, bounded retry/backoff, audit trails, and a clear rollback for any write-capable agent.
8. Use a reviewer/acceptance gate that rejects unverified recovery, stale evidence, unsafe permissions, or unresolved failed tests.
9. Deploy in small stages after dependency gates are met; never treat parallel development as permission to deploy uncertified code.
10. Write a brief completion record: test results, accepted risks, remaining issues, rollback command, and next dependency.

## Phase implementation order and parallelism
- Phase 1: certification remains a separate, active critical path. No Phase 2–5 changes in its production runtime before authorized, tested promotion.
- Phase 2: agent planning, common agent schema, inter-agent task envelope and acknowledgements. First deliverable is a tested schema and message protocol, not an always-on orchestration change.
- Phase 3: memory and execution; prototype only after Phase 2 contract is stable, and require persistence, provenance, access control, deduplication, and safe retries.
- Phase 4: autonomous improvement; start with offline scoring and simulated improvements; prohibit unrestricted self-modifying production code.
- Phase 5: personal integrations; prototype adapters against mock data, require explicit consent for sensitive actions, verify provider availability, and stay within free tiers.
- Develop independent features in parallel. Certify and deploy only when each feature's real dependency gates are satisfied.

## Current baseline (point-in-time, not a live promise)
- 2026-11-12 18:03 UTC published health snapshot: ACS-01, ACS-02, ACS-04, ACS-05 healthy; ACS-03 degraded (fitness_tracking_verifier error).
- The snapshot reports recovery_proof.verified=false; process crash and external scheduler outage remain untested.
- Pull Request #37 remains open as of 2026-11-12; do not declare Phase 1 certified.
- Run all current-status checks afresh before making a deployment decision.

## Phase 2 initial acceptance criteria
- JSON schema defines agent ID, role, authorized actions, task envelope, correlation and idempotency keys, status, evidence, timestamp, retry policy, and error codes.
- Planner -> executor -> result -> acknowledgement test works with mocks and no production calls.
- Failure-mode tests pass for duplicate deliveries, out-of-order updates, malformed messages, timeouts, and agent errors.
- No unexpected production side effects; commit SHA and test output documented.
- Independent review of contract and tests before any promotion.
