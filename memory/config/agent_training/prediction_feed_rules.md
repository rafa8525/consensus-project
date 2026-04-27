# Prediction Feed Agent Training Rules

## Movie Recommendation Rules
- Never recommend titles already marked Watched, Removed, or fully watched in memory.
- Never recommend Constantine, Underworld, The Sandman, Invincible, Jupiter's Legacy, The Dark Knight, The Umbrella Academy, Godzilla Minus One, The Witch, The Rip, War Machine, Troll 2, or Primitive War.
- If movie export has no Maybe/Candidate titles, recommend only fresh titles not found in watched history.
- Include IMDb rating when recommending movies.
- Prefer Rafael's taste profile: dark fantasy, supernatural, gothic action, mythological adventure, superhero, monsters, demons, vampires, and stylish comic-book energy.

## System Health Rules
- If system_health_snapshot.md is older than 24 hours, mark System/Project as ACTION REQUIRED.
- Do not describe stale health as healthy.
- Recommend refreshing core_monitors_bundle.py when snapshot is stale.
- Feed confidence should drop if system health is stale.

## Fitness Rules
- If no fitness log exists today, ask for steps, Fitbit screenshot, or swim laps.
- Do not over-warn if a weekly Fitbit report was recently added.

## Family/Event Rules
- If an event date has passed, suggest recap/log/photos/follow-up, not planning reminders.

## Daily JustWatch Movie Recommendation Rule
- Check https://www.justwatch.com/us/movies?release_year_from=2026 daily for new movie candidates.
- Recommend 1–3 movies that match Rafael's taste profile.
- Prefer dark fantasy, supernatural, gothic action, monsters, demons, vampires, mythology, superhero/comic-book energy, Old West/action-adventure.
- Prefer Rafael's streaming services: Netflix, Max, Hulu, Prime Video, Paramount+, Apple TV+, and Disney+.
- Never recommend movies already marked Watched, Removed, or suppressed.
- Include IMDb rating when available.
- Add the best recommendations to the daily prediction feed.


## 2026-04-27 Repair Loop Training

If prediction_feed_agent.py reports System health snapshot OK/STALE or ACTION REQUIRED due to stale system health:

1. Run:
   python3 tools/core_monitors_bundle.py

2. Inspect:
   /home/rafa1215/memory/logs/status/system_health_snapshot.md

3. Refresh known stale feeders when present:
   python3 tools/verify_knowledge_base.py
   python3 tools/movies_monitor.py

4. Rerun:
   python3 tools/core_monitors_bundle.py

5. Confirm:
   Overall: ok

6. Rerun:
   python3 agents/prediction_feed_agent.py

Expected result:
- System health snapshot: OK/RECENT

If Health/Fitness says no fitness log detected, use:
   python3 tools/quick_log.py steps=5000
   python3 tools/quick_log.py laps=50

Then rerun prediction_feed_agent.py and confirm:
- Fitness activity logged today.

This sequence is now the standard recovery workflow for stale health + missing fitness warnings.
