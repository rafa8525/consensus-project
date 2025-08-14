cd /home/rafa1215/consensus-project

# 1) Normalizer for fitness logs (safe, idempotent)
cat > tools/fitness_normalize.py <<'PY'
#!/usr/bin/env python3
import re, sys
from datetime import date
from pathlib import Path

BASE   = Path.home() / "consensus-project"
FITDIR = BASE / "memory" / "logs" / "fitness"
FITDIR.mkdir(parents=True, exist_ok=True)

FNAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.md$")

def header_for(day: str) -> str:
    return f"# Fitness — {day}\n"

def normalize_file(p: Path) -> bool:
    m = FNAME_RE.match(p.name)
    if not m:
        return False
    day = "-".join(m.groups())
    orig = p.read_text(encoding="utf-8")
    lines = orig.splitlines()
    changed = False

    # Ensure header
    want_header = header_for(day).rstrip("\n")
    if not lines:
        lines = [want_header, f"- ts: {date.today().isoformat()}T00:00:00Z", "- steps: 0", "- workouts: []", '- notes: ""']
        changed = True
    else:
        if not lines[0].startswith("# Fitness —"):
            lines.insert(0, want_header)
            changed = True
        elif lines[0] != want_header:
            lines[0] = want_header
            changed = True

    # Normalize whitespace and ensure at least one "- ts:" entry
    seen_ts = any(re.match(r"^\s*-\s*ts:\s*", ln) for ln in lines)
    new = []
    for ln in lines:
        s = ln.rstrip().replace("\t", "  ")
        if s != ln:
            changed = True
        new.append(s)
    lines = new

    if not seen_ts:
        lines += [f"- ts: {date.today().isoformat()}T00:00:00Z", "- steps: 0", "- workouts: []", '- notes: ""']
        changed = True

    out = "\n".join(lines).rstrip() + "\n"
    if changed and out != orig:
        p.write_text(out, encoding="utf-8")
    return changed

def main():
    changed = 0
    for p in sorted(FITDIR.iterdir()):
        if p.is_file() and FNAME_RE.match(p.name):
            if normalize_file(p):
                changed += 1
    print(f"fitness_normalize: changed={changed}")

if __name__ == "__main__":
    main()
PY
chmod +x tools/fitness_normalize.py

# 2) Run it (idempotent)
python3 tools/fitness_normalize.py

# 3) Pre-commit guard: ensure today's fitness file exists and has a ts entry
cat > .git/hooks/pre-commit <<'SH'
#!/usr/bin/env bash
set -e
d=$(date +%F)
f="memory/logs/fitness/${d}.md"
if [ ! -f "$f" ]; then
  echo "# Fitness — ${d}" > "$f"
  printf -- "- ts: %s\n- steps: 0\n- workouts: []\n- notes: \"\"\n" "$(date -u +%FT%TZ)" >> "$f"
  git add "$f"
fi
if ! grep -qE '^\s*-\s*ts:\s' "$f"; then
  echo "ERROR: fitness log $f missing '- ts:' entry" >&2
  exit 1
fi
exit 0
SH
chmod +x .git/hooks/pre-commit

# 4) Commit any normalized files + tool
git add tools/fitness_normalize.py memory/logs/fitness/*.md
git commit -m "Fitness: normalize per-day files; add pre-commit guard to ensure daily entry"
git push origin v1.1-dev
