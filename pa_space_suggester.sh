#!/usr/bin/env bash
set -euo pipefail

# ------------ config you can tweak -------------
ROOT="$HOME"
# Projects to protect entirely (no deletions inside)
PROTECT_DIRS=( "mysite" "reminder-api" "consensus-project" )
# Minimum age/size
MIN_AGE_DAYS=7
MIN_SIZE="+1M"
# Parallelism
P=6
# ----------------------------------------------

OUT_DIR="$HOME/_cleanup"
mkdir -p "$OUT_DIR"

PROTECT_PRUNE=()
for d in "${PROTECT_DIRS[@]}"; do
  PROTECT_PRUNE+=( -path "$ROOT/$d" -prune -o )
done

# Build preview lists
FILES_LOG_TXT="$OUT_DIR/files_log_txt.list"
FILES_PYC="$OUT_DIR/files_pyc.list"
DIRS_CACHE="$OUT_DIR/dirs_cache.list"
DIRS_BACKUP="$OUT_DIR/dirs_backup.list"

: > "$FILES_LOG_TXT"
: > "$FILES_PYC"
: > "$DIRS_CACHE"
: > "$DIRS_BACKUP"

echo "[1/4] Scanning logs/txt (>${MIN_SIZE}, older than ${MIN_AGE_DAYS}d) ..."
find "$ROOT" \
  "${PROTECT_PRUNE[@]}" \
  \( -type f \( -iname '*.log' -o -iname '*.txt' \) -a -mtime +"$MIN_AGE_DAYS" -a -size "$MIN_SIZE" \) \
  -print0 >> "$FILES_LOG_TXT"

echo "[2/4] Scanning .pyc (>${MIN_SIZE}, older than ${MIN_AGE_DAYS}d) ..."
find "$ROOT" \
  "${PROTECT_PRUNE[@]}" \
  \( -type f -iname '*.pyc' -a -mtime +"$MIN_AGE_DAYS" -a -size "$MIN_SIZE" \) \
  -print0 >> "$FILES_PYC"

echo "[3/4] Scanning __pycache__ dirs (older than ${MIN_AGE_DAYS}d, dir size >${MIN_SIZE}) ..."
# list dirs, then size-filter them with du
find "$ROOT" \
  "${PROTECT_PRUNE[@]}" \
  \( -type d -name '__pycache__' -a -mtime +"$MIN_AGE_DAYS" \) -print0 \
| xargs -0 -P "$P" -I{} du -sb "{}" 2>/dev/null \
| awk -v mins=1048576 '($1>=mins){$1=$1; print $2}' \
| tr '\n' '\0' >> "$DIRS_CACHE"

echo "[4/4] Scanning *backup* dirs (older than ${MIN_AGE_DAYS}d, dir size >${MIN_SIZE}) ..."
find "$ROOT" \
  "${PROTECT_PRUNE[@]}" \
  \( -type d \( -iname '*_backup*' -o -iname '*backup*' \) -a -mtime +"$MIN_AGE_DAYS" \) -print0 \
| xargs -0 -P "$P" -I{} du -sb "{}" 2>/dev/null \
| awk -v mins=1048576 '($1>=mins){$1=$1; print $2}' \
| tr '\n' '\0' >> "$DIRS_BACKUP"

# Compose preview table: SIZE,TYPE,REASON,PATH
PREVIEW="$OUT_DIR/preview.tsv"
: > "$PREVIEW"

emit_table () {
  local kind="$1" reason="$2" list="$3"
  if [ -s "$list" ]; then
    # shellcheck disable=SC2016
    xargs -0 -P "$P" -I{} bash -c 'S=$(du -sb "{}" 2>/dev/null | awk "{print \$1}"); echo -e "${S}\t'"$kind"'\t'"$reason"'\t{}"' \
      < "$list" >> "$PREVIEW"
  fi
}

emit_table "file" "log/txt (safe to delete historical logs & exports)" "$FILES_LOG_TXT"
emit_table "file" "pyc bytecode (rebuilds automatically)" "$FILES_PYC"
emit_table "dir"  "__pycache__ (compiled caches)" "$DIRS_CACHE"
emit_table "dir"  "backup snapshot/archives" "$DIRS_BACKUP"

# Sort by size desc and add human sizes
SORTED="$OUT_DIR/preview_sorted.tsv"
awk -F'\t' '{print $0}' "$PREVIEW" \
| sort -k1,1nr > "$SORTED"

TOTAL_BYTES=$(awk -F'\t' '{s+=$1} END{print s+0}' "$SORTED")
TOTAL_HUMAN=$(numfmt --to=iec --suffix=B --padding=7 "$TOTAL_BYTES" 2>/dev/null || echo "${TOTAL_BYTES}B")

echo
echo "=== Preview (largest first) ==="
printf "%-10s | %-4s | %-35s | %s\n" "SIZE" "TYPE" "REASON" "PATH"
printf -- "-----------+------+-------------------------------------+----------------------------------------\n"
awk -F'\t' '{
  human=$1; cmd="numfmt --to=iec --suffix=B "human; cmd|getline human; close(cmd);
  printf "%-10s | %-4s | %-35s | %s\n", human, $2, $3, $4
}' "$SORTED" || true

echo
echo "Total reclaimable (if all deleted): $TOTAL_HUMAN"
echo "Full table saved to: $SORTED"
echo
echo "Delete usage:"
echo "  bash pa_space_suggester.sh --delete-all"
echo "  # or delete by class:"
echo "  bash pa_space_suggester.sh --delete logs    # only .log/.txt"
echo "  bash pa_space_suggester.sh --delete pyc     # only .pyc"
echo "  bash pa_space_suggester.sh --delete caches  # only __pycache__ dirs"
echo "  bash pa_space_suggester.sh --delete backups # only *backup* dirs"

# Delete modes
if [[ "${1:-}" == "--delete-all" ]]; then
  set -x
  [ -s "$FILES_LOG_TXT" ] && xargs -0 -P "$P" -I{} rm -f "{}" < "$FILES_LOG_TXT"
  [ -s "$FILES_PYC"     ] && xargs -0 -P "$P" -I{} rm -f "{}" < "$FILES_PYC"
  [ -s "$DIRS_CACHE"    ] && xargs -0 -P "$P" -I{} rm -rf "{}" < "$DIRS_CACHE"
  [ -s "$DIRS_BACKUP"   ] && xargs -0 -P "$P" -I{} rm -rf "{}" < "$DIRS_BACKUP"
  set +x
  echo "✅ Deletion done."
  exit 0
fi

if [[ "${1:-}" == "--delete" ]]; then
  case "${2:-}" in
    logs)    [ -s "$FILES_LOG_TXT" ] && xargs -0 -P "$P" -I{} rm -f "{}" < "$FILES_LOG_TXT" ;;
    pyc)     [ -s "$FILES_PYC"     ] && xargs -0 -P "$P" -I{} rm -f "{}" < "$FILES_PYC" ;;
    caches)  [ -s "$DIRS_CACHE"    ] && xargs -0 -P "$P" -I{} rm -rf "{}" < "$DIRS_CACHE" ;;
    backups) [ -s "$DIRS_BACKUP"   ] && xargs -0 -P "$P" -I{} rm -rf "{}" < "$DIRS_BACKUP" ;;
    *) echo "Unknown class: ${2:-} (use logs|pyc|caches|backups)"; exit 2 ;;
  esac
  echo "✅ Deletion done for class: $2"
  exit 0
fi
