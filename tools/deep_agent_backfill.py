import os
import shutil
from datetime import datetime

PROJECT_DIR = "/home/rafa1215/consensus-project"
BRAINSTORM_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/brainstorm")
OPTIMIZATION_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/optimization")
SUGGESTIONS_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/suggestions")

for d in [BRAINSTORM_DIR, OPTIMIZATION_DIR, SUGGESTIONS_DIR]:
    os.makedirs(d, exist_ok=True)

# Filename patterns that imply category
FILENAME_HINTS = {
    "brainstorm": ["knowledge_shared", "simulations", "ideas", "concepts"],
    "optimization": ["self_improvement", "refactor", "optimize"],
    "suggestions": ["lessons_learned", "proposals", "recommendations"]
}

# Keyword patterns inside files
CONTENT_HINTS = {
    "brainstorm": ["brainstorm", "idea", "concept", "simulation", "future feature"],
    "optimization": ["optimize", "self-improve", "refactor", "streamline", "efficiency"],
    "suggestions": ["suggestion", "recommendation", "proposal", "enhancement"]
}

def classify_file(fname, content):
    low = fname.lower()
    for category, hints in FILENAME_HINTS.items():
        if any(h in low for h in hints):
            return category

    lowc = content.lower()
    for category, hints in CONTENT_HINTS.items():
        if any(h in lowc for h in hints):
            return category
    return None

def deep_scan_and_copy():
    results = {"brainstorm": 0, "optimization": 0, "suggestions": 0}

    for root, _, files in os.walk(PROJECT_DIR):
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

            category = classify_file(f, content)
            if category:
                ts = datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y%m%d_%H%M%S")
                dest_dir = (
                    BRAINSTORM_DIR if category == "brainstorm"
                    else OPTIMIZATION_DIR if category == "optimization"
                    else SUGGESTIONS_DIR
                )
                dest_path = os.path.join(dest_dir, f"{category}_{f}_{ts}.md")
                shutil.copy2(path, dest_path)
                results[category] += 1

    return results

if __name__ == "__main__":
    print("[INFO] Starting deep recursive scan across entire project...")
    results = deep_scan_and_copy()
    print(f"[INFO] Files copied: {results}")
    print("[INFO] Check brainstorm/, optimization/, suggestions/ for results.")
