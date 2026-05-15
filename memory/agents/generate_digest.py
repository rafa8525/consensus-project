# agents/generate_digest.py

import os
from datetime import datetime

def generate_daily_digest(memory_dir="memory", logs_dir="logs"):
    today = datetime.now().strftime("%Y-%m-%d")
    digest_filename = f"daily_digest_{today}.txt"
    digest_path = os.path.join(logs_dir, digest_filename)
    preview_path = os.path.join(logs_dir, "daily_digest.txt")

    digest = [f"🧠 AI Consensus Digest - {today}", "=" * 40]
    count = 0

    for fname in sorted(os.listdir(memory_dir), reverse=True):
        if fname.endswith(".txt"):
            with open(os.path.join(memory_dir, fname), "r", encoding="utf-8") as f:
                content = f.read()
                digest.append(f"\n--- {fname} ---\n{content}")
                count += 1
            if count >= 3:
                break

    final_text = "\n".join(digest)

    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"✅ Digest archived to: {digest_path}")
    print("🧠 Dashboard preview updated.")

if __name__ == "__main__":
    generate_daily_digest()
