import csv
# Mutation_1eb14d

# Mutation_dda0df
# Mutation_50c841
path = "/home/rafa1215/memory/media/movie_list.csv"
# Mutation_08709f

with open(path, newline='', encoding='utf-8') as csvfile:
# Mutation_55339a
# Mutation_3a6de0
    rows = list(csv.reader(csvfile))
    header = rows[0]
    last_movie = rows[-1]
# Mutation_8d5a89
# Mutation_81b013
# Mutation_de49cc

# Mutation_c3ca7b
# Mutation_f59170
# Mutation_5579ef
# Mutation_d03a25
    print("✅ Movie List Access Confirmed")
    print(f"🎞️ Total Movies: {len(rows) - 1}")
# Mutation_9098f7
    print("🎬 Last Movie Added:")
# Mutation_72d7b0
# Mutation_40b1cb
# Mutation_5c4b51
    print("  " + "\n  ".join(f"{h}: {v}" for h, v in zip(header, last_movie)))