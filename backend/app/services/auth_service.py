import base64
import hashlib
import hmac
import json
import os
import secrets
import time


OWNER_USERNAME = os.getenv("OWNER_USERNAME", "")
OWNER_PASSWORD = os.getenv("OWNER_PASSWORD", "")
OWNER_AUTH_SECRET = os.getenv("OWNER_AUTH_SECRET", "")
TOKEN_TTL_SECONDS = int(os.getenv("OWNER_TOKEN_TTL_SECONDS", "43200"))


def verify_owner_credentials(username: str, password: str) -> bool:
    if not OWNER_USERNAME or not OWNER_PASSWORD:
        return False

    return secrets.compare_digest(username or "", OWNER_USERNAME) and secrets.compare_digest(
        password or "", OWNER_PASSWORD
    )


def _get_signing_secret() -> bytes:
    if not OWNER_AUTH_SECRET:
        raise ValueError("OWNER_AUTH_SECRET is not configured")
    return OWNER_AUTH_SECRET.encode("utf-8")


def create_owner_token(username: str) -> str:
    issued_at = int(time.time())
    payload = {
        "username": username,
        "iat": issued_at,
        "exp": issued_at + TOKEN_TTL_SECONDS,
    }

    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_part = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
    signature = hmac.new(_get_signing_secret(), payload_part.encode("utf-8"), hashlib.sha256).digest()
    signature_part = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    return f"{payload_part}.{signature_part}"


def validate_owner_token(token: str):
    if not token:
        return None

    try:
        payload_part, signature_part = token.split(".", 1)
    except ValueError:
        return None

    try:
        expected_signature = hmac.new(
            _get_signing_secret(), payload_part.encode("utf-8"), hashlib.sha256
        ).digest()
        actual_signature = base64.urlsafe_b64decode(signature_part + "==")
    except Exception:
        return None

    if not hmac.compare_digest(expected_signature, actual_signature):
        return None

    try:
        payload_bytes = base64.urlsafe_b64decode(payload_part + "==")
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None

    exp = payload.get("exp")
    username = payload.get("username")
    if not username or not exp or int(exp) < int(time.time()):
        return None

    if OWNER_USERNAME and not secrets.compare_digest(username, OWNER_USERNAME):
        return None

    return {"username": username, "exp": exp}