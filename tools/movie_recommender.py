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
        twilio_guard.send_sms(client, body=message_text, from_=FROM_NUM, to=TO_NUM)
        log_heartbeat("✅ SMS sent successfully on first attempt")
        return True
    except Exception as e1:
        log_heartbeat(f"⚠️ SMS attempt 1 failed: {e1}")
        time.sleep(10)
        try:
            twilio_guard.send_sms(client, body=message_text, from_=FROM_NUM, to=TO_NUM)
            log_heartbeat("✅ SMS sent successfully on retry")
            return True
        except Exception as e2:
            log_heartbeat(f"❌ SMS retry failed: {e2}")
            return False

def generate_recommendations():
    """
    Generate recommendations ONLY from candidates with current,
    explicit U.S. streaming verification.

    Never guess or randomly assign a streaming platform.
    """

    import datetime
    import json
    from pathlib import Path
    from textwrap import shorten

    canonical_memory = Path("/home/rafa1215/memory")

    overlay_file = (
        canonical_memory
        / "state"
        / "movie_candidates_overlay.json"
    )

    verification_queue = (
        canonical_memory
        / "state"
        / "streaming_verification_queue.json"
    )

    authoritative_export = (
        canonical_memory
        / "exports"
        / "movie_list_export.txt"
    )

    MAX_VERIFICATION_AGE_DAYS = 7

    # ---------------------------------------------------------
    # Read watched / removed titles from authoritative export.
    # ---------------------------------------------------------
    blocked_titles = set()

    if authoritative_export.exists():
        for raw in authoritative_export.read_text(
            encoding="utf-8",
            errors="replace"
        ).splitlines():

            if not raw.strip() or raw.lstrip().startswith("#"):
                continue

            parts = raw.split("\t")

            if len(parts) < 3:
                continue

            title = parts[0].strip()
            status = parts[2].strip().lower()

            if (
                "watched" in status
                or "removed" in status
                or status.startswith("yes")
                or status.startswith("no")
            ):
                blocked_titles.add(title.casefold())

    # ---------------------------------------------------------
    # Load candidate overlay.
    # ---------------------------------------------------------
    candidates = []

    if overlay_file.exists():
        try:
            payload = json.loads(
                overlay_file.read_text(
                    encoding="utf-8",
                    errors="replace"
                )
            )
            candidates = payload.get("candidates", [])
        except Exception as exc:
            log_heartbeat(
                f"Candidate overlay unreadable: {exc!r}"
            )

    if not isinstance(candidates, list):
        candidates = []

    today = datetime.date.today()

    verified = []
    pending = []

    # ---------------------------------------------------------
    # Enforce streaming proof.
    # ---------------------------------------------------------
    for item in candidates:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip()

        if not title:
            continue

        if title.casefold() in blocked_titles:
            continue

        platform = str(item.get("platform", "")).strip()
        country = str(item.get("country", "")).strip().upper()

        checked_date = str(
            item.get(
                "checked_date",
                item.get("verified_date", "")
            )
        ).strip()

        source = str(
            item.get(
                "verification_source",
                item.get("source_url", "")
            )
        ).strip()

        availability = str(
            item.get(
                "availability",
                item.get("access", "")
            )
        ).strip().lower()

        verified_flag = item.get("verified") is True

        date_ok = False

        if checked_date:
            try:
                checked = datetime.date.fromisoformat(
                    checked_date[:10]
                )

                age = (today - checked).days

                date_ok = 0 <= age <= MAX_VERIFICATION_AGE_DAYS

            except ValueError:
                date_ok = False

        stream_now = availability in {
            "stream",
            "streaming",
            "subscription",
            "included",
            "free",
            "free with ads",
        }

        proof_ok = (
            verified_flag
            and bool(platform)
            and country == "US"
            and date_ok
            and bool(source)
            and stream_now
        )

        if proof_ok:
            verified.append(item)
        else:
            pending.append(
                {
                    "title": title,
                    "year": item.get("year"),
                    "status": "Needs Verification",
                    "reason": (
                        "Missing or stale current U.S. "
                        "streaming proof"
                    ),
                    "required_fields": [
                        "verified=true",
                        "platform",
                        "country=US",
                        "checked_date",
                        "verification_source",
                        "availability=subscription/included/free",
                    ],
                }
            )

    # ---------------------------------------------------------
    # Always maintain verification queue.
    # ---------------------------------------------------------
    verification_queue.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    verification_queue.write_text(
        json.dumps(
            {
                "generated": datetime.datetime.now().isoformat(),
                "pending_count": len(pending),
                "pending": pending,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

    outfile = OUT_DIR / f"weekly_list_{timestamp}.md"

    # ---------------------------------------------------------
    # Fail closed when nothing is verified.
    # ---------------------------------------------------------
    if not verified:
        body = (
            f"# Weekly Movie Recommendations ({timestamp})\n\n"
            "No verified stream-now recommendation is available.\n\n"
            "The recommender intentionally refused to guess a "
            "streaming platform.\n\n"
            f"Pending verification: {len(pending)} title(s).\n\n"
            f"Verification queue: {verification_queue}\n"
        )

        outfile.write_text(
            body,
            encoding="utf-8"
        )

        log_heartbeat(
            "Movie recommender BLOCKED safely: "
            f"verified=0 pending={len(pending)}"
        )

        print(
            "BLOCKED: No currently verified U.S. "
            "stream-now candidates."
        )

        print(
            f"Verification queue written: "
            f"{verification_queue}"
        )

        print(
            "No SMS was sent because there is no "
            "verified recommendation."
        )

        print(
            f"Report written: {outfile}"
        )

        return

    # ---------------------------------------------------------
    # Recommend only verified titles.
    # ---------------------------------------------------------
    verified = sorted(
        verified,
        key=lambda x: (
            -float(x.get("imdb", 0) or 0),
            str(x.get("title", "")).casefold(),
        ),
    )

    selected = verified[:10]

    results = []

    for item in selected:
        results.append(
            {
                "title": item["title"],
                "year": item.get("year"),
                "platform": item["platform"],
                "availability": item.get("availability"),
                "verified": True,
                "checked_date": item.get(
                    "checked_date",
                    item.get("verified_date"),
                ),
                "verification_source": item.get(
                    "verification_source",
                    item.get("source_url"),
                ),
                "imdb": item.get("imdb"),
            }
        )

    with outfile.open(
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            f"# Weekly Movie Recommendations ({timestamp})\n\n"
        )

        for i, r in enumerate(results, 1):

            f.write(
                f"## {i}. {r['title']}\n"
            )

            if r.get("year"):
                f.write(
                    f"- Year: {r['year']}\n"
                )

            f.write(
                f"- Platform: {r['platform']}\n"
            )

            f.write(
                f"- Availability: {r['availability']}\n"
            )

            f.write(
                f"- Checked: {r['checked_date']}\n"
            )

            f.write(
                f"- Verification source: "
                f"{r['verification_source']}\n"
            )

            if r.get("imdb"):
                f.write(
                    f"- IMDb: {r['imdb']}\n"
                )

            f.write("\n")

    log_heartbeat(
        "Movie recommender executed with verified "
        f"streaming proof | total={len(results)}"
    )

    msg_header = "Verified movie picks:\n"

    msg_body = "\n".join(
        [
            f"{i+1}. {r['title']} ({r['platform']})"
            for i, r in enumerate(results)
        ]
    )

    message_text = shorten(
        msg_header + msg_body,
        width=1450,
        placeholder="...",
    )

    success = send_sms(message_text)

    if success:
        print(
            "SMS notification delivered with "
            "verified recommendations."
        )
    else:
        print(
            "SMS delivery failed or is unavailable."
        )

    print(
        f"Verified movie recommendations saved to {outfile}"
    )

    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    generate_recommendations()