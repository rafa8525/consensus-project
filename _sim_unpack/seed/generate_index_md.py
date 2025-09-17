
import os

SEED_DIR = "seed"
INDEX_FILE = os.path.join(SEED_DIR, "index.md")

def generate_index():
    files = sorted(f for f in os.listdir(SEED_DIR) if f.endswith(".txt") or f.endswith(".md"))

    with open(INDEX_FILE, "w") as index:
        index.write("# 🧠 AI Consensus Project – Seed Directory Index\n\n")
        index.write("This folder contains foundational modules, logs, and system features for the AI Consensus System.\n\n")
        index.write("## 📁 File Reference\n\n")
        index.write("| File Name | Description |
")
        index.write("|-----------|-------------|
")

        for filename in files:
            if filename == "index.md":
                continue  # skip self
            name_display = filename.replace("_", " ").replace(".txt", "").replace(".md", "")
            link = f"[{filename}](./{filename})"
            index.write(f"| {link} | _To be described_ |
")

        index.write("\n---\n")
        index.write("📌 Regenerate this file with `python generate_index_md.py` to keep it up to date.\n")

if __name__ == "__main__":
    generate_index()
