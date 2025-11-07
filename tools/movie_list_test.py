import csv

path = "/home/rafa1215/memory/media/movie_list.csv"

with open(path, newline='', encoding='utf-8') as csvfile:
    rows = list(csv.reader(csvfile))
    header = rows[0]
    last_movie = rows[-1]

    print("✅ Movie List Access Confirmed")
    print(f"🎞️ Total Movies: {len(rows) - 1}")
    print("🎬 Last Movie Added:")
    print("  " + "\n  ".join(f"{h}: {v}" for h, v in zip(header, last_movie)))
