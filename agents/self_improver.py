from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
import difflib, re, os, time

from agents.core.agent_base import Agent

PATCH_DIR = Path("memory/logs/agents/self_improvement_patches")

def ensure_header(lines: List[str], header: str) -> List[str]:
    if any(header in ln for ln in lines[:5]):
        return lines
    return [header + "\n"] + lines

class SelfImprover(Agent):
    name = "self_improver"

    def run(self) -> Dict[str, Any]:
        """
        Dry-run self-improvement:
        - Scan simple issues (bash scripts missing 'set -euo pipefail'; Python files missing __main__ guards).
        - Propose minimal patches as .patch files (no automatic apply).
        """
        suggestions = []
        # 1) Bash hardening suggestions
        for sh in Path("tools").glob("*.sh"):
            try:
                src = sh.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            if not any("set -euo pipefail" in ln for ln in src[:5]):
                new = src[:]
                new = ensure_header(new, "#!/usr/bin/env bash")
                if "set -euo pipefail" not in "".join(new[:5]):
                    new.insert(1, "set -euo pipefail")
                patch = "\n".join(difflib.unified_diff(src, new, fromfile=str(sh), tofile=str(sh), lineterm=""))
                p = PATCH_DIR / f"{sh.name}.hardening.patch"
                p.write_text(patch, encoding="utf-8")
                suggestions.append(str(p))

        # 2) Python __main__ guard suggestions (tiny example)
        for py in Path("tools").glob("*.py"):
            try:
                src = py.read_text(encoding="utf-8")
            except Exception:
                continue
            if "def main(" in src and "__name__" not in src:
                patch_text = f"# Suggest adding:\nif __name__ == '__main__':\n    main()\n"
                p = PATCH_DIR / f"{py.name}.main_guard.SUGGESTION.txt"
                p.write_text(patch_text, encoding="utf-8")
                suggestions.append(str(p))

        # summary
        report = "# Self-improvement suggestions\n\n"
        if suggestions:
            report += "\n".join(f"- {s}" for s in suggestions) + "\n"
        else:
            report += "No suggestions today.\n"
        out = self.write_artifact(f"self_improvement_{time.strftime('%Y-%m-%d', time.gmtime())}.md", report)
        return {"suggestions": len(suggestions), "report": str(out)}
