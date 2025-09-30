import os
import re
import shutil
from datetime import datetime

BASE_DIR = "/home/rafa1215/consensus-project/memory/logs/system"
BRAINSTORM_DIR = os.path.join(BASE_DIR, "brainstorm")
OPTIMIZATION_DIR = os.path.join(BASE_DIR, "optimization")
SUGGESTIONS_DIR = os.path.join(BASE_DIR, "suggestions")

# Ensure target directories exist
for d in [BRAINSTORM_DIR, OPTIMIZATION_DIR, SUGGESTIONS_DIR]:
    os.makedirs(d, exist_ok=True)

# Keywords for classification
KEYWORDS = {
    "brainstorm": ["brainstorm", "idea"],
    "optimization": ["optimize", "optimization", "self-improve", "improvement"],
    "suggestions": ["suggestion", "recommendation", "proposal"]
}

def classify_line(line):
    l = line.lower()
    for category, words in KEYWORDS.items():
        for w in words:
            if w in l:
                return category
    return None

def backfill_logs():
    for root, _, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith(".log") or f.endswith(".md") or f.endswith(".txt"):
                path = os.path.join(root, f)
                if any(skip in path for skip in ["brainstorm", "optimization", "suggestions"]):
                    continue  # skip already-classified dirs

                with open(path, "r", errors="ignore") as infile:
                    for line in infile:
                        category = classify_line(line)
                        if category:
                            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                            fname = f"{category}_{ts}.md"
                            if category == "brainstorm":
                                outpath = os.path.join(BRAINSTORM_DIR, fname)
                            elif category == "optimization":
                                outpath = os.path.join(OPTIMIZATION_DIR, fname)
                            else:
                                outpath = os.path.join(SUGGESTIONS_DIR, fname)
                            with open(outpath, "a") as outfile:
                                outfile.write(f"[From {path}]\n{line}\n")

def patch_logging_config():
    """Redirect new agent logs into correct folders by patching environment variables."""
    config_path = os.path.join(BASE_DIR, "log_routing.conf")
    with open(config_path, "w") as cfg:
        cfg.write("# Auto-generated routing config\n")
        cfg.write(f"BRAINSTORM_DIR={BRAINSTORM_DIR}\n")
        cfg.write(f"OPTIMIZATION_DIR={OPTIMIZATION_DIR}\n")
        cfg.write(f"SUGGESTIONS_DIR={SUGGESTIONS_DIR}\n")

    print(f"[INFO] Log routing config updated at {config_path}")

if __name__ == "__main__":
    print("[INFO] Starting backfill...")
    backfill_logs()
    print("[INFO] Backfill complete.")
    patch_logging_config()
    print("[INFO] Agents will now log directly into the correct folders.")
