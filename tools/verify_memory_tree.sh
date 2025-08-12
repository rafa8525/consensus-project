#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin >/dev/null
remote=$(git ls-tree -r --name-only origin/v1.1-dev:memory | wc -l)
local=$(find memory -type f -not -path '*/.git/*' | wc -l)
echo "remote=$remote local=$local"
test "$local" -ge 1 && test "$local" -ge "$remote"
