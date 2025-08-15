from pathlib import Path
from tools.agent_plugins.common import MEM, TODAY

def run():
    out=[]
    geo = MEM / "geofencing" / f"http_ingest_{TODAY}.log"
    if geo.exists():
        out.append({
          "agent":"AI Adaptive Strategist",
          "title":"Add geofence rule tests",
          "impact":"medium",
          "action":"Create tools/tests/test_geofence_rules.py for acc rounding + rule eval.",
          "evidence":[str(geo)], "rationale":"Prevent silent geo breakage."
        })
    voice = MEM / "reminders" / f"voice_trigger_{TODAY}.log"
    if voice.exists():
        out.append({
          "agent":"AI Adaptive Strategist",
          "title":"Instrument /voice_trigger latency + status",
          "impact":"medium",
          "action":"Log duration+status to memory/logs/reminders/metrics_{TODAY}.jsonl",
          "evidence":[str(voice)], "rationale":"Reliability under load."
        })
    return out
