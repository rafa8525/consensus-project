import os
import re
from datetime import datetime

PROJECT_DIR = "/home/rafa1215/consensus-project"
SUMMARY_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/agent_summaries")
BRAINSTORM_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/brainstorm")
OPTIMIZATION_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/optimization")
SUGGESTIONS_DIR = os.path.join(PROJECT_DIR, "memory/logs/system/suggestions")

os.makedirs(SUMMARY_DIR, exist_ok=True)

def summarize_text(content):
    """Extract the first meaningful line from content."""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return "No content."
    first_line = re.sub(r'\s+', ' ', lines[0])
    if len(first_line) > 200:
        first_line = first_line[:200] + "..."
    return first_line

def process_dir(directory, category):
    """Process files in a given category directory and return summaries + index entries."""
    summaries = []
    index_entries = []

    for f in sorted(os.listdir(directory)):
        path = os.path.join(directory, f)
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
        index_entries.append(f"- {f} (created {ts}) → {path}")

    return summaries, index_entries

def build_summary():
    sections = {}
    indexes = {}

    for category, directory in [
        ("Brainstorm", BRAINSTORM_DIR),
        ("Optimization", OPTIMIZATION_DIR),
        ("Suggestions", SUGGESTIONS_DIR),
    ]:
        summaries, index_entries = process_dir(directory, category)
        sections[category] = summaries
        indexes[category] = index_entries

    # Build digest with every file included
    digest_path = os.path.join(SUMMARY_DIR, "agent_summary_digest.md")
    with open(digest_path, "w") as out:
        out.write("# Agent Summary Digest\n\n")
        out.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        out.write("This digest shows one-line summaries of **every file** in brainstorm, optimization, and suggestions.\n\n")

        for category in ["Brainstorm", "Optimization", "Suggestions"]:
            out.write(f"## {category}\n")
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
            out.write("\n---\n")

    print(f"[INFO] Digest written to {digest_path}")
    print(f"[INFO] Index written to {index_path}")

if __name__ == "__main__":
    build_summary()
