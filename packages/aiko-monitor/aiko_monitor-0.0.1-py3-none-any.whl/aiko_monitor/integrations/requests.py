from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:  # pragma: no cover
    from ..core import Monitor


_PATCHED_ATTR = "__aiko_patched__"


def instrument(monitor: "Monitor") -> None:
    if getattr(requests, _PATCHED_ATTR, False):
        return

    original = requests.Session.request

    @functools.wraps(original)
    def wrapped(session, method, url, **kwargs):  # type: ignore[override]
        user_id = kwargs.pop("aiko_user_id", "unknown")
        session_id = kwargs.pop("aiko_session_id", "unknown")
        with monitor.capture_http_call(user_id, session_id, url):
            return original(session, method, url, **kwargs)

    requests.Session.request = wrapped  # type: ignore[assignment]
    setattr(requests, _PATCHED_ATTR, True)
