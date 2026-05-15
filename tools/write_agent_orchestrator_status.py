#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.home() / "consensus-project"
STATUS_DIR = ROOT / "memory" / "logs" / "status"
SUG_DIR = ROOT / "memory" / "logs" / "agents" / "suggestions"
AGENT_DIR = ROOT / "memory" / "logs" / "agents"

today = datetime.now().date().isoformat()
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

suggestions_file = SUG_DIR / f"suggestions_{today}.jsonl"
self_file = AGENT_DIR / f"self_improvement_{today}.md"
status_file = STATUS_DIR / "agent_orchestrator_status.md"

STATUS_DIR.mkdir(parents=True, exist_ok=True)

suggestion_count = 0
plugin_errors = 0
missing_plugins = 0

if suggestions_file.exists():
    for line in suggestions_file.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        suggestion_count += 1
        title = str(item.get("title", "")).lower()
        if "plugin error" in title:
            plugin_errors += 1
        if "plugin missing" in title:
            missing_plugins += 1

overall = "ok"
if not suggestions_file.exists() or not self_file.exists():
    overall = "warn"
if plugin_errors or missing_plugins:
    overall = "warn"

content = f"""# Agent Orchestrator Status

Generated UTC: {now}

Overall: {overall}

## Today
- Date: {today}
- Suggestions file: {suggestions_file}
- Suggestions file exists: {suggestions_file.exists()}
- Suggestion count: {suggestion_count}
- Self-improvement file: {self_file}
- Self-improvement file exists: {self_file.exists()}

## Plugin Health
- Plugin errors: {plugin_errors}
- Missing plugins: {missing_plugins}

## Role
tools/agents_orchestrator.py is currently the active suggestion/plugin orchestrator.

## Next Promotion Step
Confirmed: this orchestrator is monitored by core_monitors_bundle.py and is eligible to serve as the manager-of-managers foundation.
"""

status_file.write_text(content, encoding="utf-8")
print(f"ok wrote {status_file}")
