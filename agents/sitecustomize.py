
from pathlib import Path
from datetime import datetime
import atexit
import re

def _streaming_recommendation_gate():
    try:
        mem_dir = Path("/home/rafa1215/memory/logs/system/predictions")
        repo_dir = Path("/home/rafa1215/consensus-project/memory/logs/system/predictions")
        paths = []

        today = datetime.now().strftime("%Y-%m-%d")
        for base in (mem_dir, repo_dir):
            p = base / f"prediction_feed_{today}.md"
            if p.exists():
                paths.append(p)

        if not paths:
            latest = sorted(mem_dir.glob("prediction_feed_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            if latest:
                paths.append(latest[0])
                mirror = repo_dir / latest[0].name
                if mirror.exists():
                    paths.append(mirror)

        allowed_platforms = [
            "Netflix", "Max", "Hulu", "Prime Video", "Paramount+", "Apple TV+",
            "Disney+", "Tubi", "Roku Channel", "Plex", "Hoopla", "Fawesome",
            "Freevee", "Fandango at Home Free"
        ]

        def has_proof(line):
            low = line.lower()
            has_platform = any(p.lower() in low for p in allowed_platforms)
            has_source = ("source:" in low) or ("verified:" in low) or ("justwatch" in low)
            has_date = ("checked:" in low) or ("date checked:" in low)
            rent_buy_only = ("rent" in low or "buy" in low) and not any(
                p.lower() in low for p in allowed_platforms
            )
            return has_platform and has_source and has_date and not rent_buy_only

        for path in paths:
            original = path.read_text(errors="replace")
            lines = original.splitlines()
            out = []
            changed = False
            i = 0

            while i < len(lines):
                line = lines[i]
                low = line.lower()

                starts_unverified_reco_block = (
                    "here are 3 picks for tonight" in low
                    or "recommended movies" in low
                    or "movie recommendation" in low
                )

                if starts_unverified_reco_block:
                    block = [line]
                    j = i + 1
                    while j < len(lines):
                        nxt = lines[j]
                        if j > i + 1 and (
                            re.match(r"^\d+\.\s+\[[A-Z]+\]", nxt)
                            or nxt.startswith("## ")
                        ):
                            break
                        block.append(nxt)
                        j += 1

                    movie_lines = [
                        b for b in block
                        if b.strip().startswith("-") and "imdb" in b.lower()
                    ]

                    if movie_lines and not all(has_proof(b) for b in movie_lines):
                        out.append("3. [LOW] Streaming recommendation gate blocked unverified movie picks.")
                        out.append("   - Reason: Movie suggestions must include verified current U.S. streaming platform, verification source, and date checked. Rent/buy-only or ambiguous titles are rejected.")
                        changed = True
                        i = j
                        continue

                out.append(line)
                i += 1

            if changed:
                path.write_text("\n".join(out).rstrip() + "\n")
                audit = mem_dir / "streaming_gate_audit.log"
                audit.parent.mkdir(parents=True, exist_ok=True)
                with audit.open("a") as f:
                    f.write(f"{datetime.now().isoformat()} blocked_unverified_movie_recommendations file={path}\n")

                mirror_audit = repo_dir / "streaming_gate_audit.log"
                mirror_audit.parent.mkdir(parents=True, exist_ok=True)
                try:
                    mirror_audit.write_text(audit.read_text())
                except Exception:
                    pass

    except Exception as exc:
        try:
            audit = Path("/home/rafa1215/memory/logs/system/predictions/streaming_gate_audit.log")
            audit.parent.mkdir(parents=True, exist_ok=True)
            with audit.open("a") as f:
                f.write(f"{datetime.now().isoformat()} streaming_gate_error={exc!r}\n")
        except Exception:
            pass

atexit.register(_streaming_recommendation_gate)
