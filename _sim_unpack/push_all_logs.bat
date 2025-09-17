@echo off
echo Uploading logs using batch_push_md.py...

setlocal

python batch_push_md.py "upload_sync/manual_push/kitchen_log.md" "memory/logs/geofencing/kitchen_log.md"
python batch_push_md.py "upload_sync/manual_push/meal_log.md" "memory/logs/nutrition/meal_log.md"
python batch_push_md.py "upload_sync/manual_push/heart_log.md" "memory/logs/fitness/heart_log.md"
python batch_push_md.py "upload_sync/manual_push/transit_log.md" "memory/logs/transport/transit_log.md"

echo All uploads attempted.
endlocal
pause