from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import threading
from typing import Any, Dict, Mapping, Optional, Tuple

import requests

__all__ = ["extract_identity", "Identity"]


_jwt_field_cache: Dict[str, str] = {}
_cache_lock = threading.Lock()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

_COOKIE_RE = re.compile(r"\s*([^=;]+)=([^;]*)")


class Identity:
    def __init__(
        self, user_id: Optional[str], provider: str, raw_claims: Optional[dict] = None
    ):
        self.user_id = user_id
        self.provider = provider
        self.raw_claims = raw_claims or {}

    def __repr__(self):
        return f"Identity(user_id={self.user_id!r}, provider={self.provider!r})"


def _parse_cookie_header(cookie_header: str | None) -> dict[str, str]:
    if not cookie_header:
        return {}
    return {m.group(1): m.group(2) for m in _COOKIE_RE.finditer(cookie_header)}


def _b64_urlsafe_decode(segment: str) -> bytes:
    pad = "=" * ((4 - len(segment) % 4) % 4)
    return base64.urlsafe_b64decode(segment + pad)


def _decode_jwt_payload(token: str) -> dict[str, Any] | None:
    try:
        _, payload_b64, *_ = token.split(".")
        return json.loads(_b64_urlsafe_decode(payload_b64))
    except Exception:
        return None


def _get_jwt_schema_hash(claims: dict[str, Any]) -> str:
    schema = {k: type(v).__name__ for k, v in claims.items()}
    schema_str = json.dumps(schema, sort_keys=True)
    return hashlib.sha256(schema_str.encode()).hexdigest()[:16]


def _call_llm_for_field_identification(claims: dict[str, Any]) -> Optional[str]:
    if not OPENROUTER_API_KEY:
        return None

    prompt = f"""Given this JWT payload, identify the field that contains the user's identity (prioritize email, then username):

{json.dumps(claims, indent=2)}

Respond with ONLY the field name that contains the user identity. If there's an email field, return that. Otherwise return the username field. If neither exists, return the most appropriate user identifier field.

Examples:
- If payload has {{"email": "user@example.com", "sub": "123"}}, respond: email
- If payload has {{"username": "john_doe", "id": "456"}}, respond: username
- If payload has {{"user_email": "user@example.com"}}, respond: user_email

Response (field name only):"""

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "google/gemini-2.5-flash",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 50,
            },
            timeout=5,
        )

        if response.status_code == 200:
            result = response.json()
            field_name = result["choices"][0]["message"]["content"].strip()
            if field_name in claims:
                return field_name
    except Exception:
        pass

    return None


def _extract_user_from_jwt(claims: dict[str, Any]) -> Optional[str]:
    schema_hash = _get_jwt_schema_hash(claims)

    with _cache_lock:
        if schema_hash in _jwt_field_cache:
            field_name = _jwt_field_cache[schema_hash]
            return str(claims.get(field_name)) if field_name in claims else None

    field_name = _call_llm_for_field_identification(claims)

    if field_name:
        with _cache_lock:
            _jwt_field_cache[schema_hash] = field_name
        return str(claims.get(field_name))

    common_fields = [
        "email",
        "user_email",
        "username",
        "user_name",
        "sub",
        "user_id",
        "uid",
        "id",
    ]
    for field in common_fields:
        if field in claims and claims[field]:
            with _cache_lock:
                _jwt_field_cache[schema_hash] = field
            return str(claims[field])

    return None


def _from_jwt(
    token: str,
) -> Tuple[Optional[str], Optional[str], Optional[dict[str, Any]]]:
    """Extract user ID and session ID from JWT."""
    claims = _decode_jwt_payload(token)
    if not claims:
        return None, None, None

    uid = _extract_user_from_jwt(claims)
    sid = claims.get("sid") or claims.get("jti")

    return (
        uid,
        str(sid) if sid is not None else None,
        claims,
    )


def _fingerprint(headers: Mapping[str, str]) -> str:
    ua = headers.get("user-agent", "")
    ip = (
        headers.get("cf-connecting-ip")
        or headers.get("x-forwarded-for", "").split(",")[0]
        or headers.get("remote-addr", "")
    )
    return hashlib.sha256(f"{ip}|{ua}".encode()).hexdigest()[:32]


def _is_auth_endpoint(request) -> bool:
    path = getattr(request, "path", None)
    if path is None:
        path = getattr(getattr(request, "url", None), "path", "")
    return path.startswith("/api/auth")


def extract_identity(request) -> Identity:
    """Extract user identity from various sources in the request."""
    try:
        if hasattr(request, "user") and getattr(
            request.user, "is_authenticated", False
        ):
            return Identity(
                user_id=str(request.user.id),
                provider="builtin",
                raw_claims=None,
            )
    except (AssertionError, AttributeError):
        # Handle case where AuthenticationMiddleware is not installed
        pass

    if _is_auth_endpoint(request):
        return Identity(user_id=None, provider="none", raw_claims=None)

    headers: dict[str, str] = {k.lower(): v for k, v in request.headers.items()}
    cookies: Mapping[str, str] = getattr(request, "cookies", None)
    if cookies is None:
        cookies = _parse_cookie_header(headers.get("cookie"))

    authz = headers.get("authorization", "")
    if authz.lower().startswith("bearer "):
        token = authz[7:].strip()
        uid, _, claims = _from_jwt(token)
        if uid:
            return Identity(uid, "bearer", claims)

    for name in ("sessionid", "connect.sid"):
        if name in cookies:
            return Identity(
                user_id=None,
                provider="session",
                raw_claims=None,
            )

    return Identity(
        user_id=None,
        provider="none",
        raw_claims=None,
    )
