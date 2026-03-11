#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/rafa1215/consensus-project"
CANONICAL_ROOT="/home/rafa1215/memory"
BRANCH="v1.1-dev"

cd "$REPO_ROOT"

mkdir -p \
  "$REPO_ROOT/memory/logs/system/predictions" \
  "$REPO_ROOT/memory/logs/status" \
  "$REPO_ROOT/memory/exports"

echo "Mirroring proven live-write targets into repo..."
rsync -a "$CANONICAL_ROOT/logs/system/predictions/" "$REPO_ROOT/memory/logs/system/predictions/"
rsync -a "$CANONICAL_ROOT/logs/status/" "$REPO_ROOT/memory/logs/status/"
rsync -a "$CANONICAL_ROOT/exports/" "$REPO_ROOT/memory/exports/"

echo
echo "Running audit..."
python3 "$REPO_ROOT/tools/repo_write_audit.py" || true

echo
echo "Staging only proven live-write targets..."
git add \
  memory/logs/system/predictions \
  memory/logs/status \
  memory/exports \
  tools/repo_write_audit.py \
  tools/fix_repo_write_pipeline.sh

if git diff --cached --quiet; then
  echo "No staged changes to commit."
  exit 0
fi

MSG="Repair repo mirror for proven live-write targets ($(date +%F\ %T))"
git commit -m "$MSG"

echo
echo "Pushing..."
git -c http.version=HTTP/1.1 push origin "$BRANCH"

echo
echo "Done."
