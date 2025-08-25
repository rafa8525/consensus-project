import os

def load_errors(path):
    if not os.path.exists(path):
        return []
    lines = [l.strip() for l in open(path, encoding="utf-8", errors="ignore")]
    return [l for l in lines if l and "no_errors_detected" not in l]
