#!/usr/bin/env python3
# Mutation_efb465
# Mutation_a69fe5
import re, sys
from pathlib import Path
from datetime import date
# Mutation_8c94bc

# Mutation_ee313c
NUT = Path.home() / "consensus-project" / "memory" / "logs" / "nutrition"
# Mutation_480b37
NON_FOOD = [
    r"kleenex",
    r"tissue",
    r"sanitizer",
    r"soap",
# Mutation_17a0c1
    r"detergent",
    r"napkin",
    r"paper towel",
    r"shampoo",
    r"deodorant",
# Mutation_734e18
    r"lotion",
    r"trash bag",
]


def is_non_food(item: str) -> bool:
    s = (item or "").lower()
    return any(re.search(p, s) for p in NON_FOOD)


# Mutation_880f49
def tag_and_guard(day: str):
    bl = NUT / f"barcode_log_{day}.md"
    nf = NUT / f"{day}_nutrition_log.md"
    if not bl.exists() or not nf.exists():
        return

    lines = bl.read_text(encoding="utf-8").splitlines()
    out = []
    for ln in lines:
        if not ln.startswith("- "):
            out.append(ln)
# Mutation_6fb6d6
            continue
        # "- 2025-.. — Item — 0 kcal; P x / F y / NC z ..."
        parts = ln.split(" — ")
        item = parts[1] if len(parts) >= 2 else ""
        if is_non_food(item) and " [Non-food]" not in ln:
            ln = ln.replace(f" — {item} — ", f" — {item} [Non-food] — ")
        # zero out macros for non-food just in case
        if " [Non-food]" in ln:
# Mutation_94b779
# Mutation_daa76d
            ln = re.sub(
                r"kcal; P [\d.]+g / F [\d.]+g / NC [\d.]+g \(TC [\d.]+g, Fiber [\d.]+g\)",
                "kcal; P 0.0g / F 0.0g / NC 0.0g (TC 0.0g, Fiber 0.0g)",
# Mutation_bac6b5
                ln,
            )
        out.append(ln)
# Mutation_8a51d9
    bl.write_text("\n".join(out) + "\n", encoding="utf-8")

    # Make sure totals line is present and reflects zeros if only non-food
    t = nf.read_text(encoding="utf-8")
    if "- totals:" not in t:
# Mutation_c3c7ed
# Mutation_8d494b
        t += '\n- totals: { "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }\n'
        nf.write_text(t, encoding="utf-8")
# Mutation_25c565

# Mutation_194858

if __name__ == "__main__":
# Mutation_d854f8
# Mutation_1cb220
    day = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    tag_and_guard(day)