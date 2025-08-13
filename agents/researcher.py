from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import os, time, json, glob, statistics

from agents.core.agent_base import Agent

class Researcher(Agent):
    name = "researcher"

    def run(self) -> Dict[str, Any]:
        # Scan memory/logs for recent activity & staleness
        base = Path("memory/logs")
        findings = []

        # heartbeat staleness (absorption)
        hb = base / "heartbeat" / "memory_absorption_heartbeat.log"
        if hb.exists():
            last = hb.read_text(encoding="utf-8").strip().splitlines()[-1]
            findings.append(f"Absorption heartbeat tail: {last}")
        else:
            findings.append("WARN: memory_absorption_heartbeat.log missing")

        # geofence heartbeat today
        gf_hb = base / "geofencing" / f"heartbeat_{time.strftime('%Y-%m-%d', time.gmtime())}.md"
        if gf_hb.exists():
            last_g = gf_hb.read_text(encoding="utf-8").strip().splitlines()[-1]
            findings.append(f"Geofence heartbeat tail: {last_g}")
        else:
            findings.append("WARN: geofencing heartbeat for today missing")

        # git sync summary
        sync = base / "github_sync" / "sync.log"
        if sync.exists():
            tail = "\n".join(sync.read_text(encoding="utf-8").strip().splitlines()[-3:])
            findings.append("Git sync tail:\n" + tail)
        else:
            findings.append("WARN: github_sync/sync.log missing")

        md = "# Research snapshot\n\n" + "\n\n".join(f"- {x}" for x in findings) + "\n"
        out = self.write_artifact("knowledge_shared_{}.md".format(time.strftime("%Y-%m-%d", time.gmtime())), md)
        return {"report": str(out), "findings_count": len(findings)}
