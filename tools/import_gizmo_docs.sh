#!/usr/bin/env bash
set -euo pipefail
SRC_DIR="docs/inbox"
DEST_DIR="docs/knowledge"

mkdir -p "$SRC_DIR" "$DEST_DIR"

# Copy *.txt from inbox, normalize names
copied=()
shopt -s nullglob
for src in "$SRC_DIR"/*.txt; do
  base="$(basename "$src")"
  clean="$(printf '%s' "$base" | tr ' ' '_' | tr -d '()')"
  if [[ ! -f "$DEST_DIR/$clean" ]] || ! cmp -s "$src" "$DEST_DIR/$clean"; then
    cp -f -- "$src" "$DEST_DIR/$clean"
    copied+=("$clean")
  fi
done
shopt -u nullglob

# Build/refresh README
readme="$DEST_DIR/README.md"
{
  echo "# Knowledge Base (Gizmo imports)"
  echo
  echo "_Auto-generated index for imported planning/support docs._"
  echo
  if ((${#copied[@]}==0)) && [[ -z "$(ls -1 "$DEST_DIR"/*.txt 2>/dev/null || true)" ]]; then
    echo "> No files in $SRC_DIR. Nothing to import yet."
  else
    echo "## Files"
    echo
    # List all .txt currently in knowledge, sorted
    for f in $(ls -1 "$DEST_DIR"/*.txt 2>/dev/null | sort); do
      bn="$(basename "$f")"
      # tiny blurbs by pattern (optional)
      case "$bn" in
        *vpn*|*VPN*) blurb="VPN activation/testing";;
        *fitness*|*health*) blurb="Fitness tracking plans";;
        *knowledge*|*status*|*next_steps*|*reminder*|*security_audit*) blurb="Project ops & KB";;
        *) blurb="Imported note";;
      esac
      echo "- \`$bn\` — $blurb"
    done
  fi
} > "$readme"

# Commit only if there are actual changes
if ! git diff --quiet || ! git diff --cached --quiet; then
  git add "$DEST_DIR"
  git commit -m "docs(knowledge): import/update Gizmo planning docs and index"
  git push origin HEAD
  echo "✅ Imported/updated and pushed."
else
  echo "ℹ️ Nothing new to import; no commit."
fi
