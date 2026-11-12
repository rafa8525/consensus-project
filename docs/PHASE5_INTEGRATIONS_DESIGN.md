# Phase 5 — Personal integrations design and release gates

Date: 2026-11-12. Branch: `phase5-personal-integrations-design`.
Status: DESIGN ONLY. No personal data connections or production agents modified.

## Mission
Unify existing personal assistant workflows without duplicating functioning
automations. Prefer free integrations, permission minimization and clear evidence.

## Inventory and proposed priority
1. **Notifications and schedules:** inventory existing bill, package, sports,
   monitoring and reminder workflows. Do not recreate active tasks.
2. **Health / wearables:** mock COROS and wearable fitness records; use explicit
   authorization before accessing actual personal health data.
3. **Bills / shopping:** mock receipts and cost changes, avoid moving funds,
   payments, subscriptions or purchases without explicit approval.
4. **Entertainment:** mock streaming availability and preferences with current,
   attributable provider evidence.
5. **Devices / security:** design an adapter for public-Wi-Fi VPN detection,
   but require device-specific feasibility, consent, network security testing.
6. **Cross-device interface:** support accessible summaries and audit history.

## Adapter contract (design)
Each adapter must specify:
- Unique adapter ID, owner ACS agent, capability, data classification
- Input/output schema, UTC timestamp, source URI or evidence identifier
- Required permissions and explicit approval gate for sensitive actions
- Rate/cost limits (free tier only), independent availability checks
- Replay/idempotency key, timeout, bounded retry, circuit breaker
- Test fixture, recovery story, deletion/retention policy, rollback
- Observable success and failure signals; stale data policy

## Development and deployment rules
- Work exclusively with synthetic mock data until a particular connector and
  permissions are reviewed. Do not copy real personal records into GitHub.
- Existing monitoring routines remain single-source-of-truth. Never add a
  duplicate scheduler or surprise notification.
- Phase 1 health and alerting must remain unaffected.
- Phase 2 coordination and Phase 3 task memory must pass dependency gates
  before a live adapter writes or executes actions.
- Do not assume a connector offers free access or a particular API capability.
- Prove per-adapter tests, real service errors, permissions, outage handling,
  billing restrictions and independent verification before promotion.
- No unattended payments, security changes or self-modifying deployments.

## Initial acceptance gates
- [ ] Inventory existing workflows and owners, flag duplicates.
- [ ] Build an in-memory mock integration registry with least-privilege policy.
- [ ] Run tests for unauthorized access, stale evidence, data redaction,
      repeat delivery, outages and rollback.
- [ ] Produce exact-commit CI evidence and a production-readiness review.
- [ ] Obtain approval for any real sensitive-data use or external side effect.

The purpose is to make Phase 5 faster through reusable contracts, not to
bypass the safety and certification lessons of Phase 1.
