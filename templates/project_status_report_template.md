cat > "$ROOT/templates/project_status_report_template.md" <<'MD'
# Weekly Status — {{WEEK_LABEL}}
**Date range:** {{WEEK_RANGE}}  
**Branch:** {{BRANCH}}  
**Generated at:** {{NOW}}

## Highlights
- …

## Milestones Achieved
- …

## Current Tasks
- …

## Issues / Failures (last 7 days)
- …

## Next Steps
- …

Overall Status: …
MD
