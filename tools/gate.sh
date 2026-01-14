#!/usr/bin/env bash
set -o pipefail
fail() { echo "ERROR: $*" >&2; return 1; }

# gate "<label>" <command...>
gate() {
  local label="$1"; shift
  echo "=== $label ==="
  "$@"
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo "FAIL ($rc): $label" >&2
    return $rc
  fi
  echo "OK: $label"
  return 0
}
