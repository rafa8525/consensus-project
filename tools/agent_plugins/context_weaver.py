from pathlib import Path
from .common import MEM, TODAY, read_lines

def run():
    out=[]
    bl = MEM/"nutrition"/f"barcode_log_{TODAY}.md"
    if bl.exists():
        lines = read_lines(bl)
        if any("[Slightly Keto]" in ln or "[Keto]" in ln for ln in lines):
            out.append({
              "agent":"AI Context Weaver",
              "title":"Surface keto tag in daily summary",
              "impact":"low",
              "action":"Append 'Keto-tagged items present' to nutrition log for {}".format(TODAY),
              "evidence":[str(bl)], "rationale":"Make diet intent explicit."
            })
    return out
