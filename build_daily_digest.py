import os
import datetime

log_dir = "logs"
digest_path = os.path.join(log_dir, f"daily_digest_{datetime.date.today()}.txt")
os.makedirs(log_dir, exist_ok=True)

digest_lines = []

for fname in os.listdir(log_dir):
    if fname.endswith(".txt"):
        with open(os.path.join(log_dir, fname), "r", encoding="utf-8") as f:
            for line in f:
                if any(keyword in line for keyword in ["GOAL:", "AGENT:", "ERROR:"]):
                    digest_lines.append(f"{fname} ➜ {line.strip()}")

with open(digest_path, "w", encoding="utf-8") as f:
    f.write("🧠 Daily Digest Summary\n\n")
    f.write("\n".join(digest_lines))

print(f"✅ Daily digest generated: {digest_path}")
