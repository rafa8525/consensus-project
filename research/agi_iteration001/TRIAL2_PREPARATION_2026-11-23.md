# Trial 2 prepared for review — NO NEW API SPEND

Version prepared November 23, 2026. This is a **non-executable candidate** for a second **separately authorized** live proposal test.

## What changed relative to trial 1
- Fixed, model-only request to `gpt-6-luna`, `tools=[]`, `store=False`, no auto-retries, no production access.
- Enlarges the visible + reasoning combined output allowance from **800 to 1600 tokens** to reduce potential incomplete responses. This may increase actual cost; this does **not** prove why trial 1 failed. No automatic second requests.
- Sanitized API failure categories, including `OUTPUT_TOKEN_BUDGET_EXHAUSTED` and HTTP status classes. No raw error body, key, request ID or proposal text is printed.
- Uses independent `YES-TRIAL-2` input and manual GitHub environment review; same restricted research branch.
- One request per runner invocation; GitHub **cannot** enforce a lifetime one-request quota, and billing project caps may overshoot. Revoke the key immediately afterwards.
- Immutable code SHA pinned to `25f362ed74f3227e44df815eb376b70791cb4a85`; unreviewed later research changes cannot silently modify the executed Python.
- No secret currently exists in `agi-research-live`, and the original key was revoked. The original run remains failed and must not be retried.

## Technical and scientific limitations
- No actual API call has been made for trial 2. Offline tests cannot certify live model compatibility, authentication, or spending.
- The generated proposal's alternatives remain predetermined baseline and two specific Naive Bayes variants; this only tests real model-driven structured-output generation and diagnostics, **not AGI, algorithm discovery, or autonomous self-improvement**.
- The result records a validated proposal SHA-256 hash but not the raw proposal. A hash alone is insufficient to independently study research quality, so a richer approved evidence protocol will be needed before claiming substantive AI research progress.
- The budget is 1600 output tokens, not a guaranteed financial limit. Fresh actual prices, model access, API spend, and project hard-limit setting must be checked before executing.
- The `main` workflow still pins OLD trial 1 code. **Nothing here modifies main or production.**

## Approval boundary
Before a trial 2 request: explicit authorization to (1) install reviewed trial 2 workflow metadata to `main` and matching research branch, (2) create and store a new project-scoped single-use key (user action), and (3) make **one additional possibly billed API request**. Until then, keep this file inert. Installation alone is not payment authorization.
