# ACS Health Reliability Recovery — 2026-10-14

This document is an operational recovery procedure, **not a declaration of repair**. The repository is public: do not publish OAuth tokens, Gmail messages, environment files, PythonAnywhere exception tracebacks containing secrets, or a copy of modified source before checking for sensitive data.

## Evidence and boundaries

- GitHub Actions run 38558911844: 14 watchdog/public snapshot tests passed; the live health check failed.
- Published `logs/system/pythonanywhere_health.json` (2026-10-14 07:02 UTC): ACS-01 degraded, ACS-02 healthy, ACS-03 execution_failure, ACS-04 WORKTREE_DIRTY, ACS-05 critical with Google OAuth/Gmail issue code.
- Branch synchronization blocked: `blocked_local_source_changes`; 36 tracked changes. These are **not** safe to discard automatically.
- Scheduler API reported `acs01_task` and `health_task` enabled. This confirms configuration at snapshot time, **not** that every agent succeeds.
- The isolated health-publishing mechanism is functioning. Keep it independent from the live PythonAnywhere checkout.
- `main` and `v1.1-dev` have diverged substantially. Never mass-merge or force-reset them as an incident workaround.
- Job cleanup warns about orphaned gitlink `memory/github_memory_repo` lacking a matching `.gitmodules` entry; diagnose separately. Node 20/action version warnings are also independent from the actual health failure.

## Non-destructive incident procedure

1. On PythonAnywhere, enter the project and record `git status --porcelain=v1`, `git branch -vv`, `git diff --stat`, and `git ls-files -u` to a **private**, timestamped incident directory outside the repository.
2. Create a **private** archive of modified tracked files, untracked required configuration, and a patch of working-tree changes. Restrict permissions; validate archive readability and hashes. Never put the archive or its contents in the public repository.
3. Classify every modified tracked file as intentional code, generated runtime data, local configuration, or sensitive data. Compare against `origin/v1.1-dev` only after `git fetch`. Move generated runtime data outside Git and update ignores using a reviewable change.
4. Do not run `git reset --hard`, `git clean -fd`, history rewrites, blind `git stash pop`, or force pushes. Resolve source changes in a separate worktree and review diffs. Preserve the original live checkout for rollback.
5. Diagnose ACS-05 in the private runtime: inspect the *sanitized* error category, token expiry/revocation, configured OAuth client and scopes. Reauthorize only through the legitimate provider, with user involvement when consent is necessary. Do not print credentials to CI or commit token files.
6. Diagnose ACS-03 from private exception traces; record only redacted exception categories and failing components in issues. Restore execution via a tested source change, not a fabricated success timestamp.
7. Rerun ACS-04 and verify tracked changes fall to zero **only after** intentional changes are preserved; address agent-specific infrastructure findings and orphaned submodule metadata separately.
8. Run ACS-01 orchestration; verify all five agents with real execution evidence and health statuses. Ensure ACS-02 remains healthy.
9. Publish a fresh redacted snapshot via the existing isolated bridge. Check schema, timestamps, each agent's `verified`, `status`, `health_status`, and scheduled task availability. Re-run the watchdog. **Do not weaken its thresholds to turn red green.**
10. Run failure-injection regression tests: unavailable scheduler, stale/missing snapshot, unhealthy agent, blocked branch sync, OAuth revoked, agent crash, and failed publish. Verify alerts are actionable and recovery cannot silently report success.

## Acceptance criteria

- ACS-01 through ACS-05 each have fresh, verified, healthy execution evidence, with failures honestly represented.
- PythonAnywhere's two required scheduled tasks are independently verified available and enabled, and their actual executions are observable.
- No unreviewed local changes or credentials are lost; private backup and tested rollback exist.
- Source changes and runtime-generated data are isolated; repeated health publishing no longer creates unreviewed source modifications.
- Main-vs-development branch reconciliation uses reviewed, bounded changes rather than an indiscriminate merge.
- Continuous scheduled watchdog runs succeed for at least two consecutive expected windows **after** upstream defects are genuinely repaired; fault injection still causes failure.
