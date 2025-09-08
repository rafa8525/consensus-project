
## Defer: Web Research Fanout (55-agent crawl)
**Reason:** Console noise + time sink; to be revisited after core features are stable.  
**Done so far:** script drafted; quiet mode + retries; summary builder.  
**Open items:** refine CSV parsing on edge cases, tune concurrency, add sandbox limiter.  
**Acceptance:** run completes quietly (QUIET=1), produces `summary.csv` with ≥90% valid titles.

