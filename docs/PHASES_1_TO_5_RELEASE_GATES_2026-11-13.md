# AI Consensus System — Five-Phase Release Gates (2026-11-13)

This document is a **point-in-time engineering record**, not a production certification or authorization to deploy. Each phase stays gated independently; development tests must not be counted as real production operation.

## Verified evidence and exact refs

### Phase 1 — current production stability and recovery certification
- Existing PR: https://github.com/rafa8525/consensus-project/pull/37
- Reconciled acceptance head: `da23e74e372ad2c7b1fda726beb57745e20aa569`; draft, clean and mergeable at inspection.
- Exact-head checks: https://github.com/rafa8525/consensus-project/actions/runs/43474511775 and related successful acceptance / schedule-regression checks.
- Published production report: `main:logs/system/pythonanywhere_health.json`, generated `2026-11-13T07:05:49.367114+00:00`; all ACS-01..ACS-05 reported `verified:true` and acceptable health at that time.
- Explicit unresolved evidence: `self_heal.recovery_proof.verified=false`; process crash and external scheduler outage remain unproven in the production acceptance scope.
- PythonAnywhere source worktree reported 22 tracked changes. Audit and preserve these; do not reset or equate dirty tree with automatic failure.
- Acceptance requires authenticated, scope-correct, SHA-256-matched recovery artifacts and 3 independent qualifying report observations separated by at least 18 hours. Report freshness limit is 30 hours, with separate per-agent execution freshness horizon.

**Phase 1 release gate: FAIL / NOT CERTIFIED.** Green CI and five healthy snapshots are necessary but not sufficient. Do not run a live scheduler interruption or process crash without separate, explicit approval. Prefer passive observation of real failures; if controlled intervention is ever authorized, use verified backup, isolation, and automatic restoration conditions.

### Phase 2 — agent protocol and orchestration
- Source: `agents/phase2_*.py`; tests: `tests/test_phase2_*.py`.
- Verified only in synthetic CI: message schema validation, durable task journal, replay/idempotency protection, and conflict detection.
- Release blockers: authenticated agent identities, explicit capability permissions, real transport durability and end-to-end operational observation.

### Phase 3 — provenance memory
- Source: `agents/phase3_*.py`; tests: `tests/test_phase3_*.py`.
- Verified only in synthetic CI: persistent SQLite evidence, duplicate resistance, restart behavior, and isolated memory pipeline.
- Release blockers: secrets/data separation, retention/erasure, permissions, restoration proof, and trustworthy production provenance.

### Phase 4 — autonomous improvement
- Source: `agents/phase4_*.py`; tests: `tests/test_phase4_*.py`.
- Verified only in synthetic CI: offline baseline/candidate comparison and safety checks. `deployment_allowed` remains `false`.
- Release blockers: independently measured real performance, proposal review, rollback testing, and explicit production promotion authority. Never enable unbounded self-modifying deployment.

### Phase 5 — personal integrations
- Source: `agents/phase5_*.py`; tests: `tests/test_phase5_*.py`.
- Verified only in synthetic CI: mock-only adapter permissions, durable event claiming and duplicate suppression.
- Release blockers: approved live connector scopes, external provider receipts, safe reconciliation of uncertain effects, and privacy/consent controls. No real accounts or personal data in the synthetic fixture.

## Shared Phase 2–5 integration
- Development branch: `phase2-5-system-demo`.
- Previously passing full system CI: https://github.com/rafa8525/consensus-project/actions/runs/43315127790 at `5dcfa270106f8542498b23a0bd195b60524d6ce1`.
- Follow-up boundary regression tests whether the combined synthetic workflow attempts network or subprocess operations, added at commit `969f4d36a7154de6501554e846b25ce8aa35ae0e`; **check latest exact-commit CI result separately**.
- Existing-cloud staging preflight: `docs/EXISTING_CLOUD_STAGING_PREFLIGHT_2026-11-12.md`. Staging access, host isolation, cost and permissions were **not** verified, so no cloud staging deployment is claimed.

## Next safe steps in dependency order
1. Phase 1: preserve production, independently inventory local recovery artifacts and worktree changes; verify *actual* unattended recovery provenance, not green no-op/simulation results.
2. Phase 1: verify new daily production reports on the published GitHub `main` path; record the three qualifying independently spaced observations with a pinned acceptance revision and review the four required recovery proofs.
3. Phase 1: only after evidence is authentic and tests pass, review PR #37 for production promotion; preserve scheduler topology and obtain release approval.
4. Phases 2–5: verify all CI suites at exact new branch HEAD; maintain no-network mock boundary and review each subsystem's acceptance contract.
5. Phases 2–5: before any staging execution, use an existing authorized environment only after current read-only verification of IAM, billing, host isolation and rollback; no new paid resources or live ACS changes.
6. Phases 2–5: do not promote until Phase 1 is certified, external side-effect evidence is attributable and trusted, and release approval is obtained.

No production agent, scheduler, credential or private data is changed by maintaining this document.
