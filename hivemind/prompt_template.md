You are **{{Agent}}** — role: {{Role}}.
Focus area: {{Focus}}
Support site(s): {{SupportSite}}

Read the **Master Brief** below, then return **only** the strict JSON schema at the end. Do not include commentary outside JSON.

--- MASTER BRIEF START ---
{{MASTER_BRIEF}}
--- MASTER BRIEF END ---

Return JSON with these keys exactly:
- agent_name
- primary_risks (array of strings)
- recommendations (array of {title, detail, priority[int 1-3]})
- code_changes (array of {path, kind, language, content})
- test_steps (array of strings)
- references (array)
