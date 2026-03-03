# Repair Log — 2026-03-03 — Prediction Feed Quick Actions + Runner Scheduling

## Summary (What is now working)
- prediction_feed_agent.py runs and writes:
  - canonical: /home/rafa1215/memory/logs/system/predictions/prediction_feed_YYYY-MM-DD.md
  - repo mirror: /home/rafa1215/consensus-project/memory/logs/system/predictions/prediction_feed_YYYY-MM-DD.md
- Quick Actions block is appended (idempotent) to both canonical + mirror:
  - tools/append_prediction_quick_actions.py
- Quick logging works (canonical write + repo mirror):
  - tools/quick_log.py
  - writes:
    - /home/rafa1215/memory/logs/fitness/daily_YYYY-MM-DD.md
    - /home/rafa1215/memory/logs/system/predictions/candidates_YYYY-MM-DD.md
- Unified daily runner works:
  - tools/run_feed_plus_marker.sh runs:
    1) prediction feed
    2) append quick actions
    3) write_absorption_public_marker.py
    4) audit log line -> /home/rafa1215/memory/logs/system/exec/run_feed_plus_marker.log
- PythonAnywhere-compatible scheduled command verified:
  - bash -lc '... source .env ... bash tools/run_feed_plus_marker.sh'

## Root causes we hit today (Why “already-fixed” stuff broke again)
1) Copy/paste contamination:
   - `.py` files were accidentally overwritten with bash heredoc lines.
   - Fix: recreate scripts via heredoc + verify `python3 -m py_compile`.
2) Env wrapper mismatch:
   - run_with_env.sh is python-only; passing `bash script.sh` caused failures.
   - Fix: scheduled jobs should use `bash -lc ...` or enhance run_with_env.sh.
3) Git push instability:
   - HTTPS push returned GitHub 500 at first; later succeeded after forcing HTTP/1.1.
4) Repo drift + symlink stash/add failure:
   - Git refused stash/add under memory/ with "beyond a symbolic link".
   - Fix: keep long-term docs/logs OUTSIDE the symlinked memory tree (use docs/).

## Known-good commands
bash -lc 'set -euo pipefail; cd /home/rafa1215/consensus-project; source /home/rafa1215/consensus-project/.env 2>/dev/null || true; bash /home/rafa1215/consensus-project/tools/run_feed_plus_marker.sh'
