#!/usr/bin/env bash
set -euo pipefail
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
REPO="${1:-$HOME/consensus-project}"; SECD="$HOME/.secrets/google"
cd "$REPO"; pass=0; fail=0; warn=0; p(){ echo -e "$@"; }

set +H 2>/dev/null || true

printf "[1] Secrets dir perms... "
if [ -d "$SECD" ]; then
  perm=$(stat -c '%a' "$SECD" 2>/dev/null || stat -f '%A' "$SECD" 2>/dev/null)
  case "$perm" in 700|7??) p "${GREEN}PASS${NC} ($perm)"; ((pass++));; *) p "${YELLOW}WARN${NC} ($perm)"; ((warn++));; esac
else p "${RED}FAIL${NC} (missing)"; ((fail++)); fi

printf "[2] Working tree secret scan... "
git grep -I -nE '(client_secret|private_key|-----BEGIN PRIVATE KEY-----|refresh_token)' -- ':!*.md' >/dev/null \
  && { p "${RED}FAIL${NC} (hits found)"; ((fail++)); } || { p "${GREEN}PASS${NC}"; ((pass++)); }

printf "[3] History scan (known files)... "
remain=0
for f in credentials.json memory/core/secrets/gmail_credentials.json memory/core/secrets/token_gmail.json _sim_unpack/credentials.json _sim_unpack/client_secrets.json _sim_unpack/token.json 'reminder agent/credentials.json' memory/archive/auto_cleanup/2025-10-20/client_secrets.json memory/archive/auto_cleanup/2025-10-20/credentials.json; do
  git log --all --full-history -- "$f" >/dev/null 2>&1 && git log --all --full-history -- "$f" | grep -q '^commit' && remain=$((remain+1)) || true
done
[ $remain -eq 0 ] && { p "${GREEN}PASS${NC}"; ((pass++)); } || { p "${RED}FAIL${NC} ($remain remain)"; ((fail++)); }

printf "[4] .gitignore exceptions... "
(grep -q 'memory/logs/\*\*' .gitignore && grep -q '!memory/logs/' .gitignore && grep -q '!memory/logs/system/' .gitignore && grep -q '!memory/logs/reports/' .gitignore && grep -q '!memory/logs/status/' .gitignore) \
  && { p "${GREEN}PASS${NC}"; ((pass++)); } || { p "${YELLOW}WARN${NC}"; ((warn++)); }

printf "[5] creds path normalization... "
bad=$(git grep -nI '"credentials\.json"' -- '*.py' | grep -v '/home/rafa1215/.secrets/google/' | wc -l)
bad2=$(git grep -nI 'token_gmail\.json' -- '*.py' | grep -v '/home/rafa1215/.secrets/google/token_gmail.json' | wc -l)
[ "$bad" -eq 0 ] && [ "$bad2" -eq 0 ] && { p "${GREEN}PASS${NC}"; ((pass++)); } || { p "${YELLOW}WARN${NC} ($((bad+bad2)) refs)"; ((warn++)); }

printf "[6] Remote origin present... "
git remote get-url origin >/dev/null 2>&1 && { p "${GREEN}PASS${NC}"; ((pass++)); } || { p "${RED}FAIL${NC}"; ((fail++)); }

printf "[7] Console hardening present... "
( grep -q 'export PAGER=cat' ~/.bashrc && declare -F runq >/dev/null ) \
  && { p "${GREEN}PASS${NC}"; ((pass++)); } || { p "${YELLOW}WARN${NC}"; ((warn++)); }

echo; p "Result: ${GREEN}PASS=$pass${NC}, ${YELLOW}WARN=$warn${NC}, ${RED}FAIL=$fail${NC}"
[ $fail -eq 0 ] || exit 1
[ $warn -eq 0 ] || exit 2
