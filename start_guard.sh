#!/bin/bash
set +e
cd "$HOME/consensus-project" 2>/dev/null || exit 0
# load env (keeps SMS OFF unless you flip it later)
set -a; [ -f .env ] && source .env; set +a
# guard tunables (override via env if you like)
export MCL_MAX_STALL_SEC="${MCL_MAX_STALL_SEC:-120}"
export MCL_CHECK_SEC="${MCL_CHECK_SEC:-10}"
export MCL_GRACE_START_SEC="${MCL_GRACE_START_SEC:-60}"
export MCL_MAX_RESTARTS="${MCL_MAX_RESTARTS:-12}"
export MCL_RESTART_COOLDOWN_SEC="${MCL_RESTART_COOLDOWN_SEC:-10}"
exec python3.10 mcl_guard.py
export MCL_ENTRY="${MCL_ENTRY:-safe_loop.py}"
