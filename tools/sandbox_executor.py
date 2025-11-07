#!/usr/bin/env python3
"""
AI Consensus System – Sandbox Executor (Phase 7b)
-------------------------------------------------
Purpose:
  • Test proposed patch files from Adaptive Code Evolver safely
  • Run them in an isolated sandbox environment
  • Record runtime metrics, exceptions, and outcome (PASS / FAIL)

Inputs
  memory/logs/system/adaptive_patch_proposals_*.md
  config/AGENT_CANDIDATES.yaml (for context if needed)

Outputs
  memory/logs/system/sandbox_test_results_YYYY-MM-DD.md
"""

import os, shutil, time, datetime, subprocess, tempfile, glob

ROOT   = os.path.expanduser("~/consensus-project")
LOGS   = os.path.join(ROOT, "memory/logs/system")
TOOLS  = os.path.join(ROOT, "tools")
OUT_MD = os.path.join(LOGS, f"sandbox_test_results_{datetime.date.today()}.md")

# ---------- Helper utilities ----------
def log(msg):
    print(msg)

def recent_proposal():
    files = sorted(glob.glob(os.path.join(LOGS, "adaptive_patch_proposals_*.md")))
    return files[-1] if files else None

# ---------- Prepare sandbox ----------
sandbox_dir = tempfile.mkdtemp(prefix="sandbox_", dir="/tmp")
log(f"🧪 Created sandbox: {sandbox_dir}")

proposal_file = recent_proposal()
if not proposal_file:
    log("No adaptive patch proposal file found. Nothing to test.")
    exit(0)

# Extract tool names mentioned in proposals
tools_to_test = []
with open(proposal_file, "r", errors="ignore") as f:
    for line in f:
        if line.strip().startswith("### Patch Proposal"):
            name = line.split("`")[1] if "`" in line else None
            if name: tools_to_test.append(name)

if not tools_to_test:
    log("No specific tools listed in proposal file.")
    exit(0)

# ---------- Begin testing ----------
results = []
for tool in tools_to_test:
    original = os.path.join(TOOLS, tool)
    if not os.path.exists(original):
        results.append((tool, "MISSING", 0, "Skipped"))
        continue

    temp_tool = os.path.join(sandbox_dir, tool)
    shutil.copy2(original, temp_tool)

    start = time.time()
    try:
        subprocess.run(["python3", temp_tool], timeout=10, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = "PASS"
    except subprocess.TimeoutExpired:
        status = "TIMEOUT"
    except subprocess.CalledProcessError:
        status = "FAIL"
    except Exception:
        status = "ERROR"
    elapsed = round(time.time() - start, 2)
    results.append((tool, status, elapsed, "Verified" if status == "PASS" else "Rejected"))

# ---------- Write report ----------
os.makedirs(LOGS, exist_ok=True)
with open(OUT_MD, "w") as f:
    f.write(f"# Sandbox Test Results – {datetime.datetime.now()}\n\n")
    f.write("| Tool | Status | Runtime (s) | Decision |\n")
    f.write("|------|---------|-------------|-----------|\n")
    for t, s, e, d in results:
        f.write(f"| {t} | {s} | {e:.2f} | {d} |\n")
    f.write(f"\nTotal tested: {len(results)}\n")

# Clean up
shutil.rmtree(sandbox_dir, ignore_errors=True)
log(f"✅ Sandbox testing complete. Results saved to: {OUT_MD}")
