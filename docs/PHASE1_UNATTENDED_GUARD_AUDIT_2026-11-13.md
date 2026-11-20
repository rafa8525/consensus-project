# Phase 1 independent-scheduler audit — November 13, 2026

**Read-only source inspection. No production changes, no synthetic production proofs.**

## Directly verified GitHub evidence

- GitHub Actions scheduled execution, workflow `ACS-01 Independent Scheduler Guard`, run [43383660273](https://github.com/rafa8525/consensus-project/actions/runs/43383660273), created 2026-11-13T07:09:03Z, event `schedule`, conclusion `success`. Job 131746984660 reports:
  - `Recovery disabled: read-only decision, no schedule modifications.`
  - `{"changed": false, "mode": "dry_run", "report_status": "healthy", "status": "HEALTHY_NOOP", "task_id": 1524414}`
- Older scheduled run [43299490159](https://github.com/rafa8525/consensus-project/actions/runs/43299490159), created 2026-11-12T20:21:27Z, conclusion `failure`. Job 131466514183 reports:
  - `Recovery disabled: read-only decision, no schedule modifications.`
  - `{"changed": false, "mode": "dry_run", "report_status": "unhealthy_agents", "status": "ESCALATE_ENABLED_BUT_unhealthy_agents", "task_id": 1524414}`
- Earlier scheduled successful run [43176765800](https://github.com/rafa8525/consensus-project/actions/runs/43176765800) on 2026-11-12T07:38:34Z returned `HEALTHY_NOOP` with `changed=false`.
- The live default-branch workflow has `cron: "33 */6 * * *"` and checks `vars.ACS_SCHEDULER_RECOVERY_ENABLED`; only when equal to `true` on a schedule does it pass `--apply --allow-enable`. Recovery was **not enabled in these observed runs**. Do not print or change secrets.
- Actual run spacing shown in history exceeds the nominal six-hour cadence; GitHub documentation warns that scheduled jobs may be delayed or dropped. Avoid promising every six-hour execution without direct proof.

## Current production report

- `main:logs/system/pythonanywhere_health.json`, as read November 13, generated `2026-11-13T18:03:06.223794+00:00`: ACS-01..ACS-05 all current and healthy/ok; integrated ACS-01 task 1524414 reported enabled.
- `self_heal.recovery_proof.verified=false`, `test_type=observed_remote_divergence_recovery`, `not_tested=process_crash_and_external_scheduler_outage`.
- 22 tracked modifications, all under local `memory/` per owner-executed redacted inventory; preserve, don't reset.

## Certification outcomes — distinguish scopes

| Evidence | Finding |
| --- | --- |
| Unattended GitHub scheduler execution | **Verified** (run event `schedule`) |
| Authentication and PythonAnywhere task read | **Verified** by read-only guard run result and job exit code |
| Healthy no-op and bounded escalation of unhealthy report | **Verified** |
| Automatic scheduler re-enable from real disabled state | **NOT OBSERVED** |
| Autonomous recovery from actual production process crash | **NOT OBSERVED** |
| Accurate six-hour schedule delivery | **NOT ESTABLISHED** |
| Phase 1 certified | **NO** |

## Official guidance

- [GitHub scheduled workflow caveats](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows): scheduled triggers may be delayed or dropped.
- [GitHub scheduled workflow semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows): schedule is default-branch only; UTC schedule support.
- [PythonAnywhere schedule API](https://help.pythonanywhere.com/pages/API): GET task details, PATCH specific schedule fields.
- [GitHub repository variables](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables): repository Settings -> Secrets and variables -> Actions -> Variables.

## Specific remaining steps

1. Preserve existing production guard and its default-deny behavior pending explicit authorization for a change that would automatically re-enable real production tasks.
2. Review the `ACS_SCHEDULER_RECOVERY_ENABLED` repository variable and `ACS_SCHEDULER_MAINTENANCE` control; do not expose token values. The observed runs have recovery disabled, so scheduled recovery cannot yet be proven in production.
3. Continue read-only examination of scheduled run event, conclusion, timestamps, verdict, and reported task state. Treat observed missing/delayed schedules as reliability alerts, not automatic recovered incidents.
4. To prove a real scheduler-outage recovery **without intentional interruption**, wait for a naturally occurring disabled state; capture independent before/after scheduler details, enabled-state-only PATCH evidence, and subsequent scheduled execution. Otherwise require separate authorization for a controlled real intervention.
5. To prove real production process-crash recovery, capture an organically occurring crash and automatic restart evidence; isolated disposable-process tests do not substitute.
6. Check all Phase 1 acceptance evidence requirements; do not mark production proof as true based on branch-sync recovery, no-op checks, CI, simulations, or manually repaired configuration.

Phases 2–5 remain on their separate isolated development branch and are not production-certified.
