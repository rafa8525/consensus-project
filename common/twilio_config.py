"""Load only established private Twilio configuration for scheduled ACS alerts.

No credentials are logged, no files are modified, and sending is NOT enabled
by default. Runtime environment overrides private files; project .env overrides
the legacy reminder-api .env as the newer explicit configuration.
"""
from __future__ import annotations

import os
from pathlib import Path

CREDENTIAL_KEYS = (
    "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
    "TWILIO_FROM_NUMBER", "TWILIO_TO_NUMBER",
)
SAFETY_KEYS = ("TWILIO_ENABLE_SEND", "TWILIO_SILENCE")
ALLOWED_KEYS = CREDENTIAL_KEYS + SAFETY_KEYS


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    # Existing project dependency; never execute a .env file as shell/Python.
    from dotenv import dotenv_values
    values = dotenv_values(path)
    return {key: value for key in ALLOWED_KEYS
            if isinstance((value := values.get(key)), str) and value.strip()}


def load_existing_twilio_settings(
    home: Path | None = None, environ: dict | None = None
) -> dict[str, str]:
    root = Path.home() if home is None else home
    environment = os.environ if environ is None else environ
    result: dict[str, str] = {}
    for path in (
        root / "reminder-api/.env",
        root / "consensus-project/memory/.env",
        root / "consensus-project/.env",
    ):
        result.update(_read_dotenv(path))
    result.update({key: environment[key] for key in ALLOWED_KEYS
                   if environment.get(key)})
    # Fail closed. Legacy credential files do not imply permission to send.
    result.setdefault("TWILIO_ENABLE_SEND", "0")
    result.setdefault("TWILIO_SILENCE", "0")
    return result
