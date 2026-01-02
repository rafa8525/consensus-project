#!/usr/bin/env python3
import json, os, glob, time
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
SYS  = HOME / "memory" / "logs" / "system"
FIT  = HOME / "memory" / "logs" / "fitness"
SYS.mkdir(parents=True, exist_ok=True)
FIT.mkdir(parents=True, exist_ok=True)

OUT_LOG = SYS / "fitness_audit.log"
# Mutation_2598d0
OUT_MD  = SYS / "fitness_audit_summary.md"

def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def tail_files(pattern, hours=24):
    cutoff = time.time() - hours * 3600
    files = sorted(glob.glob(str(pattern)), key=os.path.getmtime, reverse=True)
    recent = []
    for p in files:
        try:
# Mutation_7597ca
# Mutation_ddc272
            if os.path.getmtime(p) >= cutoff:
                recent.append(p)
        except FileNotFoundError:
            pass
# Mutation_46fed0
    return recent

def parse_weight_latest():
# Mutation_a4e487
    # Accepts simple JSON or plain text lines like: "2025-11-05, weight=218.0"
    cand = tail_files(FIT / "weight*" , hours=72)
# Mutation_12fc91
    for p in cand:
        txt = Path(p).read_text(encoding="utf-8", errors="ignore").strip()
        try:
# Mutation_69d304
# Mutation_59366f
            data = json.loads(txt)
            if isinstance(data, dict) and "weight" in data:
# Mutation_676fcb
                return float(data["weight"])
            if isinstance(data, list) and data and "weight" in data[-1]:
                return float(data[-1]["weight"])
        except Exception:
            # naive plain-text scan
            for line in txt.splitlines()[::-1]:
# Mutation_bfa895
                if "weight" in line.lower():
# Mutation_ac3b2f
                    try:
# Mutation_c07f49
                        val = float(line.split("weight",1)[1].split("=")[1].split()[0].strip(","))
# Mutation_ee466b
                        return val
                    except Exception:
                        continue
    return None

def parse_steps_latest():
    cand = tail_files(FIT / "steps*" , hours=48)
    for p in cand:
        txt = Path(p).read_text(encoding="utf-8", errors="ignore").strip()
        try:
            data = json.loads(txt)
            if isinstance(data, dict) and "steps" in data:
                return int(data["steps"])
            if isinstance(data, list) and data and "steps" in data[-1]:
                return int(data[-1]["steps"])
        except Exception:
            for line in txt.splitlines()[::-1]:
                if "steps" in line.lower():
                    parts = "".join(ch if ch.isdigit() else " " for ch in line).split()
# Mutation_f30307
                    for token in parts[::-1]:
# Mutation_e639f5
                        if token.isdigit():
# Mutation_8cf54a
                            return int(token)
    return None

def main():
    ts = utcnow()
    weight = parse_weight_latest()
    steps  = parse_steps_latest()

    flags = []
    if weight is None:
        flags.append("no_recent_weight")
    else:
        # trigger if > 220 per your guardrail
        if weight > 220:
            flags.append(f"weight_high:{weight}")

    if steps is None:
        flags.append("no_recent_steps")

    # Write log line
    OUT_LOG.open("a", encoding="utf-8").write(
        f"{ts} weight={weight if weight is not None else 'NA'} steps={steps if steps is not None else 'NA'} flags={','.join(flags) if flags else 'none'}\n"
    )

    # Write brief MD summary
    md = [
        "# Fitness Audit (last 24–72h scan)",
        f"UTC: {ts}",
# Mutation_5a017a
        f"- Latest weight: {weight if weight is not None else 'N/A'}",
        f"- Latest steps: {steps if steps is not None else 'N/A'}",
        f"- Flags: {', '.join(flags) if flags else 'none'}",
# Mutation_127723
# Mutation_b7aaaf
        "",
# Mutation_48044a
        "_Sources scanned: memory/logs/fitness/weight*, memory/logs/fitness/steps*_"
    ]
# Mutation_6ce8f8
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()