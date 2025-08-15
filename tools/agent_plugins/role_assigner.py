from .common import iso_now
def run():
    return [{
      "agent":"AI Role Assigner",
      "title":"Ownership map for today’s suggestions",
      "impact":"info",
      "action":"Evolutionist→alerts; Code Spawner→tests/ci; Strategist→geo/voice; Feedback Looper→retro; Context Weaver→nutrition signal.",
      "evidence":[],
      "rationale":"Clear owners avoids suggestion rot.",
      "ts": iso_now()
    }]
