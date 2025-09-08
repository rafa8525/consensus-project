from __future__ import annotations
import os, json, time, hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from mcl_v2.paths import LEDGER

# ---------- helpers ----------
def _env_bool(name: str, default: bool=False) -> bool:
    v = os.getenv(name, str(default))
    return str(v).strip().lower() in ("1","true","yes","on")

def _parse_whitelist(s: str) -> List[str]:
    if not s:
        return []
    return [item.strip() for item in s.split(",") if item.strip()]

def _quiet_hit(spec: str, dt: Optional[datetime]=None) -> bool:
    """
    spec '21-08' means quiet from 21:00 through 07:59.
    '00-00' disables quiet hours.
    """
    dt = dt or datetime.now()
    try:
        sh, eh = spec.split("-")
        sh, eh = int(sh), int(eh)
        if sh == eh:
            return False  # disabled
        h = dt.hour
        if sh < eh:
            return sh <= h < eh
        # wraps midnight
        return (h >= sh) or (h < eh)
    except Exception:
        return False

def _truncate(s: str, n: int=160) -> str:
    s = s or ""
    return s if len(s) <= n else (s[:n] + "…")

# ---------- policy ----------
class SmsPolicy:
    """
    Status codes:
      SKIP_DISABLED, SKIP_NOT_WHITELISTED, SKIP_QUIET_HOURS,
      SKIP_RATE_HOURLY, SKIP_RATE_DAILY,
      ALLOW, DELIVERED, ERROR_*
    """
    def __init__(
        self,
        enabled: bool,
        whitelist: List[str],
        quiet_hours: str = "21-08",
        rate_per_hour: int = 5,
        rate_per_day: int = 10,
    ):
        self.enabled = bool(enabled)
        self.whitelist = set([w for w in whitelist if w])
        self.quiet_hours = quiet_hours
        self.rate_per_hour = int(rate_per_hour)
        self.rate_per_day = int(rate_per_day)

    @classmethod
    def from_env(cls) -> "SmsPolicy":
        enabled = _env_bool("SMS_ENABLED", False)
        whitelist = _parse_whitelist(os.getenv("SMS_WHITELIST", ""))
        quiet = os.getenv("SMS_QUIET_HOURS", "21-08")
        rph = int(os.getenv("SMS_RATE_PER_HOUR", "5") or "5")
        rpd = int(os.getenv("SMS_RATE_PER_DAY", "10") or "10")
        return cls(enabled=enabled, whitelist=whitelist, quiet_hours=quiet,
                   rate_per_hour=rph, rate_per_day=rpd)

    # stable id for ledger grouping
    def stable_key(self, to: str, body: str) -> str:
        raw = f"{to}|{body}".encode("utf-8", "ignore")
        return hashlib.sha256(raw).hexdigest()[:16]

    # read ledger safely
    def _iter_ledger(self):
        try:
            with open(LEDGER, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except Exception:
                        # skip malformed lines
                        continue
        except FileNotFoundError:
            return
        except Exception:
            return

    def _recent_counts(self, now: Optional[datetime]=None) -> Tuple[int,int]:
        now = now or datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        hcount = 0
        dcount = 0
        for entry in self._iter_ledger():
            ts = entry.get("timestamp")
            try:
                # accept 'YYYY-MM-DDTHH:MM:SS' (no tz)
                dt = datetime.fromisoformat(ts)
            except Exception:
                try:
                    # try trimming 'Z'
                    if isinstance(ts, str) and ts.endswith("Z"):
                        dt = datetime.fromisoformat(ts[:-1])
                    else:
                        continue
                except Exception:
                    continue
            if dt >= day_ago:
                dcount += 1
            if dt >= hour_ago:
                hcount += 1
        return hcount, dcount

    def decide(self, to: str, body: str, **kwargs) -> Tuple[str, Dict]:
        """Backward-compatible decision gate; ignores extra kwargs from legacy callers."""
        if not self.enabled:
            return "SKIP_DISABLED", {"reason": "policy_disabled"}
        # require explicit whitelist; empty whitelist blocks
        if (not self.whitelist) or (to not in self.whitelist):
            return "SKIP_NOT_WHITELISTED", {"whitelist": sorted(self.whitelist)}
        if _quiet_hit(self.quiet_hours):
            return "SKIP_QUIET_HOURS", {"window": self.quiet_hours}
        hcount, dcount = self._recent_counts()
        if self.rate_per_hour and hcount >= self.rate_per_hour:
            return "SKIP_RATE_HOURLY", {"limit": self.rate_per_hour, "used": hcount}
        if self.rate_per_day and dcount >= self.rate_per_day:
            return "SKIP_RATE_DAILY", {"limit": self.rate_per_day, "used": dcount}
        return "ALLOW", {}
    def record(self, status: str, to: str, body: str, *, key: Optional[str]=None, meta: Optional[Dict]=None) -> None:
        meta = meta or {}
        try:
            os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
        except Exception:
            pass

        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "to": to,
            "status": status,
            "key": key or self.stable_key(to, body),
            "body": _truncate(body, 200),
            "meta": meta,
        }
        try:
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            # best-effort only — never crash the worker
            pass
