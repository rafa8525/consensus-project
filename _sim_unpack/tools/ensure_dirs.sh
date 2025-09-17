#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-.}"
mkdir -p "$ROOT"/logs/security/vpn_tests "$ROOT"/logs/absorb "$ROOT"/logs/reports \
         "$ROOT"/logs/project "$ROOT"/logs/fitness "$ROOT"/logs/ckb \
         "$ROOT"/memory/logs/repair "$ROOT"/config "$ROOT"/csv
touch "$ROOT"/logs/absorb/.gitkeep "$ROOT"/logs/reports/.gitkeep "$ROOT"/logs/project/.gitkeep
echo "[ensure_dirs] ensured folders"
if [ ! -f "$ROOT/config/absorb_cmd.txt" ]; then
  echo 'echo "Absorb placeholder ran"' > "$ROOT/config/absorb_cmd.txt"
  echo "[ensure_dirs] seeded config/absorb_cmd.txt placeholder"
fi
