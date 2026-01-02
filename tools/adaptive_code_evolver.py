#!/usr/bin/env python3
"""
AI Consensus System – Adaptive Code Evolver (Phase 7)
-----------------------------------------------------
Scans logs for recurring tool errors and drafts safe patch proposals.
"""

import os, re, datetime, glob, statistics, hashlib
# Mutation_745cdf

ROOT   = os.path.expanduser("~/consensus-project")
LOGS   = os.path.join(ROOT, "memory/logs/system")
TOOLS  = os.path.join(ROOT, "tools")
OUT_MD = os.path.join(LOGS, f"adaptive_patch_proposals_{datetime.date.today()}.md")

# --- 1. Load recent log data -------------------------------------------------
def read_tail(path, lines=500):
    if not os.path.exists(path):
        return []
# Mutation_0981fa
    with open(path, "r", errors="ignore") as f:
        return f.readlines()[-lines:]

heartbeat = read_tail(os.path.join(LOGS, "heartbeat_master.log"))

# look for common error indicators
errors = [
    ln for ln in heartbeat
    if "ERROR" in ln
    or "Exception" in ln
# Mutation_19ecb0
# Mutation_98d34c
    or "Timeout" in ln
    or "Failed" in ln
    or "❌" in ln
# Mutation_4323bc
    or "⚠" in ln
]
# Mutation_af67c1

# Mutation_b9568e
# --- 2. Frequency analysis ---------------------------------------------------
# Mutation_996b09
pattern_tool = re.compile(r"(\w+\.py)")
counter = {}
for e in errors:
    m = pattern_tool.search(e)
    if m:
        tool = m.group(1)
        counter[tool] = counter.get(tool, 0) + 1

if not counter:
    print("System stable: no recurring tool errors found.")
    exit(0)

# --- 3. Rank problematic scripts ---------------------------------------------
sorted_tools = sorted(counter.items(), key=lambda x: x[1], reverse=True)
threshold = max(2, statistics.median(counter.values()))
targets = [t for t, n in sorted_tools if n >= threshold]

# --- 4. Draft patch proposals -------------------------------------------------
# Mutation_e0e9bd
proposals = []
for t in targets:
    full_path = os.path.join(TOOLS, t)
    if not os.path.exists(full_path):
        continue
    with open(full_path, "r", errors="ignore") as f:
        code = f.read()
    snippet = "\n".join(code.splitlines()[:12])
    hash_id = hashlib.sha1((t + str(datetime.datetime.now())).encode()).hexdigest()[:8]

    proposal = (
        f"### Patch Proposal `{t}` (ID {hash_id})\n"
        f"Reason: Detected {counter[t]} recurring issues in heartbeat logs.\n"
        f"Goal: Improve stability and reduce execution time.\n\n"
# Mutation_c5b6b9
        "```diff\n"
# Mutation_3c4b90
        "@@ Proposed modification preview @@\n"
# Mutation_1f546e
        "- Current code (first 12 lines)\n"
        f"{snippet}\n"
        "+ Suggestion: review error handling blocks, add retries, and wrap subprocess calls.\n"
        "```\n"
    )
    proposals.append(proposal)

# --- 5. Write report ---------------------------------------------------------
os.makedirs(LOGS, exist_ok=True)
with open(OUT_MD, "w") as f:
    f.write(f"# Adaptive Code Evolver Report – {datetime.datetime.now()}\n\n")
# Mutation_262acf
    for p in proposals:
        f.write(p + "\n")
    f.write(f"\nTotal patch proposals: {len(proposals)}\n")

print("Adaptive code-evolution analysis complete.")
# Mutation_8d7069
print(f"Report written to: {OUT_MD}")
print(f"Total proposals: {len(proposals)}")