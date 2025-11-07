#!/usr/bin/env python3
from common import twilio_guard
import os, datetime, random, json, time
from pathlib import Path
from textwrap import shorten

# === CONFIG ===
BASE = Path("/home/rafa1215/consensus-project")
MOVIE_FILE = BASE / "memory/movies/movies.txt"
OUT_DIR = BASE / "memory/logs/media/movie_recommendations"
HEARTBEAT_LOG = BASE / "memory/logs/system/heartbeat/heartbeat_movie_recommender.md"
OUT_DIR.mkdir(parents=True, exist_ok=True)
HEARTBEAT_LOG.parent.mkdir(parents=True, exist_ok=True)

# === TWILIO SMS CONFIG ===
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUM = os.getenv("TWILIO_FROM_NUMBER")
TO_NUM = os.getenv("TWILIO_TO_NUMBER")

# === USER PROFILE ===
GENRE_PREFERENCES = ["dark fantasy", "Old West", "supernatural", "action-adventure"]
STREAMING_SERVICES = ["Netflix", "HBO Max", "Disney+", "Hulu", "Apple TV+", "Paramount+"]

CATALOG = {
    "dark fantasy": [
        "The Witcher", "Pan's Labyrinth", "Shadow and Bone", "Crimson Peak",
        "The Pale Blue Eye", "Sleepy Hollow"
    ],
    "Old West": [
        "The Magnificent Seven", "3:10 to Yuma", "The Harder They Fall",
        "Tombstone", "True Grit", "Old Henry"
    ],
    "supernatural": [
        "Constantine", "The Sixth Sense", "The Others", "The Frighteners",
        "Hellboy", "The Conjuring"
    ],
    "action-adventure": [
        "Mad Max: Fury Road", "The Equalizer", "Edge of Tomorrow",
        "Mission: Impossible – Fallout", "Dune", "Gladiator"
    ]
}

def log_heartbeat(msg: str):
    """Append a line to the heartbeat log."""
    with HEARTBEAT_LOG.open("a") as hb:
        hb.write(f"{datetime.datetime.now()} | {msg}\n")

def send_sms(message_text: str):
    """Send SMS with one automatic retry if Twilio fails."""
    from twilio.rest import Client
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    try:
        clienttwilio_guard.send_sms(client, body=message_text, from_=FROM_NUM, to=TO_NUM)
        log_heartbeat("✅ SMS sent successfully on first attempt")
        return True
    except Exception as e1:
        log_heartbeat(f"⚠️ SMS attempt 1 failed: {e1}")
        time.sleep(10)
        try:
            clienttwilio_guard.send_sms(client, body=message_text, from_=FROM_NUM, to=TO_NUM)
            log_heartbeat("✅ SMS sent successfully on retry")
            return True
        except Exception as e2:
            log_heartbeat(f"❌ SMS retry failed: {e2}")
            return False

def generate_recommendations():
    watched = set()
    if MOVIE_FILE.exists():
        with MOVIE_FILE.open() as f:
            watched = {line.strip().lower() for line in f if line.strip()}

    all_picks = [
        (title, genre)
        for genre in GENRE_PREFERENCES
        for title in CATALOG.get(genre, [])
        if title.lower() not in watched
    ]

    random.shuffle(all_picks)
    selected = all_picks[:10]

    results = []
    for title, genre in selected:
        platform = random.choice(STREAMING_SERVICES)
        reason = f"Fits your {genre} preference and matches titles like those in your movie list."
        results.append({
            "title": title, "platform": platform, "reason": reason, "genre": genre
        })

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    outfile = OUT_DIR / f"weekly_list_{timestamp}.md"

    with outfile.open("w") as f:
        f.write(f"# 🎬 Weekly Movie Recommendations ({timestamp})\n\n")
        for i, r in enumerate(results, 1):
            f.write(f"**{i}. {r['title']}**  \n")
            f.write(f"Platform: {r['platform']}  \n")
            f.write(f"Genre: {r['genre']}  \n")
            f.write(f"Reason: {r['reason']}\n\n")

    log_heartbeat(f"✅ Movie recommender executed successfully | Saved file: {outfile.name} | Total: {len(results)}")

    # Build SMS body
    msg_header = "🎬 Weekly Movie Picks:\n"
    msg_body = "\n".join([f"{i+1}. {r['title']} ({r['platform']})" for i, r in enumerate(results)])
    message_text = shorten(msg_header + msg_body, width=1450, placeholder="...")

    # Send SMS with retry
    success = send_sms(message_text)

    if success:
        print("✅ SMS notification delivered.")
    else:
        print("❌ SMS delivery failed. Check heartbeat for details.")

    print(f"✅ Movie recommendations saved to {outfile}")
    print(f"🩺 Heartbeat logged to {HEARTBEAT_LOG}")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    generate_recommendations()