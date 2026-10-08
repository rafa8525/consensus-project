"""Read-only ACS backup health evaluation. No network or agent mutations."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json

MAX_AGE_HOURS = 36


def evaluate(path: Path, now: datetime | None = None, max_age_hours: float = MAX_AGE_HOURS) -> dict:
    if now is None:
        now = datetime.now(timezone.utc)
    if not path.is_file() or path.is_symlink():
        return {"ok": False, "status": "critical", "reason": "verified backup receipt missing"}
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        if (record.get("status") != "uploaded_verified"
                or record.get("restore_verified") is not True
                or not isinstance(record.get("file_count"), int)
                or record["file_count"] <= 0
                or not record.get("remote_id")
                or len(record.get("encrypted_sha256", "")) != 64):
            raise ValueError("invalid verification record")
        stamp = datetime.fromisoformat(record["finished_at_utc"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("naive timestamp")
        age = (now - stamp).total_seconds() / 3600
        if age < -0.25 or age > max_age_hours:
            return {"ok": False, "status": "critical", "reason": "verified backup overdue"}
        return {"ok": True, "status": "healthy", "age_hours": round(age, 2),
                "file_count": record["file_count"]}
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError):
        return {"ok": False, "status": "critical", "reason": "verification record unreadable or invalid"}
