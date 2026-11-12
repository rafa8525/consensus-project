# Phase 4 — Offline autonomous improvement design (not production-enabled)

Date: 2026-11-12. Branch: `phase4-offline-optimization-design`.

## Purpose
Let ACS agents *propose* measurable improvements to their task-routing,
memory retrieval and retry policies without modifying production code or
configurations automatically. Every candidate must be tested in a sandbox,
compared against a fixed baseline and submitted for review.

## Lessons inherited from Phase 1–3
- Green CI alone never certifies live autonomy; require independent observed evidence.
- Do not create duplicate schedulers, duplicate agents or redundant health publications.
- Fail closed on stale/missing/inconsistent proof; capture exact commit and UTC timestamps.
- Preserve no-op safety, idempotency, bounded retries, task ownership and rollback.
- Treat failures per component; avoid global health scores masking a degraded agent.
- Prevent a claimed self-improvement from bypassing task ACLs or data provenance.
- Stay on free tools and synthetic data during development.

## Proposed offline workflow
1. **Baseline snapshot:** capture code SHA, deterministic fixture ID, metrics and limits.
2. **Candidate proposal:** named target, exact change, rollback path, risk category and measurable objective.
3. **Static preflight:** reject network calls, credential access, disallowed file writes and unspecified dependencies.
4. **Simulation trials:** fixed seeded mock tasks, error injection, duplicate events, crashes, stale inputs and concurrency.
5. **Evaluation:** compare success rate, duplicate-execution rate, unverified outcomes, latency and resource use against same baseline.
6. **Guardrails:** zero unauthorized writes, zero unexpected duplicate side effects, no unsupported recovery claims, no disclosure of private data.
7. **Decision:** mark candidate REJECTED, NEEDS_REVIEW or ELIGIBLE_FOR_REVIEW. Never auto-merge or auto-deploy.
8. **Evidence record:** exact SHA, fixtures, CI run ID, test outcomes, metric deltas and counterexamples.
9. **Human-controlled promotion:** only after Phase 1–3 dependency gates and independent review.

## Initial prototype acceptance criteria
- [ ] Offline evaluator consumes a fixed JSON fixture, not production logs.
- [ ] Rejects malformed, stale or incomparable evidence.
- [ ] Rejects any candidate with a safety guardrail regression even if faster.
- [ ] Deterministic, bounded test cases with negative cases.
- [ ] No external APIs, paid resources, production writes or self-modifying code.
- [ ] Independent GitHub Actions verification against the exact commit.
- [ ] Phase 4 design reviewed before implementation.

## Out of scope
Unrestricted recursive code rewriting, autonomous privilege changes, agent
creation without limits, real-money transactions, automatic live deployment and
claims that the AI is independently learning without evaluated evidence.

## Dependency status
Phase 1: certification outstanding.
Phase 2: simulation tests passed; production integration not certified.
Phase 3: isolated testing ongoing; real deployment and security approval pending.
Phase 4: design only. No production authorization.
