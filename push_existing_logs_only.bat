@echo off
echo Smart uploader: only pushing files that exist...

setlocal

if exist upload_sync\manual_push\kitchen_log.md (
  python batch_push_md.py "upload_sync/manual_push/kitchen_log.md" "memory/logs/geofencing/kitchen_log.md"
) else (
  echo ❌ kitchen_log.md not found. Skipping.
)

if exist upload_sync\manual_push\meal_log.md (
  python batch_push_md.py "upload_sync/manual_push/meal_log.md" "memory/logs/nutrition/meal_log.md"
) else (
  echo ❌ meal_log.md not found. Skipping.
)

if exist upload_sync\manual_push\heart_log.md (
  python batch_push_md.py "upload_sync/manual_push/heart_log.md" "memory/logs/fitness/heart_log.md"
) else (
  echo ❌ heart_log.md not found. Skipping.
)

if exist upload_sync\manual_push\transit_log.md (
  python batch_push_md.py "upload_sync/manual_push/transit_log.md" "memory/logs/transport/transit_log.md"
) else (
  echo ❌ transit_log.md not found. Skipping.
)

echo ✅ All existing logs processed.
endlocal
pause