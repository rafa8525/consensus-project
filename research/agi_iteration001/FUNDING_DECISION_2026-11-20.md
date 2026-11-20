# Funding decision — 2026-11-20

The user explicitly declined purchasing prepaid OpenAI API credits and directed continuation of **no-cost preparation only**. This supersedes any inference that the earlier $1 API-usage authorization permits a credit purchase. The credit purchase modal showed a **$5 minimum purchase** and $10 default. User's screenshots show organization prepaid API credit balance **$0.00**, wallet $0.00, auto-reload **OFF**, and **AGI Research Sandbox** project spending limit **$1.00, enforced** at the time observed. These are historical screenshot observations, not live billing attestations.

## Authorized work
- Offline tests, preregistration, non-secret code changes, GitHub Actions research branch verification.
- Review existing source, research hypotheses and benchmark methodology.
- Keep live API adapter disconnected and fail closed.
- Preserve production ACS system, main branch and 55 proposed roles unchanged.

## Not authorized
- Credit purchases, enabling auto-reload, increasing spending limits.
- Any live OpenAI API call that could incur charges while credit balance is zero or project/credentials/usage are unverified.
- Secret upload, production deployment, autonomous retries or widening the live trial beyond one request.

## Resumption conditions
User separately authorizes a funding action **if they choose to**; or a legitimate existing credit balance becomes available without a purchase. Actual credits, project access and billing settings must then be freshly verified. A dedicated scoped API key must be stored securely without appearing in this repository or in chat, model pricing and access confirmed, and a single verified request budget enforced. The project hard limit may overshoot due to billing enforcement lag; it must not be presented as a hard guarantee of $1 total charges.

## Current decision
**Live AGI API experiment PAUSED / BLOCKED.** No additional user action is required to continue free preparation. There is no scheduled background process here.
