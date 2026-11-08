# Decisions

## 2026-11-08 — Use existing GitHub repository for project memory
Decision: Keep the project memory as Markdown in `memory/project/` in `rafa8525/consensus-project`.
Rationale: Reuse existing repository, Git version history, and connected read/write access; avoid introducing a new paid service.
Safety: Start on a separate review branch, do not change runtime files or schedulers, and do not merge without approval.
Deferred: Automatic agent writeback and inter-agent memory integration until the five repair phases are verified.
