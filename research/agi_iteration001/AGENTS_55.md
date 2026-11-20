# Project AGI — 55-agent proposed registry

This registry preserves **all 55 named agent concepts** from `agentscreatingotheragents.doc.txt` (2026-11-19) and maps them to Project AGI Version 3.0 research divisions.

**Important:** These are proposed **roles**, not evidence of 55 running agents. Every record is `PROPOSED_UNVERIFIED`, with `runtime_binding: null`, `execution_evidence: null`, and `production_enabled: false`. Source purposes are concise operational interpretations; the source document remains the canonical conceptual description.

## How to activate a role safely
1. Find an actual implementation in repository/authorized runtime.
2. Record path, version, owner, dependencies and runtime binding.
3. Verify unit/integration tests in a sandbox.
4. Verify task I/O, shared record format, resource caps, logging, safe retries and kill switch.
5. Obtain approval for any production-critical change, security permission, paid resource or irreversible action.
6. Only after evidence exists, change its lifecycle state with an independently reviewed record.

## Research divisions
- **Architecture Research:** 8 proposed roles
- **Learning Algorithms:** 6 proposed roles
- **Reasoning and Cognition:** 8 proposed roles
- **Scientific Research:** 11 proposed roles
- **Engineering and Infrastructure:** 7 proposed roles
- **Evaluation and Verification:** 4 proposed roles
- **Autonomous Recovery:** 1 proposed roles
- **Research Governance:** 10 proposed roles

## Red-line safeguards
Agent spawning, model mutation, autonomous deployment and speculative concepts are **design-only** until bounded experiments and independent evaluations exist. Conceptual titles (e.g., AI Sentience Architect, AI Post-Singularity Engineer, AI Reality Coder) do not imply those capabilities actually exist.

## Registry verification
Run `python3 validate_registry.py` next to the JSON. Requires Python standard library only. This verifies 55 unique source-defined IDs/names and no enabled production roles.

## Priority
Current published health snapshot at `logs/system/pythonanywhere_health.json` indicated ACS-03 degraded and ACS-05 critical on 2026-11-19; remediate and independently verify them before allocating production resources. This research branch must not modify ACS schedules or the default branch.
