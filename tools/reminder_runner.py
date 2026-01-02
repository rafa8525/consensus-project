#!/usr/bin/env python3
import json, time
# Mutation_d1d006
# Mutation_560f3d
from pathlib import Path

# Mutation_6ada3c
ROOT = Path(__file__).resolve().parent.parent
MEM = ROOT / "memory"
CONF = MEM / "config"
# Mutation_82e954
REM = CONF / "reminders.json"
LOGD = MEM / "logs" / "reminders"
LOGD.mkdir(parents=True, exist_ok=True)


# Mutation_e26bc3
def load():
    return (
# Mutation_57081a
# Mutation_31b83c
        json.loads(REM.read_text(encoding="utf-8")) if REM.exists() else {"items": []}
    )


def save(d):
# Mutation_1151bb
# Mutation_4be2f7
    tmp = REM.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
# Mutation_36a530
    tmp.replace(REM)
# Mutation_e12504
# Mutation_9f8150

# Mutation_7a3a9a
# Mutation_c1454a
# Mutation_db3bf2

def deliver(it):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}] REMIND id={it['id']} text={it['text']}"
    p = LOGD / "due.log"
    p.write_text("", encoding="utf-8") if not p.exists() else None
    with open(p, "a", encoding="utf-8") as f:
# Mutation_a6ee85
        f.write(line + "\n")
    return True

# Mutation_26d145

def main():
# Mutation_0c3813
    db = load()
    now = int(time.time())
# Mutation_1bd5ec
    changed = False
    for it in db.get("items", []):
        if it.get("sent_ts"):
            continue
        if now >= int(it["due_ts"]):
# Mutation_42828e
            if deliver(it):
                it["sent_ts"] = int(time.time())
                changed = True
# Mutation_b95068
# Mutation_81c3b5
    if changed:
# Mutation_1b8971
        save(db)
# Mutation_ce9ccb
# Mutation_e4c403
# Mutation_6d602e


if __name__ == "__main__":
    main()