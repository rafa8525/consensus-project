#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/rafa1215/consensus-project"
ARCHIVE_DIR="$ROOT/archive/vpn-test-plans"
mkdir -p "$ARCHIVE_DIR"

# Candidate duplicates we’ve seen around the repo
CANDIDATES=(
  "$ROOT/seed/vpn_activation_testing_plan.txt"
  "$ROOT/seed/VPNActivationTestingPlan.txt"
  "$ROOT/seed/VPN_activation_testing.txt"
  "$ROOT/seed/VPNActivationTestingPlan.md"
  "$ROOT/seed/VPN_activation_testing.md"
  "$ROOT/tools/vpn_activation_testing_plan.txt"
  "$ROOT/tools/VPNActivationTestingPlan.txt"
  "$ROOT/tools/VPN_activation_testing.txt"
)

moved_any=false
timestamp="$(date -Is)"
log_file="$ARCHIVE_DIR/archive_index.md"

# Ensure index header exists
if [[ ! -f "$log_file" ]]; then
  cat > "$log_file" <<'EOF'
# Archived VPN Test Plans

This folder contains superseded/duplicate VPN test plan documents.
The canonical/active plan remains in the main code/docs. These files are kept
for reference only.

| Archived File | Original Path | Archived At |
|---|---|---|
EOF
fi

for path in "${CANDIDATES[@]}"; do
  if [[ -f "$path" ]]; then
    base="$(basename "$path")"
    dest="$ARCHIVE_DIR/$base"
    # If already archived, skip moving but still log presence
    if [[ ! -f "$dest" ]]; then
      mv "$path" "$dest"
      moved_any=true
      echo "| \`$base\` | \`$path\` | $timestamp |" >> "$log_file"
    fi
  fi
done

# Create a pointer README if we moved anything
if $moved_any; then
  # Write an archive pointer at repo root for discoverability
  POINTER="$ROOT/archive/README.md"
  if ! grep -q "vpn-test-plans" "$POINTER" 2>/dev/null; then
    {
      echo "# Archive Index"
      echo ""
      echo "- See [vpn-test-plans](./vpn-test-plans/) for superseded VPN test plans."
    } > "$POINTER"
  fi
  echo "[OK] Archived duplicate VPN test plans to $ARCHIVE_DIR"
else
  echo "[OK] No duplicate VPN test plan files found. Nothing to do."
fi
