#!/usr/bin/env python3
import csv
from datetime import datetime
from pathlib import Path

# Paths
media_csv = Path("/home/rafa1215/memory/media/movie_list.csv")
summary_file = Path("/home/rafa1215/memory/logs/media/movie_list_voice_summary.txt")
log_file = Path("/home/rafa1215/memory/logs/media/movie_list_status.log")

def generate_voice_summary():
    if not media_csv.exists():
        return "Movie list not found."

    with media_csv.open("r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        if len(reader) <= 1:
            return "No movie data available."

        header = reader[0]
        rows = reader[1:]
        total_movies = len(rows)
        last_entry = rows[-1]
        last_movie = {
            "title": last_entry[0],
            "year": last_entry[1] if len(last_entry) > 1 else "Unknown",
            "notes": last_entry[2] if len(last_entry) > 2 else "No notes"
        }

    # Build readable summary
    summary = (
        f"As of {datetime.now():%Y-%m-%d %H:%M}, your movie list contains {total_movies:,} entries. "
        f"The most recent movie added is {last_movie['title']} ({last_movie['year']}). "
        f"Notes: {last_movie['notes']}."
    )

    # Save summary to file
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    with summary_file.open("w", encoding="utf-8") as f:
        f.write(summary)

    # Log run
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - Voice summary updated: {last_movie['title']} ({last_movie['year']})\n")

    return summary


if __name__ == "__main__":
    print(generate_voice_summary())









