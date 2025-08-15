#!/usr/bin/env python3
import re, sys
from pathlib import Path
from datetime import date

NUT = Path.home() / "consensus-project" / "memory" / "logs" / "nutrition"
NON_FOOD = [r"kleenex", r"tissue", r"sanitizer", r"soap", r"detergent", r"napkin",
            r"paper towel", r"shampoo", r"deodorant", r"lotion", r"trash bag"]

def is_non_food(item: str) -> bool:
    s = (item or "").lower()
    return any(re.search(p, s) for p in NON_FOOD)

def tag_and_guard(day: str):
    bl = NUT / f"barcode_log_{day}.md"
    nf = NUT / f"{day}_nutrition_log.md"
    if not bl.exists() or not nf.exists(): return

    lines = bl.read_text(encoding="utf-8").splitlines()
    out = []
    for ln in lines:
        if not ln.startswith("- "): out.append(ln); continue
        # "- 2025-.. — Item — 0 kcal; P x / F y / NC z ..."
        parts = ln.split(" — ")
        item = parts[1] if len(parts) >= 2 else ""
        if is_non_food(item) and " [Non-food]" not in ln:
            ln = ln.replace(f" — {item} — ", f" — {item} [Non-food] — ")
        # zero out macros for non-food just in case
        if " [Non-food]" in ln:
            ln = re.sub(r"kcal; P [\d.]+g / F [\d.]+g / NC [\d.]+g \(TC [\d.]+g, Fiber [\d.]+g\)",
                        "kcal; P 0.0g / F 0.0g / NC 0.0g (TC 0.0g, Fiber 0.0g)", ln)
        out.append(ln)
    bl.write_text("\n".join(out) + "\n", encoding="utf-8")

    # Make sure totals line is present and reflects zeros if only non-food
    t = nf.read_text(encoding="utf-8")
    if "- totals:" not in t:
        t += '\n- totals: { "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }\n'
        nf.write_text(t, encoding="utf-8")

if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    tag_and_guard(day)
