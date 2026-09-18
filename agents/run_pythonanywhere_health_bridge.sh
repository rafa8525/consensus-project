#!/usr/bin/env bash
set -euo pipefail

# Safe launcher for PythonAnywhere health monitoring.
# Never merges or rebases the live branch.
# Always executes the current bridge from origin/main in a temporary file.

REPO="$HOME/consensus-project"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

cd "$REPO"

git fetch --quiet origin main

git show origin/main:agents/pythonanywhere_health_bridge.py > "$TMP"

python3 "$TMP"
