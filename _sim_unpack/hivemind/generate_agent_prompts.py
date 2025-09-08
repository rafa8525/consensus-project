#!/usr/bin/env python3
import csv, re, sys
from pathlib import Path
ROOT = Path.home()/ "consensus-project"/ "hivemind"
PROMPTS = ROOT/"hivemind_prompts"
MASTER = ROOT/"00_master_brief.md"
TEMPLATE = ROOT/"prompt_template.md"

def slugify(s:str)->str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+","-", s).strip("-")
    return s[:60] or "agent"

def main(csv_path:str):
    if not MASTER.exists(): raise SystemExit("Missing 00_master_brief.md")
    if not TEMPLATE.exists(): raise SystemExit("Missing prompt_template.md")
    master = MASTER.read_text(encoding="utf-8")
    tpl = TEMPLATE.read_text(encoding="utf-8")
    PROMPTS.mkdir(parents=True, exist_ok=True)
    n=0
    with open(csv_path, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        required = {"Agent","Role","Focus","SupportSite"}
        if not required.issubset(rdr.fieldnames or []):
            raise SystemExit(f"CSV must include headers: {sorted(required)}")
        for idx,row in enumerate(rdr, start=1):
            agent = (row.get("Agent") or "").strip()
            role  = (row.get("Role") or "").strip()
            focus = (row.get("Focus") or "").strip()
            site  = (row.get("SupportSite") or "").strip()
            if not agent: 
                continue
            body = tpl.replace("{{Agent}}", agent)\
                      .replace("{{Role}}", role)\
                      .replace("{{Focus}}", focus)\
                      .replace("{{SupportSite}}", site)\
                      .replace("{{MASTER_BRIEF}}", master)
            name = f"{idx:03d}_{slugify(agent)}.md"
            (PROMPTS/name).write_text(body, encoding="utf-8")
            n+=1
    print(f"Generated {n} prompts in {PROMPTS}")

if __name__ == "__main__":
    if len(sys.argv)<2: 
        print("Usage: generate_agent_prompts.py <path/to/55_Agents___Support_Sites.csv>")
        sys.exit(2)
    main(sys.argv[1])
