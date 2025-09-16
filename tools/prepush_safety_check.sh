#!/bin/bash
set -euo pipefail
echo "🔍 Running safety pre-push checks..."

# 1. Verify .gitignore is present and has runtime rules
if ! grep -q "memory/logs" .gitignore; then
  echo "⚠️ .gitignore may be missing runtime rules!"
  exit 1
fi

# 2. Make sure no sensitive files are staged
if git diff --cached --name-only | grep -E "github_sync_log|memory/logs"; then
  echo "❌ Sensitive/runtime files staged — aborting push"
  exit 1
fi

# 3. Check that origin remote is set correctly
if ! git remote get-url origin | grep -q "github.com/rafa8525/consensus-project.git"; then
  echo "❌ Origin remote not set properly"
  exit 1
fi

echo "✅ All clear: safe to push."
