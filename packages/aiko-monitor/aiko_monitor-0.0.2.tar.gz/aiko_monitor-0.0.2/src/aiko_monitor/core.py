from __future__ import annotations

import base64
import gzip
import hashlib
import hmac
import json
import logging
import os
import queue
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Callable, Dict, Optional

import requests

from .identity import extract_user_id_sync


class _LogfmtFormatter(logging.Formatter):
    _BASE = {
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "name",
        "taskName",  # Exclude taskName from output
    }

    def format(self, record: logging.LogRecord) -> str:
        dt = datetime.fromtimestamp(record.created, timezone.utc)
        ts = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        parts = [
            f"time={ts}",
            f"level={record.levelname}",
            f'msg="{record.getMessage()}"',
        ]

        for k, v in record.__dict__.items():
            if k in self._BASE or k.startswith("_"):
                continue
            parts.append(f"{k}={v}")

        return " ".join(parts)


logger = logging.getLogger("aiko_monitor")
logger.addHandler(logging.NullHandler())
logger.propagate = False

# ---- Error sink (JSONL) that runs after every ERROR log ----
# (will be later changed to send to endpoint instead of jsonl write)
_error_file_lock = Lock()
_error_sink_func = None  # type: Optional[Callable[[dict], None]]
_error_sink_handler_added = False
_error_file_path_default = os.getenv(
    "AIKO_ERROR_LOG_FILE", os.path.join(os.getcwd(), "aiko_errors.log")
)


def _default_error_sink_write_jsonl(event: dict) -> None:
    """Append one JSON object per line to the error sink file.
    Uses a lock to avoid interleaving across threads.
    """
    try:
        with _error_file_lock:
            with open(_error_file_path_default, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
    except Exception:
        # Never raise from logging paths
        pass


def set_error_sink(func: Callable[[dict], None]) -> None:
    """Replace the sink function. Later you can set this to an HTTP sender.
    The function receives a dict with keys like time, level, message, and extras.
    """
    global _error_sink_func
    _error_sink_func = func


class _ErrorSinkHandler(logging.Handler):
    """Logging handler that forwards ERROR+ records to the pluggable sink."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # Build a structured event
            dt = datetime.fromtimestamp(record.created, timezone.utc)
            event = {
                "time": dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "logger": record.name,
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "funcName": record.funcName,
                "lineno": record.lineno,
            }
            # Attach non-base extras similar to _LogfmtFormatter
            extras = {}
            for k, v in record.__dict__.items():
                if k in _LogfmtFormatter._BASE or k.startswith("_"):
                    continue
                extras[k] = v
            if extras:
                event["extra"] = extras
            # Attach traceback if present
            if record.exc_info:
                etype, evalue, etb = record.exc_info
                event["exc_type"] = getattr(etype, "__name__", str(etype))
                event["exc_message"] = str(evalue)
                event["traceback"] = "".join(
                    traceback.format_exception(etype, evalue, etb)
                )
            sink = _error_sink_func or _default_error_sink_write_jsonl
            sink(event)
        except Exception:
            # Sink must never crash logging
            pass


def enable_error_sink() -> None:
    """Attach the error sink handler to both SDK loggers once."""
    global _error_sink_handler_added
    if _error_sink_handler_added:
        return
    h = _ErrorSinkHandler(level=logging.ERROR)
    logger.addHandler(h)
    _error_sink_handler_added = True


def enable_logfmt(
    *, level: int = logging.ERROR, stream=sys.stderr, file: str = ""
) -> None:
    """Attach a logfmt handler.
    Guarded by AIKO_ALLOW_LOGFMT to avoid accidental console noise in client apps.
    Set AIKO_ALLOW_LOGFMT=1 to allow; otherwise this is a no-op.
    """
    allow = os.getenv("AIKO_ALLOW_LOGFMT", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if not allow:
        return
    if file:
        handler = logging.FileHandler(file)
    else:
        handler = logging.StreamHandler(stream)
    handler.setFormatter(_LogfmtFormatter())
    logger.addHandler(handler)
    logger.setLevel(level)


# Attach error sink by default (writes to AIKO_ERROR_LOG_FILE or ./aiko_errors.log)
enable_error_sink()


_DEFAULT_ENDPOINT = os.getenv("AIKO_MONITOR_ENDPOINT", "http://localhost:8080/monitor")


def _b64_urlsafe_decode(data: str) -> bytes:
    # pad correctly (0–3 extra '=' depending on length)
    return base64.urlsafe_b64decode(data + ("=" * (-len(data) % 4)))


def _sign(secret: bytes, data: bytes) -> str:
    mac = hmac.new(secret, data, hashlib.sha256)
    return mac.hexdigest()


def safe_execute(func: Callable) -> Callable:
    """
    Decorator to ensure monitoring code NEVER breaks user requests.
    Catches all exceptions, logs them, and returns safely without raising.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            extra = {
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys()) if kwargs else [],
            }

            if hasattr(e, "_monitoring_context"):
                extra.update(e._monitoring_context)

            # Log the error with full context but DON'T re-raise
            logger.error(
                f"Monitoring error in {func.__name__}: {str(e)}",
                exc_info=True,  # This includes the full stack trace
                extra=extra,
            )
            # Return None or some safe default
            return None

    return wrapper


@contextmanager
def safe_execute_context(block_name: str = "anonymous"):
    try:
        yield
    except Exception as e:
        logger.error(
            f"Monitoring error in block '{block_name}': {str(e)}", exc_info=True
        )


class _HTTPTransport:
    def __init__(
        self,
        endpoint: str,
        secret_key: str,
        project_key: str,
    ) -> None:
        self.endpoint = endpoint
        try:
            self.secret = _b64_urlsafe_decode(secret_key)
        except Exception:
            # Fallback: treat provided secret as raw text
            self.secret = secret_key.encode()
        self.project_key = project_key
        self._queue: "queue.SimpleQueue[dict]" = queue.SimpleQueue()
        # start healthy; _flush() may flip this to False on repeated failures
        self._backend_healthy = True
        self._health_lock = threading.Lock()
        self._health_checker_running = False
        # Start worker threads
        self._worker = threading.Thread(
            target=self._run, daemon=True, name="aiko-worker"
        )
        self._worker.start()

        # jwt cache.
        # currently held in memory. it might be lost in serverless envs or should be filled multiple times in many workers scenarios
        # this still means ~2 llm calls per fresh cache. nothing to worry about
        self._jwt_cache = {}

        # Reuse TCP/TLS connections for lower latency/CPU
        self._session = requests.Session()

    def send(self, payload: Dict[str, Any]) -> None:
        if not self._backend_healthy:
            logger.debug(
                "backend_unhealthy_drop",
                extra={"endpoint": payload.get("endpoint", "unknown")},
            )
            return
        logger.debug(
            "queue_put",
            extra={
                "endpoint": payload.get("endpoint", "unknown"),
                "queue_size": self._queue.qsize(),
            },
        )
        self._queue.put(payload)

    def _run(self) -> None:
        total_processed = 0
        while True:
            try:
                # If backend is unhealthy, pause consumption so we don't drop queued items
                if not self._backend_healthy:
                    time.sleep(0.5)
                    continue

                item = self._queue.get(timeout=5.0)
                logger.debug(
                    "queue_get",
                    extra={
                        "endpoint": item.get("endpoint", "unknown"),
                        "total_processed": total_processed,
                    },
                )

                total_processed += 1

                try:
                    # check if the cache is filled
                    headers = ((item or {}).get("request") or {}).get("headers", {})
                    logger.debug(f"headers : {headers}")
                    logger.debug(f"jwt_cache:{self._jwt_cache}")

                    identity = extract_user_id_sync(
                        request_headers=headers, jwt_field_cache=self._jwt_cache
                    )

                    logger.debug(f"identity extracted: {identity}")
                except Exception:
                    identity = None
                    logger.error(
                        "extract_user_id_sync failed",
                        exc_info=True,
                        extra={
                            "reqresp": item,
                            "header_count": len(headers)
                            if isinstance(headers, dict)
                            else 0,
                        },
                    )

                # old user_id format is now extracted_user
                item["user_id"] = identity if identity is not None else "unknown"

                # Try to send to backend; no persistence wired yet
                if not self._flush(item):
                    logger.warning(
                        "flush_failed_no_persistence",
                        extra={"endpoint": item.get("endpoint", "unknown")},
                    )

            except queue.Empty:
                continue

            except Exception:
                logger.error("worker_loop_error", exc_info=True)
                continue

    def _mark_unhealthy_and_probe(self):
        if self._backend_healthy:
            self._backend_healthy = False
        # start checker if not already running
        with self._health_lock:
            if self._health_checker_running:
                return
            self._health_checker_running = True
        t = threading.Thread(
            target=self._health_check_loop, name="aiko-health", daemon=True
        )
        t.start()

    def _health_check_loop(self):
        """Periodically probe the backend and flip healthy flag when reachable.
        Drops are already happening while unhealthy; this only determines when to resume.
        """
        backoff = 1.0  # seconds
        max_backoff = 60.0
        endpoint = self.endpoint
        while not self._backend_healthy:
            ok = self._probe_backend(endpoint)
            if ok:
                logger.debug("backend_recovered", extra={"endpoint": endpoint})
                self._backend_healthy = True
                with self._health_lock:
                    self._health_checker_running = False
                return
            time.sleep(backoff)
            backoff = min(max_backoff, backoff * 2)
        # If became healthy elsewhere, ensure flag is reset
        with self._health_lock:
            self._health_checker_running = False

    def _probe_backend(self, endpoint: str) -> bool:
        """Consider backend up if TCP/HTTP is reachable and not a hard 5xx.
        We accept 200-499 as 'reachable' (405/404 are fine for HEAD/GET).
        """
        try:
            # Prefer a lightweight HEAD; some servers may 405 it, which is fine
            r = self._session.head(endpoint, timeout=1)
            if 200 <= r.status_code < 500:
                return True
        except Exception:
            pass
        try:
            # Fallback to GET
            r = self._session.get(endpoint, timeout=1)
            if 200 <= r.status_code < 500:
                return True
        except Exception:
            return False
        return False

    def _flush(self, item: Dict):
        # flushing a single item to backend. returns true if success
        endpoints = item.get("endpoint", "unknown")
        logger.debug("flush_start", extra={"endpoint": endpoints})
        json_body = json.dumps(item, default=str).encode()
        body = gzip.compress(json_body)
        sig = _sign(
            self.secret, body
        )  # project key, signature, Authorization, Bearer token
        headers = {
            "Content-Type": "application/json",
            "Content-Encoding": "gzip",
            "X-Project-Key": self.project_key,
            "X-Signature": sig,
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self._session.post(
                    self.endpoint, data=body, headers=headers, timeout=2
                )
                response.raise_for_status()
                logger.debug(
                    "http_post_success", extra={"status": response.status_code}
                )
                return True  # Success, exit retry loop
            except Exception as exc:
                logger.warning(
                    "http_post_failed",
                    extra={"attempt": attempt + 1, "error": str(exc)},
                )
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(
                        "last_flush_try_failed",
                        extra={
                            "reqresp": item,
                            "max_attempts_reached": True,
                        },
                    )
                    self._mark_unhealthy_and_probe()
                    return False
                time.sleep(0.1 * (2**attempt))


class Monitor:
    _singleton: Optional["Monitor"] = None

    @classmethod
    @safe_execute
    def init(
        cls,
        *,
        project_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        endpoint: str = _DEFAULT_ENDPOINT,
        openrouter_api_key: Optional[str] = None,
    ) -> "Monitor":
        if cls._singleton is not None:
            return cls._singleton
        project_key = project_key or os.getenv("AIKO_PROJECT_KEY", "demo_project")
        secret_key = secret_key or os.getenv("AIKO_SECRET_KEY", "demo_secret")
        openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY", "")

        # Set the API key for identity module if provided
        if openrouter_api_key:
            os.environ["OPENROUTER_API_KEY"] = openrouter_api_key

        monitor = cls(project_key=project_key, secret_key=secret_key, endpoint=endpoint)
        cls._singleton = monitor
        return monitor

    @classmethod
    def auto(cls):
        mon = cls.init()
        from .integrations import requests as _requests_integ

        _requests_integ.instrument(mon)
        return mon

    def __init__(
        self,
        app=None,
        *,
        project_key: str,
        secret_key: str,
        endpoint: str = _DEFAULT_ENDPOINT,
    ):
        self.project_key = project_key
        self.secret_key = secret_key

        self._transport = _HTTPTransport(endpoint, secret_key, project_key)

        if app is not None:
            self._auto_instrument(app)

    @contextmanager
    def capture_http_call(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        url: str = "",
    ):
        # timestamp would be good to have as well but its not used currently
        start_perf = time.perf_counter()  # this and latency are the app req/resp latency, identity and flush are not counted because they don't slow down the app
        req_meta: Dict[str, Any] = {
            "url": url,
            "method": None,
            "latency_ms": 0,
            "request_headers": {},
            "request_body": {},
            "status": None,
            "response_headers": {},
            "response_body": {},
            "endpoint": url,  # can be overwritten by caller
        }
        try:
            yield req_meta
        finally:
            computed_latency_ms = int((time.perf_counter() - start_perf) * 1000)
            # payload = {
            #     "user_id": user_id if user_id is not None else "unknown",
            #     "endpoint": req_meta["endpoint"],
            #     "latency_ms": computed_latency_ms,
            #     "request": {
            #         "method": req_meta["method"],
            #         "url": req_meta["url"],
            #         "headers": req_meta["request_headers"],
            #         "body": req_meta["request_body"],
            #     },
            #     "response": {
            #         "status": req_meta["status"],
            #         "headers": req_meta["response_headers"],
            #         "body": req_meta["response_body"],
            #     },
            # }
            # legacy format
            payload = {
                "endpoint": req_meta["endpoint"],
                "method": req_meta["method"],
                "status_code": req_meta["status"],
                "request_headers": req_meta["request_headers"],
                "request_body": req_meta["request_body"],
                "response_headers": req_meta["response_headers"],
                "response_body": req_meta["response_body"],
                "duration_ms": computed_latency_ms,
                "url": req_meta["url"],
                "extracted_user": user_id if user_id is not None else "unknown",
            }

            logger.debug(
                "payload_created",
                extra={"endpoint": req_meta["endpoint"], "status": req_meta["status"]},
            )
            self._transport.send(payload)

    def _auto_instrument(self, app) -> None:
        try:
            app_type = type(app).__name__
            module_name = type(app).__module__
            logger.debug(
                "auto instrumenting",
                extra={"app_type": app_type, "module_name": module_name},
            )
            # framework auto_instrument is gonna need to detect deploy server to use the appropriate wrapper for asgi/wsgi middleware if used
            if app_type == "FastAPI":
                from .integrations.fastapi import instrument

                instrument(app, self)
            elif app_type == "Flask":
                from .integrations.flask_final import instrument

                instrument(app, self)
            else:
                logger.error(
                    "unsupported app type",
                    extra={"app_type": app_type, "module_name": module_name},
                )
        except ImportError as e:
            logger.error(f"Missing integration: {e}")
        except Exception as e:
            # Internal error - debug for me, silent for user
            logger.error(f"Instrumentation failed: {e}", exc_info=True)


init = Monitor.init

auto = Monitor.auto
