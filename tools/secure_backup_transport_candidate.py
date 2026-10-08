#!/usr/bin/env python3
"""Staged secure backup transport; NOT wired into schedulers or agents.

Encryption must happen before Google Drive transfer. The encryption key must
be stored outside this repository, backed up separately, and never committed.
Requires the optional 'cryptography' dependency. No implicit uploads.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MAGIC = b"ACSENC01"
AAD = b"acs-consensus-encrypted-backup-v1"
MAX_ENCRYPT_BYTES = 110 * 1024 * 1024


def key_bytes(path: Path) -> bytes:
    """Load 32 raw bytes from a private external key file."""
    if path.is_symlink() or not path.is_file():
        raise ValueError("key file missing or symlink")
    mode = path.stat().st_mode & 0o777
    if mode & 0o077:
        raise PermissionError("key permissions must exclude group and others")
    key = path.read_bytes()
    if len(key) != 32:
        raise ValueError("key must contain exactly 32 random bytes")
    return key


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """AES-256-GCM with a fresh cryptographically random nonce per backup."""
    if len(key) != 32 or len(plaintext) > MAX_ENCRYPT_BYTES:
        raise ValueError("invalid key or plaintext exceeds cap")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    nonce = os.urandom(12)
    return MAGIC + nonce + AESGCM(key).encrypt(nonce, plaintext, AAD)


def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    if len(key) != 32 or not ciphertext.startswith(MAGIC) or len(ciphertext) < len(MAGIC) + 12 + 16:
        raise ValueError("invalid encrypted backup header")
    if len(ciphertext) > MAX_ENCRYPT_BYTES + 64:
        raise ValueError("encrypted backup exceeds cap")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    start = len(MAGIC)
    return AESGCM(key).decrypt(ciphertext[start:start + 12], ciphertext[start + 12:], AAD)


def encrypt_file(source: Path, destination: Path, key_file: Path) -> dict:
    """Explicit operation; refuses overwrite and never writes plaintext to Drive."""
    if not source.is_file() or source.is_symlink():
        raise ValueError("source must be a regular file")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("encrypted destination already exists")
    blob = source.read_bytes()
    encrypted = encrypt(blob, key_bytes(key_file))
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".acs-encrypted-", dir=destination.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(encrypted)
            f.flush()
            os.fsync(f.fileno())
        os.link(tmp, destination)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return {"status": "encrypted", "bytes": len(encrypted),
            "sha256": hashlib.sha256(encrypted).hexdigest()}


def verify_encrypted_archive(encrypted_file: Path, key_file: Path, candidate_module) -> dict:
    """Decrypt only in memory and verify full ZIP manifest and per-file SHA-256."""
    import zipfile
    ciphertext = encrypted_file.read_bytes()
    plaintext = decrypt(ciphertext, key_bytes(key_file))
    with zipfile.ZipFile(io.BytesIO(plaintext)) as z:
        if z.testzip() is not None:
            raise ValueError("damaged ZIP archive")
        names = z.namelist()
        if len(names) != len(set(names)) or candidate_module.MANIFEST not in names:
            raise ValueError("invalid ZIP manifest")
        manifest = json.loads(z.read(candidate_module.MANIFEST))
        expected = manifest["files"]
        if not expected or set(names) != set(expected) | {candidate_module.MANIFEST}:
            raise ValueError("missing or extra archive entries")
        for name, digest in expected.items():
            if candidate_module.disallowed(Path(name)) or name.startswith("/") or ".." in Path(name).parts:
                raise ValueError("unsafe archive path")
            if not hmac.compare_digest(hashlib.sha256(z.read(name)).hexdigest(), digest):
                raise ValueError("backup file integrity failure")
    return {"status": "verified", "file_count": len(expected),
            "encrypted_sha256": hashlib.sha256(ciphertext).hexdigest()}


def upload_verified(encrypted_file: Path, drive_service, folder_id: str) -> dict:
    """Only upload encrypted .acsenc; confirm Drive metadata against local bytes."""
    from googleapiclient.http import MediaFileUpload
    if encrypted_file.suffix != ".acsenc" or not encrypted_file.read_bytes().startswith(MAGIC):
        raise ValueError("unencrypted or invalid upload source")
    if not folder_id:
        raise ValueError("Drive folder ID required")
    blob = encrypted_file.read_bytes()
    expected_md5 = base64.b64encode(hashlib.md5(blob).digest()).decode("ascii")
    # Drive's md5Checksum is hex, not base64. Keep comparisons exact.
    expected_hex = hashlib.md5(blob).hexdigest()
    metadata = {"name": encrypted_file.name, "parents": [folder_id]}
    media = MediaFileUpload(str(encrypted_file), mimetype="application/octet-stream", resumable=True)
    result = drive_service.files().create(
        body=metadata, media_body=media, fields="id,size,md5Checksum,name"
    ).execute()
    if (not result.get("id") or int(result.get("size", -1)) != len(blob)
            or not hmac.compare_digest(result.get("md5Checksum") or "", expected_hex)):
        raise RuntimeError("remote checksum or metadata mismatch; upload NOT verified")
    return {"status": "uploaded_verified", "remote_id": result["id"], "bytes": len(blob)}


def check_health(status: dict | None, now: datetime | None = None, max_age_hours: int = 36) -> dict:
    """Read-only evaluator for eventual ACS-01 integration; no state changes."""
    now = now or datetime.now(timezone.utc)
    if not status or status.get("status") != "uploaded_verified":
        return {"status": "critical", "reason": "no verified successful remote backup"}
    try:
        stamp = datetime.fromisoformat(status["finished_at_utc"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("timezone required")
        age = (now - stamp).total_seconds() / 3600
        if age < -0.25 or age > max_age_hours:
            return {"status": "critical", "reason": "backup stale or future timestamp"}
        return {"status": "healthy", "age_hours": round(age, 2)}
    except (KeyError, ValueError, TypeError):
        return {"status": "critical", "reason": "invalid backup status metadata"}
