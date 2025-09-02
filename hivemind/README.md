# Hive Mind Prompt Pack (55 Agents)

## What this gives you
- `00_master_brief.md` – project context, constraints, acceptance criteria, **strict JSON reply schema**
- `prompt_template.md` – agent-specific prompt template
- `generate_agent_prompts.py` – builds 55 prompts from your CSV
- `hivemind_aggregator.py` – merges agents’ JSON replies into one unified plan
- `hivemind_replies/` – put agents’ JSON outputs here

## Quick start
1) Ensure your CSV exists (default: `55_Agents___Support_Sites.csv` in repo root).
2) Generate per-agent prompts:
   ```bash
   python3.10 hivemind/generate_agent_prompts.py 55_Agents___Support_Sites.csv

