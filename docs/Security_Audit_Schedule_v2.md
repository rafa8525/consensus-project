# Security Audit Schedule (v2)

Frequency: Monthly
Owner/Trigger: Security & Privacy Manager (SPM) agent (or Watchdog)
Timezone: America/Los_Angeles (PT)

## Purpose
Assess and improve the security posture of the AI Consensus System.

## Next Audit Date
- **2026-02-01 (PT)**
- Recommended time: **09:00 PT**

## Required outputs (audit is not “done” without these)
Store under: `memory/logs/evidence/security/<YYYY-MM>/`

Minimum artifacts:
- `security_audit_<YYYY-MM>.md` (checklist + findings + actions)
- `secrets_scan_<YYYY-MM>.txt` (or `.md`)
- `dependency_snapshot_<YYYY-MM>.txt` (pinned versions list)
- `backup_restore_check_<YYYY-MM>.md` (proof that restore works)

## Audit checklist (high level)
- Secrets hygiene (no tokens committed, env separation verified)
- File permissions (least privilege, no world-writable)
- Dependency review (known CVEs / updates)
- Logging integrity (no missing days, tamper-evident where possible)
- Backup integrity (restore test)
- Network/VPN policies (public Wi-Fi handling verified)

## Notes
- Any “critical” finding requires an action item + follow-up verification date.
