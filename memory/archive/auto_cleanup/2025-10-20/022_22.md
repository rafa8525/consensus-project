You are **22** — role: Modularize internals but ship single deployable file when needed.
Focus area: Deployable modularity
Support site(s): https://pypi.org/project/openai/

Read the **Master Brief** below, then return **only** the strict JSON schema at the end. Do not include commentary outside JSON.

--- MASTER BRIEF START ---
# Master Brief — Consensus Project (MCL v2 Stabilization)
## Context
- Legacy `master_control_loop.py` caused fork storms (Watchdog spawning), Twilio spam, and indentation/name errors after ad-hoc patches.
- We introduced:
  - `safe_loop.py` (minimal loop; SMS hard-disabled)
  - `mcl_guard.py` (heartbeat-based supervisor with restart ceilings)
  - `mcl_v2` plan (queue-based, coalesced jobs, bounded timeouts, SMS policy)
## Non-negotiables
- No SMS/calls unless explicitly enabled; quiet hours + whitelist + rate limits enforced.
- No file-watch → direct spawn; all external work via queue worker with timeouts.
- Heartbeat freshness < 2× period; guard must not thrash.
- Idempotent queue (processing/ → done/), never duplicate send.
- Python 3.10 compatible; light on processes/RAM for PythonAnywhere.
## Open Work
- Finalize `mcl_v2` package: queue worker, policy, scheduler, logging, CLI main.
- Hard test plan + migration: smoke test, guard test, then production flip.
- Twilio guardrails review (policy + ledger) and integration points.
## Acceptance Criteria
- 30+ minutes under guard w/out fork/timeout storms.
- SMS ledger shows only SKIP while disabled; DELIVERED only when re-enabled + whitelisted.
- No unhandled exceptions; clean shutdown removes lock.
## Reply Format (strict JSON in the agent’s response)
{
  "agent_name": "string",
  "primary_risks": ["string", ...],
  "recommendations": [{"title":"string","detail":"string","priority":1}],
  "code_changes": [{"path":"string","kind":"create|patch|replace","language":"python|bash|text","content":"..."}],
  "test_steps": ["string", ...],
  "references": ["url or doc id", ...]
}

--- MASTER BRIEF END ---

Return JSON with these keys exactly:
- agent_name
- primary_risks (array of strings)
- recommendations (array of {title, detail, priority[int 1-3]})
- code_changes (array of {path, kind, language, content})
- test_steps (array of strings)
- references (array)
