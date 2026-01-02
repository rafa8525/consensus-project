
## Defer: Web Research Fanout (55-agent crawl)
**Reason:** Console noise + time sink; to be revisited after core features are stable.  
**Done so far:** script drafted; quiet mode + retries; summary builder.  
**Open items:** refine CSV parsing on edge cases, tune concurrency, add sandbox limiter.  
**Acceptance:** run completes quietly (QUIET=1), produces `summary.csv` with ≥90% valid titles.


## Audit links
- Subsystem Status Index: docs/Subsystem_Status_Index.md
- Canonical VPN Test Plan: docs/VPN_AutoActivation_TestPlan.md
- Status Template v2: docs/Project_Status_Report_Template_v2.md
- Security Audit Schedule v2: docs/Security_Audit_Schedule_v2.md
