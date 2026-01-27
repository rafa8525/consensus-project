#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google.oauth2 import service_account
from googleapiclient.discovery import build

VERSION = "2026-01-26-movie-export-stable-v4-write-even-if-small"

DEFAULT_CONFIG = "/home/rafa1215/memory/state/movie_sheets_config.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# If your service account only sees ~31 titles total, this is expected.
# We WARN, but we DO NOT fail. The goal is to generate an export so deltas can work.
WARN_MIN_UNIQUE_TITLES = 20

HEADER_TOKENS = ("movie title", "status", "preference")


def now_utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def load_json(p: Path) -> Dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def safe_tab_for_a1(title: str) -> str:
    # A1 format: 'Tab Name'!A1:C20000 ; internal single quotes doubled.
    return "'" + title.replace("'", "''") + "'"


def norm_cell(x: Any) -> str:
    s = str(x).strip()
    s = re.sub(r"\s+", " ", s)
    return s


def find_tab_title_by_gid(meta: Dict[str, Any], gid: Optional[int]) -> Tuple[str, Optional[int]]:
    sheets = meta.get("sheets", []) or []
    if not sheets:
        return ("", None)
    if gid is not None:
        for sh in sheets:
            props = sh.get("properties", {}) or {}
            if props.get("sheetId") == gid:
                return (str(props.get("title", "")), props.get("sheetId"))
    # fallback: first tab
    props0 = sheets[0].get("properties", {}) or {}
    return (str(props0.get("title", "")), props0.get("sheetId"))


def detect_header_row(values: List[List[Any]]) -> int:
    # Find the row that looks like: Movie Title / Status / Preference
    for i, row in enumerate(values[:50]):
        joined = " | ".join(norm_cell(c).lower() for c in row[:6] if norm_cell(c))
        if all(tok in joined for tok in HEADER_TOKENS):
            return i
    return -1


def extract_rows(values: List[List[Any]]) -> List[Tuple[str, str, str]]:
    header_idx = detect_header_row(values)
    start = header_idx + 1 if header_idx >= 0 else 0
    out: List[Tuple[str, str, str]] = []
    for row in values[start:]:
        if not row:
            continue
        title = norm_cell(row[0]) if len(row) > 0 else ""
        status = norm_cell(row[1]) if len(row) > 1 else ""
        pref = norm_cell(row[2]) if len(row) > 2 else ""
        if not title:
            continue
        # skip accidental header repeats
        if title.lower() in ("movie title", "title"):
            continue
        out.append((title, status, pref))
    return out


def write_export(lines: List[str], out_path: Path, mirror_path: Optional[Path]) -> None:
    ensure_dir(out_path.parent)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote (canonical): {out_path} bytes={out_path.stat().st_size} lines={len(lines)}")
    if mirror_path:
        try:
            ensure_dir(mirror_path.parent)
            mirror_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"Mirrored (repo): {mirror_path} bytes={mirror_path.stat().st_size} lines={len(lines)}")
        except Exception as e:
            print(f"WARN: mirror failed: {e}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--max-rows", type=int, default=20000)
    ap.add_argument("--no-mirror", action="store_true")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    cfg = load_json(cfg_path)
    if not cfg:
        print(f"FAIL: Config missing or unreadable. Expected JSON at {cfg_path}.")
        return 2

    creds_path = Path(str(cfg.get("credentials_json", ""))).expanduser()
    if not creds_path.exists():
        print(f"FAIL: credentials_json does not exist: {creds_path}")
        return 2

    sources = cfg.get("sources", [])
    if not isinstance(sources, list) or not sources:
        print("FAIL: No sources configured in config JSON (sources[]).")
        return 2

    out_path = Path(str(cfg.get("output_path", "/home/rafa1215/memory/exports/movie_list_export.txt"))).expanduser()
    mirror_path = None if args.no_mirror else Path(str(cfg.get("repo_mirror_path", ""))).expanduser()
    if mirror_path and str(mirror_path).strip() == "":
        mirror_path = None

    print(f"RUN v{VERSION}")
    print(f"Time (UTC): {now_utc_iso()}")
    print(f"Config: {cfg_path}")

    creds = service_account.Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)

    per_source: List[Tuple[str, int, int, str]] = []  # (year, sheetId, titles, tab_title_preview)
    merged: Dict[str, Tuple[str, str, str, str]] = {}  # key -> (title, year, status, pref)

    def a1(tab_title: str, inner: str) -> str:
        return safe_tab_for_a1(tab_title) + "!" + inner

    for src in sources:
        year = str(src.get("name", "")).strip() or "unknown"
        spreadsheet_id = str(src.get("spreadsheet_id", "")).strip()
        gid = src.get("gid", None)
        if spreadsheet_id == "":
            print(f"WARN: {year}: missing spreadsheet_id, skipping")
            continue

        meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        tab_title, picked_sheet_id = find_tab_title_by_gid(meta, gid if isinstance(gid, int) else None)
        tab_disp = tab_title.replace("\n", " ")[:60]
        if not tab_title:
            print(f"WARN: {year}: no tab title found, skipping")
            continue

        rng = a1(tab_title, f"A1:C{args.max_rows}")
        try:
            values = svc.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=rng).execute().get("values", [])
        except Exception as e:
            print(f"WARN: {year}: fetch failed: {e}")
            continue

        rows = extract_rows(values)
        per_source.append((year, int(picked_sheet_id) if picked_sheet_id is not None else -1, len(rows), tab_disp))
        for (title, status, pref) in rows:
            key = title.lower()
            if key in merged:
                continue
            merged[key] = (title, year, status, pref)

    # Build export lines (keep it simple + deterministic)
    export_lines: List[str] = []
    export_lines.append("# movie_list_export")
    export_lines.append(f"# generated_utc={now_utc_iso()}")
    export_lines.append(f"# exporter_version={VERSION}")
    export_lines.append(f"# sources={len(per_source)} unique_titles={len(merged)}")
    export_lines.append("# format: Title<TAB>Year<TAB>Status<TAB>Preference")
    export_lines.append("")

    # Sort by title
    items = sorted(merged.values(), key=lambda t: t[0].lower())
    for (title, year, status, pref) in items:
        export_lines.append(f"{title}\t{year}\t{status}\t{pref}")

    # Always write export, even if small.
    write_export(export_lines, out_path, mirror_path)

    # Summary (short)
    print("Summary per source:")
    for (year, sheet_id, titles, tab_disp) in per_source:
        print(f"- {year}: sheetId={sheet_id} titles={titles} tab='{tab_disp}'")
    print(f"Merged unique titles: {len(merged)}")

    if len(merged) < WARN_MIN_UNIQUE_TITLES:
        print(
            "WARN: export looks small (as seen by service account). "
            "This is OK for deltas, but if you expect hundreds of movies, the service account isn't seeing them."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
