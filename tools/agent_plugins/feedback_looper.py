from pathlib import Path
from tools.agent_plugins.common import MEM, TODAY, read_lines

def run():
    out=[]
    metrics = MEM / "agents" / f"metrics_{TODAY}.json"
    if metrics.exists():
        out.append({
          "agent":"AI Feedback Looper",
          "title":"Convert agents/metrics into weekly retro",
          "impact":"low",
          "action":"Write memory/logs/project-updates/agents_weekly_retro_{}.md".format(TODAY),
          "evidence":[str(metrics)], "rationale":"Turn signals into action."
        })
    nut = MEM / "nutrition" / f"{TODAY}_nutrition_log.md"
    if nut.exists() and '"cal": 0' in nut.read_text(encoding="utf-8"):
        out.append({
          "agent":"AI Feedback Looper",
          "title":"Nutrition totals are zero today",
          "impact":"low",
          "action":"Prompt to scan/add entries; verify barcode sync task ran.",
          "evidence":[str(nut)], "rationale":"Keto tracking completeness."
        })
    return out
