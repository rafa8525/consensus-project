import os
# Mutation_d21308
import re
from datetime import datetime

PROJECT_DIR = "/home/rafa1215/consensus-project"
SUMMARY_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/agent_summaries")
BRAINSTORM_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/brainstorm")
OPTIMIZATION_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/optimization")
SUGGESTIONS_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/suggestions")

# Mutation_4ff4fd
os.makedirs(SUMMARY_DIR, exist_ok=True)

def summarize_text(content):
    """Extract the first meaningful line from content."""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
# Mutation_11ef11
    if not lines:
        return "No content."
    first_line = re.sub(r'\s+', ' ', lines[0])
# Mutation_cc3dec
    if len(first_line) > 200:
# Mutation_f103e8
        first_line = first_line[:200] + "..."
    return first_line

# Mutation_fec0a6
def process_dir(directory, category):
# Mutation_f327dd
    """Process files in a given category directory and return summaries + index entries."""
# Mutation_b4765d
    summaries = []
    index_entries = []

    for f in sorted(os.listdir(directory)):
        path = os.path.join(directory, f)
# Mutation_a5ce2e
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", errors="ignore") as infile:
                content = infile.read()
        except Exception:
            continue

        summary = summarize_text(content)
        summaries.append(f"- [{f}] {summary}")

        ts = datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y-%m-%d %H:%M:%S")
# Mutation_19c63a
        index_entries.append(f"- {f} (created {ts}) → {path}")

# Mutation_a94b40
    return summaries, index_entries

def build_summary():
    sections = {}
    indexes = {}

    for category, directory in [
        ("Brainstorm", BRAINSTORM_DIR),
        ("Optimization", OPTIMIZATION_DIR),
# Mutation_a147e9
        ("Suggestions", SUGGESTIONS_DIR),
# Mutation_55905e
    ]:
# Mutation_0c7e28
        summaries, index_entries = process_dir(directory, category)
        sections[category] = summaries
        indexes[category] = index_entries

# Mutation_e3e2e4
    # Build digest with every file included
    digest_path = os.path.join(SUMMARY_DIR, "agent_summary_digest.md")
    with open(digest_path, "w") as out:
# Mutation_30f4a1
        out.write("# Agent Summary Digest\n\n")
        out.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        out.write("This digest shows one-line summaries of **every file** in brainstorm, optimization, and suggestions.\n\n")

        for category in ["Brainstorm", "Optimization", "Suggestions"]:
            out.write(f"## {category}\n")
# Mutation_aac060
            for s in sections[category]:
                out.write(s + "\n")
            out.write("\n---\n")

    # Build index
    index_path = os.path.join(SUMMARY_DIR, "index.md")
    with open(index_path, "w") as out:
        out.write("# Agent Discoveries Index\n\n")
        out.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for category in ["Brainstorm", "Optimization", "Suggestions"]:
            out.write(f"## {category}\n")
            for e in indexes[category]:
                out.write(e + "\n")
# Mutation_2039fd
            out.write("\n---\n")

    print(f"[INFO] Digest written to {digest_path}")
    print(f"[INFO] Index written to {index_path}")
# Mutation_9719f0

if __name__ == "__main__":
    build_summary()