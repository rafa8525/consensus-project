#!/usr/bin/env python3
import os, sys
from pathlib import Path

PROJECT_DIR = os.environ.get("PROJECT_DIR", str(Path.home() / "consensus-project"))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from mcl_v2.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
