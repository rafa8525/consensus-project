from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
import difflib, time
from agents.core.agent_base import Agent

PATCH_DIR = Path("memory/logs/agents/self_improvement_patches")

def ensure_header(lines: List[str], header: str) -> List[str]:
    if any(header in ln for ln in lines[:5]): return lines
    return [header + "\n"] + lines

class SelfImprover(Agent):
    name = "self_improver"

    def run(self) -> Dict[str, Any]:
        suggestions = []

        # Bash hardening for tools/*.sh
        for sh in Path("tools").glob("*.sh"):
            try: src = sh.read_text(encoding="utf-8").splitlines()
            except Exception: continue
            if not any("set -euo pipefail" in ln for ln in src[:5]):
                new = ensure_header(src[:], "#!/usr/bin/env bash")
                if "set -euo pipefail" not in "".join(new[:5]):
                    new.insert(1, "set -euo pipefail")
                patch = "\n".join(difflib.unified_diff(src, new, fromfile=str(sh), tofile=str(sh), lineterm=""))
                p = PATCH_DIR / f"{sh.name}.hardening.patch"
                p.write_text(patch, encoding="utf-8")
                suggestions.append(str(p))

        # Python __main__ guard suggestion where obvious
        for py in Path("tools").glob("*.py"):
            try: src = py.read_text(encoding="utf-8")
            except Exception: continue
            if "def main(" in src and "__name__" not in src:
                p = PATCH_DIR / f"{py.name}.main_guard.SUGGESTION.txt"
                p.write_text("if __name__ == '__main__':\n    main()\n", encoding="utf-8")
                suggestions.append(str(p))

        report = "# Self-improvement suggestions\n\n"
        report += "\n".join(f"- {s}" for s in suggestions) + ("\n" if suggestions else "No suggestions today.\n")
        out = self.write_artifact(f"self_improvement_{time.strftime('%Y-%m-%d', time.gmtime())}.md", report)
        return {"suggestions": len(suggestions), "report": str(out)}
