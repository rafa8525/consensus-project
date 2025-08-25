import re

_RULES = [
  (r'bash\\r', "CRLF endings found. Enforce LF via .gitattributes + guard; resave scripts with LF."),
  (r'requested url returned error:\s*400|clone failed', "Remote URL/PAT invalid. Use fine-grained PAT with Contents:read/write and correct HTTPS remote."),
  (r'loose object .* corrupt|reflog.*segmentation fault|data stream error', "Local .git DB is corrupt. Do clean-swap: fresh clone → rsync working tree (exclude .git) → atomic swap."),
  (r'rsync warning: some files vanished', "Benign during checkout churn. Exclude .git and ignore rsync code 23/24."),
  (r'adding embedded git repository|submodule', "Don’t keep a repo under memory/. Move working clone to .cache; .gitignore it."),
  (r'no such file or directory.*ensure_dirs\.sh', "Create tools/ensure_dirs.sh and run it before dispatch."),
  (r'should have been pointers', "Git LFS issue. `git lfs install`, track patterns, re-commit/push properly."),
]

def recommend(err_line: str) -> str:
    e = err_line.lower()
    for pat, msg in _RULES:
        if re.search(pat, e):
            return msg
    return "Investigate; capture full context. Verify remote, PAT scopes, and local repo integrity."
