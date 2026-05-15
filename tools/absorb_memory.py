#!/usr/bin/env python3
import os
import sys
import traceback
from pathlib import Path
from datetime import datetime, timezone

MAX_FILE_SIZE = 1_000_000      # skip source files > 1 MB
MAX_TOTAL_BYTES = 25_000_000   # stop output around 25 MB
PREVIEW_LIMIT = 120

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".idea",
    ".vscode",
    "archive",          # huge historical tree
    "cache",            # disposable/generated
    "queue",            # not useful for memory absorption
}

SKIP_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".svg",
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg",
    ".mp4", ".mov", ".avi", ".mkv", ".webm",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".pdf", ".sqlite", ".db", ".bin", ".pyc", ".so", ".dll", ".exe",
    ".woff", ".woff2", ".ttf", ".otf",
    ".graphml", ".json",
}

def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{ts()}] {msg}")

def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

def memory_root() -> Path:
    return repo_root() / "memory"

def output_file() -> Path:
    return memory_root() / "centralized_knowledge_base.txt"

def is_broken_symlink(path: Path) -> bool:
    try:
        return path.is_symlink() and not path.resolve(strict=False).exists()
    except OSError:
        return True

def should_skip(path: Path) -> bool:
    try:
        path_str = str(path)

        if not os.path.lexists(path_str):
            return True

        if is_broken_symlink(path):
            return True

        if not path.is_file():
            return True

        # Skip generated output itself
        if path.name == output_file().name:
            return True

        # Skip nested mirrored memory trees like memory/memory/...
        rel = path.relative_to(memory_root())
        parts = rel.parts
        if len(parts) > 0 and parts[0] == "memory":
            return True

        if path.suffix.lower() in SKIP_EXTS:
            return True

        if os.path.getsize(path_str) > MAX_FILE_SIZE:
            return True

        return False
    except Exception:
        return True

def safe_read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding, errors="strict")
        except UnicodeDecodeError:
            continue
        except Exception:
            raise
    return path.read_text(encoding="utf-8", errors="replace")

def preview_text(text: str, limit: int = PREVIEW_LIMIT) -> str:
    return " ".join(text.split())[:limit]

def iter_files(root: Path):
    for current_root, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        current_path = Path(current_root)
        for name in filenames:
            yield current_path / name

def absorb_memory() -> int:
    root = memory_root()
    out = output_file()

    if not root.exists():
        raise FileNotFoundError(f"Memory root not found: {root}")

    log("🧠 Starting full memory absorption cycle...")

    indexed = 0
    skipped = 0
    failed = 0
    written_bytes = 0

    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")

    with tmp.open("w", encoding="utf-8") as fh:
        header = (
            "Centralized Knowledge Base\n\n"
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}\n"
            f"Memory Root: {root}\n\n"
        )
        fh.write(header)
        written_bytes += len(header.encode("utf-8"))

        for file_path in iter_files(root):
            try:
                if should_skip(file_path):
                    skipped += 1
                    continue

                text = safe_read_text(file_path)
                preview = preview_text(text)

                block = (
                    f"### Ingestion Run {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Source: {file_path}\n\n"
                    f"{text.rstrip()}\n\n"
                    "---\n\n"
                )

                block_bytes = len(block.encode("utf-8"))
                if written_bytes + block_bytes > MAX_TOTAL_BYTES:
                    log("⚠️ Reached output size cap; stopping early to keep file healthy.")
                    break

                fh.write(block)
                written_bytes += block_bytes
                indexed += 1
                log(f"📄 Indexed: {file_path} | Preview: {preview}")

            except FileNotFoundError:
                skipped += 1
                log(f"⚠️ Skipped missing file: {file_path}")
            except OSError as e:
                skipped += 1
                log(f"⚠️ Skipped unreadable file: {file_path} | {e}")
            except Exception as e:
                failed += 1
                log(f"⚠️ Failed to index: {file_path} | {e}")

    os.replace(tmp, out)

    log(f"✅ Absorption complete. indexed={indexed} skipped={skipped} failed={failed} bytes={written_bytes}")
    log(f"📝 Wrote knowledge base: {out}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(absorb_memory())
    except Exception as e:
        log(f"❌ absorb_memory() failed: {e}")
        traceback.print_exc()
        sys.exit(1)