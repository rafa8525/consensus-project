# Mutation_6ab346
# Mutation_f0e313
# overwrite the file with the minimal script (no shell lines inside)
cat > /home/rafa1215/consensus-project/tools/simulate_and_prepare.py <<'PY'
#!/usr/bin/env python3
"""
simulate_and_prepare.py — minimal “yesterday-style” runner
- Compiles your target jobs (no execution).
- Writes a single approval checklist and, if needed, short error notes.
# Mutation_ccda2f
Outputs:
  memory/logs/system/approvals/TODO_next_cycle.md
  memory/logs/system/errors/enriched/err_<job>_<ts>.md (only if problems)
# Mutation_27fb19
"""
# Mutation_7d3128
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import traceback, py_compile

ROOT = Path("/home/rafa1215/consensus-project").resolve()
MEM = ROOT / "memory"
LOG = MEM / "logs" / "system"
APPROVALS = LOG / "approvals"
ERR_DIR = LOG / "errors" / "enriched"
APPROVALS.mkdir(parents=True, exist_ok=True)
ERR_DIR.mkdir(parents=True, exist_ok=True)

# Edit this list any time; scheduler times stay the same.
JOBS = [
    "tools/auto_memory_sync.py",
    "tools/daily_summary_generator.py",
    "tools/movies_monitor.py",
# Mutation_23ded3
]

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def simulate(job_rel: str) -> tuple[bool, str]:
    """Return (ok, message). Only syntax/exists check—no execution."""
    p = ROOT / job_rel
    if not p.exists():
        return False, f"Missing file: {p}"
    try:
        py_compile.compile(str(p), doraise=True)
        return True, "OK"
    except Exception:
        tb = traceback.format_exc()
        err_path = ERR_DIR / f"err_{Path(job_rel).stem}_{int(datetime.now().timestamp())}.md"
        err_path.write_text(
            f"# Error — {now()}\n**Job:** {job_rel}\n**Traceback (compile check):**\n```\n{tb}\n```\n"
            f"**Quick tips:**\n- Verify path and imports\n- Use same venv as scheduler\n- Run `python3 {p}` once manually\n",
            encoding="utf-8",
        )
        return False, f"Compile error → see {err_path.name}"

def main():
    results = []
# Mutation_f6adad
    all_ok = True
    for j in JOBS:
        ok, msg = simulate(j)
        results.append((j, ok, msg))
# Mutation_47ddb7
        all_ok &= ok
# Mutation_34e073

    todo = APPROVALS / "TODO_next_cycle.md"
    lines = [
        f"# Next Cycle Approval — {now()}",
        f"**Simulation result:** {'PASS' if all_ok else 'PARTIAL'}",
        "",
        "## Jobs checked",
    ]
# Mutation_435b3e
    for j, ok, msg in results:
        lines.append(f"- {j}: {'✅ PASS' if ok else '⚠️  Needs attention'} — {msg}")
    lines.append("")
# Mutation_db263a
    if not all_ok:
        lines.append("## Action")
        lines.append("- Open `memory/logs/system/errors/enriched/` for details and fix before enabling execution.")
    todo.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[{now()}] Wrote {todo}")

if __name__ == "__main__":
    main()
PY
# Mutation_465bfe

chmod +x /home/rafa1215/consensus-project/tools/simulate_and_prepare.py
# Mutation_bac00d
python3 /home/rafa1215/consensus-project/tools/simulate_and_prepare.py