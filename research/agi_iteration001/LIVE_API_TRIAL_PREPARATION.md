# One-shot live OpenAI API proposal experiment — preparation and approval gate

## Explicit user authorization
The user authorized **preparation** of a single bounded model-backed research experiment with up to **$1.00 USD** in API usage, conditional on verifying a dedicated API project, securely scoped credentials and billing safeguards. This is **not** authorization to bypass the condition, change production, enroll paid services, or increase the cap.

## Platform findings (November 20, 2026)
Official OpenAI Help Center documentation confirms project and organization spend limits with optional **Enforce a hard limit**. Alerts are not limits. Enforcement is not instantaneous; reported spend can exceed configured limits slightly.
- https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform
- https://help.openai.com/en/articles/6614457-troubleshooting-api-usage-and-spend-limits
- https://help.openai.com/en/articles/10478918-reviewing-api-usage-and-costs

## Account-specific preflight: NOT VERIFIED
- [ ] Dedicated API project identity and owner inspected via authenticated API platform connection.
- [ ] `Enforce a hard limit` visibly enabled for the selected project; a $1 or lower monthly limit verified.
- [ ] Month-to-date spend and remaining allowance verified; no other workloads share the project. $1 of remaining allowance is needed if using the full $1 authorization. Enforcement may still slightly overshoot.
- [ ] Model ID and price schedule confirmed using current official model pricing.
- [ ] Project-scoped, least-privilege API credential configured within an approved secret store **without exposing keys in chat, GitHub, CI logs or source**.
- [ ] Project model access and request limits verified.
- [ ] Single successful independently authenticated project+limit verification before any call, and a fresh usage read immediately before it.
- [ ] One no-tools, no-retries, `store=False` Responses request with bounded tokens, timeouts, strict structured output, no deployment actions.
- [ ] Inspect actual usage after the request, log nonsecret receipt and independently evaluate the proposed experiment.
- [ ] Any missing/ambiguous check -> STOP WITHOUT A CHARGE. A dollar estimate is not a billing guarantee.

## Implementation state
`live_trial_readiness.py` adds a **local declaration validator**, using the earlier estimated-cost gate. It never makes API calls and deliberately returns `proposal_api_call_permitted=False` even if every claimed check passes. Local booleans are not trusted provider attestations. The existing M17 Responses adapter is also not wired to the production or offline executor. **There is currently no verified connected OpenAI API project, no credential, no chosen approved model, and no remote billing evidence. No real call has been made.**

## Research-science limitation
The existing M17 adapter only proposes from three preselected Naive Bayes variants, so a first live call would test SDK wiring and bounded structured-output compliance—not novel AI algorithm discovery. Before claiming new research capability, create a separate meaningful problem with an expanded allowlisted hypothesis DSL and a genuinely untouched third-party evaluation source. Do not claim the user has approved any broader training or experimentation.
