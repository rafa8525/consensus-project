cat > ~/consensus-project/tools/verify_kb_permissions.py <<'PY'
#!/usr/bin/env python3
from pathlib import Path
import os, sys, json, datetime
KB = Path.home()/"consensus-project"/"memory"/"knowledge"
LOG = Path.home()/"consensus-project"/"memory"/"logs"/"system"/"kb_check.log"
KB.mkdir(parents=True, exist_ok=True)
result = {"timestamp": datetime.datetime.now().isoformat(), "exists": KB.exists(), "read": os.access(KB, os.R_OK), "write": os.access(KB, os.W_OK)}
LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text(json.dumps(result, indent=2))
print("✅ Knowledge-base permissions verified:", result)
PY
chmod +x ~/consensus-project/tools/verify_kb_permissions.py
