"""
User ID extraction functions - uses core identity detection with caching and LLM
support.
"""

# TODO put the identity extraction is core so we can cache jwt

import os
import json
import base64
import hashlib
import asyncio
import aiohttp
from typing import Dict, Optional, Any, Union, List
from .core_identity import (
    Headers, parse_headers, detect_provider, parse_cookies
)


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def make_prompt(claims: Dict[str, Any]) -> str:
    """Generate LLM prompt for JWT field identification."""
    return f"""Given this JWT payload, identify the field that contains the user's identity (prioritize email, then username, then user id):

{json.dumps(claims, indent=2)}

Respond with ONLY the field name or path that contains the user identity. If there's an email field, return that. Otherwise return the username field. If neither exists, return the most appropriate user identifier field.

Examples:
- If payload has {{"email": "user@example.com", "sub": "123"}}, respond: email
- If payload has {{"username": "john_doe", "id": "456"}}, respond: username
- If payload has {{"user_email": "user@example.com"}}, respond: user_email
- If payload has {{"user": {{"email": "nested@example.com"}}}}, respond: user.email
- If payload has {{"profile": {{"user": {{"id": "123"}}}}}}, respond: profile.user.id

Response (field name or path only):"""


def hash_obj(obj: Dict[str, Any]) -> str:
    """Create hash of object keys for caching."""
    keys = sorted(get_all_keys(obj))
    return hashlib.md5(json.dumps(keys).encode()).hexdigest()


def get_all_keys(obj: Any, prefix: str = "") -> List[str]:
    """Recursively get all keys from nested dictionary."""
    keys = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_key = f"{prefix}.{key}" if prefix else key
            keys.append(current_key)
            if isinstance(value, dict):
                keys.extend(get_all_keys(value, current_key))
    return keys


def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    """Get value from nested dictionary using dot notation."""
    try:
        keys = path.split(".")
        value = obj
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return None


def decode_jwt_payload(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT payload without verification."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        payload_part = parts[1]
        payload_part += "=" * (-len(payload_part) % 4)

        payload_bytes = base64.urlsafe_b64decode(payload_part)
        return json.loads(payload_bytes.decode())

    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None


async def extract_user_id(
    request_headers: Dict[str, Union[str, List[str]]],
    request_cookies: Optional[Dict[str, str]] = None,
    jwt_field_cache: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """
    Extract user ID from request headers.

    Args:
        request_headers: Raw request headers
        request_cookies: Optional cookies dict
        jwt_field_cache: Optional cache for JWT field mappings

    Returns:
        User ID string if found, None otherwise
    """
    if jwt_field_cache is None:
        jwt_field_cache = {}

    headers = parse_headers(request_headers, request_cookies)
    provider = detect_provider(headers)

    if provider.provider == "clerk":
        return extract_clerk(headers)
    elif provider.provider == "supabase":
        return extract_supabase(headers)
    elif provider.provider == "bearer-jwt":
        return await extract_bearer_jwt(headers, jwt_field_cache)
    else:
        return None


def extract_clerk(headers: Headers) -> Optional[str]:
    """Extract user ID from Clerk authentication."""
    # Check for direct user ID header
    user_id_header = headers.headers.get("x-clerk-user-id")
    if user_id_header:
        return user_id_header

    # Check session token in cookies
    cookie_header = headers.headers.get("cookie", "")
    cookies = parse_cookies(cookie_header)
    token = cookies.get("__session")

    if not token:
        return None

    payload = decode_jwt_payload(token)
    if not payload:
        return None

    sub = payload.get("sub")
    return sub if isinstance(sub, str) else None


def extract_supabase(headers: Headers) -> Optional[str]:
    """Extract user ID from Supabase authentication."""
    auth = headers.headers.get("authorization", "")
    if not auth or not auth.startswith("Bearer "):
        return None

    token = auth[7:]  # Remove "Bearer "
    payload = decode_jwt_payload(token)
    if not payload:
        return None

    email = payload.get("email")
    return email if isinstance(email, str) else None


async def extract_bearer_jwt(
    headers: Headers,
    jwt_field_cache: Dict[str, str]
) -> Optional[str]:
    """Extract user ID from Bearer JWT authentication."""
    # Try authorization header first
    auth = headers.headers.get("authorization", "")
    x_bearer = headers.headers.get("x-bearer-jwt", "")

    token = None
    if auth and auth.startswith("Bearer "):
        token = auth[7:]
    elif x_bearer and x_bearer.startswith("Bearer "):
        token = x_bearer[7:]
    else:
        # Try cookies
        cookie_header = headers.headers.get("cookie", "")
        cookies = parse_cookies(cookie_header)
        token = cookies.get("session") or cookies.get("access_token")

    if not token:
        return None

    payload = decode_jwt_payload(token)
    if not payload:
        return None

    return await extract_user_from_jwt(payload, jwt_field_cache)


async def call_llm(claims: Dict[str, Any]) -> Optional[str]:
    """Call LLM to identify JWT field containing user identity."""
    if not OPENROUTER_API_KEY:
        return None

    prompt = make_prompt(claims)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
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
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    return None


async def extract_user_from_jwt(
    claims: Dict[str, Any],
    jwt_field_cache: Dict[str, str]
) -> Optional[str]:
    """
    Extract user identifier from JWT claims using LLM and fallback logic.

    Args:
        claims: JWT payload claims
        jwt_field_cache: Cache for field mappings by schema hash

    Returns:
        User identifier string if found, None otherwise
    """
    schema_hash = hash_obj(claims)

    # Check cache first
    if schema_hash in jwt_field_cache:
        field_path = jwt_field_cache[schema_hash]
        value = get_nested_value(claims, field_path) if "." in field_path else claims.get(field_path)
        return str(value) if value is not None else None

    # Try LLM identification
    llm_response = await call_llm(claims)

    if llm_response:
        value = get_nested_value(claims, llm_response) if "." in llm_response else claims.get(llm_response)
        if value is not None:
            jwt_field_cache[schema_hash] = llm_response
            return str(value)

    # Fallback to common fields
    common_fields = [
        "email",
        "user_email",
        "username",
        "user_name",
        "user_id",
        "sub",
        "uid",
        "id",
        "userid",
        "preferred_username",
        "upn",
        "unique_name",
        "user.email",
        "user.username",
        "user.id",
        "profile.email",
        "profile.user.email",
        "profile.user.id",
        "profile.user_id",
        "custom_claims.user_identifier",
    ]

    for field_path in common_fields:
        value = get_nested_value(claims, field_path) if "." in field_path else claims.get(field_path)

        if value is not None and value != "":
            jwt_field_cache[schema_hash] = field_path
            return str(value)

    return None


# Synchronous wrapper for backward compatibility
def extract_user_id_sync(
    request_headers: Dict[str, Union[str, List[str]]],
    request_cookies: Optional[Dict[str, str]] = None,
    jwt_field_cache: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """Synchronous wrapper for extract_user_id."""
    return asyncio.run(extract_user_id(request_headers, request_cookies,jwt_field_cache))


# NOTE: flask and fastapi starlette put the values of fields with the same key together, separated with commas. So multiple values are not in a list like how its expected
# this is fine because the Authorization field can't have duplicates and the services (clerk, supabase) etc put their fields only once always. something to keep in mind