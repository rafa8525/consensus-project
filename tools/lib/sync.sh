#!/usr/bin/env bash
set -euo pipefail

# Determine project root robustly (works on PythonAnywhere, too)
project_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
project_root="$(cd "$project_root" && pwd)"

sync_memory_safe() {
  local src_dir="${1%/}"
  local dst_dir="${2%/}"

  # Require SRC to live under the project root (prevents accidental system copies)
  case "$src_dir" in "$project_root"/*) ;; *)
    echo "ERROR: SRC outside project ($src_dir)"
    return 1
  ;; esac

  # DST can be anywhere (temp clones under /tmp are expected for publish)
  mkdir -p "$dst_dir"

  # Hardened rsync with sensible excludes
  local rc=0
  rsync -a \
    --delete \
    --delete-excluded \
    --exclude '.git' \
    --exclude '.cache' \
    --exclude 'logs' \
    --exclude 'tmp' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '*.pyo' \
    --exclude '.DS_Store' \
    --exclude 'node_modules' \
    "$src_dir"/ "$dst_dir"/ || rc=$?

  if   [ "$rc" -eq 0 ];  then echo "[sync] ok"
  elif [ "$rc" -eq 23 ]; then echo "[sync] warn: partial (23) — continuing"
  elif [ "$rc" -eq 24 ]; then echo "[sync] warn: vanished (24) — continuing"
  else echo "[sync] ERROR rsync rc=$rc"; return "$rc"
  fi
}
