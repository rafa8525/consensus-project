#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

. tools/lib/sync.sh

CACHE_DIR="$ROOT/.cache/github_memory_repo"
URL="$(cat config/GITHUB_MEMORY_REPO_URL.txt)"

export GIT_TERMINAL_PROMPT=0

mkdir -p "$CACHE_DIR"
if [ ! -d "$CACHE_DIR/.git" ]; then
  git clone --quiet "$URL" "$CACHE_DIR"
else
  git -C "$CACHE_DIR" fetch --quiet --all --prune
  # Detect default branch of the remote
  DEFBR="$(git -C "$CACHE_DIR" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || echo origin/main)"
  DEFBR="${DEFBR#origin/}"
  git -C "$CACHE_DIR" reset --hard "origin/$DEFBR" --quiet
fi

# Pull only the memory subtree into our working tree
mkdir -p "$ROOT/memory"
sync_memory_safe "$CACHE_DIR/memory" "$ROOT/memory"
