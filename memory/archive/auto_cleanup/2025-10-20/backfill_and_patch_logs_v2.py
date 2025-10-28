import os
import re
from datetime import datetime

BASE_DIR = "/home/rafa1215/consensus-project/memory/logs/system"
BRAINSTORM_DIR = os.path.join(BASE_DIR, "brainstorm")
OPTIMIZATION_DIR = os.path.join(BASE_DIR, "optimization")
SUGGESTIONS_DIR = os.path.join(BASE_DIR, "suggestions")

# Ensure directories exist
for d in [BRAINSTORM_DIR, OPTIMIZATION_DIR, SUGGESTIONS_DIR]:
    os.makedirs(d, exist_ok=True)

# Expanded keyword sets
KEYWORDS = {
    "brainstorm": [
        "brainstorm", "idea", "concept", "new task", "new duty",
        "extra duty", "creative", "think of", "future feature"
    ],
    "optimization": [
        "optimize", "optimization", "self-improve", "self improve",
        "improvement", "refactor", "streamline", "reduce", "efficiency",
        "auto-correct", "self correct", "self-correct"
    ],
    "suggestions": [
        "suggestion", "recommendation", "proposal", "enhancement",
        "improve project", "make better", "could add", "should add",
        "task idea", "upgrade", "extra duties"
    ]
}

def classify_text(text):
    """Classify a paragraph of text into brainstorm/optimization/suggestions if keywords hit."""
    low = text.lower()
    for category, words in KEYWORDS.items():
        for w in words:
            if w in low:
                return category
    return None

def backfill_logs():
    for root, _, files in os.walk(BASE_DIR):
        for f in files:
            if not (f.endswith(".log") or f.endswith(".md") or f.endswith(".txt")):
                continue
            path = os.path.join(root, f)
            if any(skip in path for skip in ["brainstorm", "optimization", "suggestions"]):
                continue

            try:
                with open(path, "r", errors="ignore") as infile:
                    content = infile.read()
            except Exception:
                continue

            # Split into paragraphs instead of lines
            paragraphs = re.split(r"\n\s*\n", content)
            for para in paragraphs:
                category = classify_text(para)
                if category:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = f"{category}_{f}_{ts}.md"
                    if category == "brainstorm":
                        outpath = os.path.join(BRAINSTORM_DIR, fname)
                    elif category == "optimization":
                        outpath = os.path.join(OPTIMIZATION_DIR, fname)
                    else:
                        outpath = os.path.join(SUGGESTIONS_DIR, fname)

                    with open(outpath, "a") as outfile:
                        outfile.write(f"[Extracted from {path}]\n\n{para.strip()}\n\n{'-'*40}\n")

def patch_logging_config():
    """Ensure routing config still points to correct folders."""
    config_path = os.path.join(BASE_DIR, "log_routing.conf")
    with open(config_path, "w") as cfg:
        cfg.write("# Auto-generated routing config (v2)\n")
        cfg.write(f"BRAINSTORM_DIR={BRAINSTORM_DIR}\n")
        cfg.write(f"OPTIMIZATION_DIR={OPTIMIZATION_DIR}\n")
        cfg.write(f"SUGGESTIONS_DIR={SUGGESTIONS_DIR}\n")

    print(f"[INFO] Log routing config updated at {config_path}")

if __name__ == "__main__":
    print("[INFO] Starting expanded backfill (v2)...")
    backfill_logs()
    print("[INFO] Expanded backfill complete.")
    patch_logging_config()
    print("[INFO] Agents will now log directly into the correct folders.")
