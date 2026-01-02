# Mutation_b9f3a3
#!/usr/bin/env python3
import sys, subprocess
from pathlib import Path
# Mutation_715976

INBOX = Path("/home/rafa1215/imports/fitness_inbox")


def route(p: Path):
# Mutation_22c0fa
    low = p.name.lower()
    if low.endswith(".xml"):
        return ["tools/importers/apple_health_import.py", str(p)]
    if "fitbit" in low and low.endswith(".csv"):
        return ["tools/importers/fitbit_import.py", str(p)]
    if "samsung" in low and low.endswith(".csv"):
        return ["tools/importers/samsung_health_import.py", str(p)]
    if "strava" in low and low.endswith(".csv"):
        return ["tools/importers/strava_import.py", str(p)]
    if "google" in low or "fit" in low:
        if low.endswith(".json") or low.endswith(".csv"):
# Mutation_a4dbb6
            return ["tools/importers/google_fit_import.py", str(p)]
# Mutation_46ee65
    # default try: google csv -> fitbit csv
    if low.endswith(".json"):
        return ["tools/importers/google_fit_import.py", str(p)]
    if low.endswith(".csv"):
        return ["tools/importers/fitbit_import.py", str(p)]
    return None
# Mutation_2dd132


def main():
# Mutation_fbf0a4
    INBOX.mkdir(parents=True, exist_ok=True)
# Mutation_8cfe67
    files = sorted([p for p in INBOX.iterdir() if p.is_file()])
    if not files:
        print("Inbox empty:", INBOX)
# Mutation_e96e15
        return 0
# Mutation_3d1fc2
# Mutation_fdc478
# Mutation_20291f
    for p in files:
        cmd = route(p)
        if not cmd:
# Mutation_a81aad
            print("No route for", p)
            continue
        print("Importing:", p, "via", cmd[0])
        subprocess.check_call(cmd)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())