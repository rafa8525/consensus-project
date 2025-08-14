#!/usr/bin/env python3
import re
from datetime import date
from pathlib import Path

BASE   = Path.home() / "consensus-project"
NUTDIR = BASE / "memory" / "logs" / "nutrition"
NUTDIR.mkdir(parents=True, exist_ok=True)

# Accept "YYYY-MM-DD_nutrition_log.md" or legacy "YYYY-MM-DD.md"
P_STD = re.compile(r"^(\d{4}-\d{2}-\d{2})_nutrition_log\.md$")
P_LEG = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")

TEMPLATE = """# Nutrition — {day}
- ts: {iso}
- meals: []
- totals: {{ "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }}
- notes: ""
"""

def iso_today():
    return date.today().isoformat() + "T00:00:00Z"

def normalize_file(p: Path) -> bool:
    m_std = P_STD.match(p.name)
    m_leg = P_LEG.match(p.name)
    if not (m_std or m_leg):
        return False

    day = (m_std or m_leg).group(1)
    target = NUTDIR / f"{day}_nutrition_log.md"

    # Rename legacy filename to standard
    changed = False
    if p != target:
        p.rename(target)
        p = target
        changed = True

    # Ensure header + required keys
    orig = p.read_text(encoding="utf-8") if p.exists() else ""
    lines = [ln.rstrip().replace("\t", "  ") for ln in orig.splitlines()]
    if not lines:
        p.write_text(TEMPLATE.format(day=day, iso=iso_today()), encoding="utf-8")
        return True

    need_header = not lines[0].startswith("# Nutrition —")
    if need_header:
        lines.insert(0, f"# Nutrition — {day}")
        changed = True
    elif lines[0] != f"# Nutrition — {day}":
        lines[0] = f"# Nutrition — {day}"
        changed = True

    # Ensure keys exist at least once
    content = "\n".join(lines) + "\n"
    def ensure(key_snippet, default_line):
        nonlocal content, changed
        if key_snippet not in content:
            content = content.rstrip() + "\n" + default_line + "\n"
            changed = True

    ensure("- ts:", f"- ts: {iso_today()}")
    ensure("- meals:", "- meals: []")
    ensure("- totals:", '- totals: { "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }')
    ensure("- notes:", '- notes: ""')

    if changed and content != orig:
        p.write_text(content, encoding="utf-8")
    return changed

def main():
    changed = 0
    for p in sorted(NUTDIR.iterdir()):
        if p.is_file():
            try:
                if normalize_file(p):
                    changed += 1
            except Exception:
                # Skip any weird files; keep going
                pass
    print(f"nutrition_normalize: changed={changed}")

if __name__ == "__main__":
    main()
