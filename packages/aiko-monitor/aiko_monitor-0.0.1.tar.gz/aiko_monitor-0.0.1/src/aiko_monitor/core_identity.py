"""
Core identity detection functions - pure with no side effects following the node structure
This is meant to be used with the wsgi environ dict. No point dealing with framework specific req objects if the headers are in environ.
"""

from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
import json
import base64


@dataclass
class Headers:
    """Normalized headers and cookies."""
    headers: Dict[str, str]
    cookies: Dict[str, str]


@dataclass
class ProviderInfo:
    """Information about detected authentication provider."""
    provider: str  # "bearer-jwt" | "clerk" | "supabase" | "authjs" | "betterauth" | "custom"
    type: str     # "jwt" | "cookie" | "opaque"


def has(obj: Dict[str, str], *keys: str) -> bool:
    """Check if any of the keys exist in the object."""
    return any(k in obj for k in keys)


def parse_headers(request_headers: Dict[str, Union[str, List[str]]], 
                 request_cookies: Optional[Dict[str, str]] = None) -> Headers:
    """
    Parse and normalize request headers and cookies.
    
    Args:
        request_headers: Raw headers dict (values can be str or List[str])
        request_cookies: Optional cookies dict
        
    Returns:
        Headers object with normalized headers and cookies
    """
    normalized_headers = {}
    
    for key, value in request_headers.items():
        normalized_key = key.lower()
        if isinstance(value, list):
            normalized_value = str(value[0]) if value else ""
        else:
            normalized_value = str(value or "")
        normalized_headers[normalized_key] = normalized_value
    
    cookies = request_cookies or {}
    
    return Headers(
        headers=normalized_headers,
        cookies=cookies
    )


def is_bearer_jwt(r: Headers) -> bool:
    """Detect if request uses Bearer JWT authentication."""
    # Check authorization headers
    auth_header = r.headers.get("authorization", "")
    x_bearer_header = r.headers.get("x-bearer-jwt", "")
    
    if auth_header.startswith("Bearer ") or x_bearer_header.startswith("Bearer "):
        return True
    
    # Check cookies for session or access_token
    cookie_header = r.headers.get("cookie", "")
    cookies = parse_cookies(cookie_header)
    
    return bool(cookies.get("session") or cookies.get("access_token"))


def is_clerk(r: Headers) -> bool:
    """Detect if request uses Clerk authentication."""
    cookie_header = r.headers.get("cookie", "")
    has_clerk_cookies = "__clerk_db_jwt=" in cookie_header
    
    return (
        has_clerk_cookies or
        has(r.cookies, "__session", "__client_uat", "__clerk_db_jwt") or
        "x-clerk-user-id" in r.headers
    )


def is_supabase(r: Headers) -> bool:
    """
    Detect if request uses Supabase authentication.
    
    Note: This checks for Supabase JWT issuer in the token.
    In a pure function version, we do basic JWT parsing without external libs.
    """
    auth = r.headers.get("authorization", "")
    if not auth or not auth.startswith("Bearer "):
        return False
    
    try:
        token = auth[7:]  # Remove "Bearer "
        # Basic JWT parsing - split by dots and decode payload
        parts = token.split(".")
        if len(parts) != 3:
            return False
            
        # Decode payload (add padding if needed)
        payload_part = parts[1]
        # Add padding for base64 decoding
        payload_part += "=" * (-len(payload_part) % 4)
        
        payload_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(payload_bytes.decode())
        
        iss = payload.get("iss", "")
        return isinstance(iss, str) and "supabase.co" in iss
        
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return False


def is_authjs(r: Headers) -> bool:
    """Detect if request uses AuthJS authentication."""
    cookie_header = r.headers.get("cookie", "")
    return "authjs.session-token=" in cookie_header


def is_better_auth(r: Headers) -> bool:
    """Detect if request uses Better Auth authentication."""
    cookie_header = r.headers.get("cookie", "")
    return "better-auth.session_token=" in cookie_header


# Provider detection table
PROVIDER_TABLE: List[Tuple[str, callable, str]] = [
    ("supabase", is_supabase, "jwt"),
    ("authjs", is_authjs, "cookie"),
    ("betterauth", is_better_auth, "cookie"),
    ("bearer-jwt", is_bearer_jwt, "jwt"),
    ("clerk", is_clerk, "jwt"),
]


def detect_provider(r: Headers) -> ProviderInfo:
    """
    Detect authentication provider from request headers.
    
    Args:
        r: Normalized headers object
        
    Returns:
        ProviderInfo with provider name and type
    """
    for provider_name, detection_fn, provider_type in PROVIDER_TABLE:
        if detection_fn(r):
            return ProviderInfo(provider=provider_name, type=provider_type)
    
    return ProviderInfo(provider="custom", type="opaque")


def parse_cookies(cookie_header: str = "") -> Dict[str, str]:
    """
    Parse cookie header string into key-value pairs.
    
    Args:
        cookie_header: Cookie header string (e.g., "key1=value1; key2=value2")
        
    Returns:
        Dictionary of cookie key-value pairs
    """
    if not cookie_header:
        return {}
    
    cookies = {}
    for cookie in cookie_header.split(";"):
        cookie = cookie.strip()
        if "=" in cookie:
            key, value = cookie.split("=", 1)
            if key and value:
                cookies[key] = value
    
    return cookies


def extract_clerk_user_id(headers: Headers) -> Optional[str]:
    """
    Extract user ID from Clerk authentication (pure function version).
    
    Args:
        headers: Normalized headers object
        
    Returns:
        User ID string if found, None otherwise
    """
    # Check for direct user ID header
    user_id_header = headers.headers.get("x-clerk-user-id")
    if user_id_header:
        return user_id_header
    
    # Check session token in cookies
    session_token = headers.cookies.get("__session")
    if not session_token:
        return None
    
    try:
        # Basic JWT parsing - split by dots and decode payload
        parts = session_token.split(".")
        if len(parts) != 3:
            return None
            
        # Decode payload (add padding if needed)
        payload_part = parts[1]
        payload_part += "=" * (-len(payload_part) % 4)
        
        payload_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(payload_bytes.decode())
        
        sub = payload.get("sub")
        return sub if isinstance(sub, str) else None
        
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None