# Subsystem Status Index (single source of truth)

> Update this file whenever a subsystem changes state, or when you rerun validations.
> Goal: make audits fast — every “OK” links to evidence.

## Core rollup
- Latest health snapshot: `memory/logs/status/system_health_snapshot.md`
- Latest project status: `memory/logs/system/project_status_latest.md`

## Subsystems
| Subsystem | Status file (expected) | Evidence folder | Last verified (PT) | Notes |
|---|---|---|---|---|
| absorption | `memory/logs/status/absorption_status.md` | `memory/logs/evidence/absorption/` |  |  |
| geofence_sms | `memory/logs/status/geofence_sms_status.md` | `memory/logs/evidence/geofence_sms/` |  |  |
| gmail | `memory/logs/status/gmail_status.md` | `memory/logs/evidence/gmail/` |  |  |
| vpn_auto_activation | `memory/logs/status/vpn_status.md` | `memory/logs/evidence/vpn/` |  | Link summary run(s) here |
| kbms (central KB) | `memory/logs/status/kbms_status.md` | `memory/logs/evidence/kbms/` |  | Spec + query proof |
| knowledge_sharing | `memory/logs/status/knowledge_sharing_status.md` | `memory/logs/evidence/knowledge_sharing/` |  | Dedupe + reuse metrics |
| fitness_tracking | `memory/logs/status/fitness_status.md` | `memory/logs/evidence/fitness/` |  | Daily + weekly outputs |
| predictions | `memory/logs/status/predictions_status.md` | `memory/logs/evidence/predictions/` |  | Feed + summaries |
| sms_daemon | `memory/logs/status/sms_daemon_status.md` | `memory/logs/evidence/sms_daemon/` |  | Rate limits + caps |

## Rules
- No subsystem is “OK” unless the status file links to **at least one evidence artifact** from the last 30 days.
- Every status file must include:
  - `Generated:` timestamp
  - `Status:` OK/WARN/FAIL
  - `Last verified:` timestamp (PT)
  - `Evidence:` links/paths
