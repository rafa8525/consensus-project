cat > ~/consensus-project/tools/log_memory_manifest.py <<'PY'
#!/usr/bin/env python3
from pathlib import Path
import hashlib, datetime, json
root = Path.home()/ "consensus-project"/"memory"
manifest = {}
for p in root.rglob("*"):
    if p.is_file():
        manifest[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
out = root/"logs"/"system"/f"manifest_{datetime.date.today()}.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(manifest, indent=2))
print("✅ Memory manifest logged", out)
PY
chmod +x ~/consensus-project/tools/log_memory_manifest.py
