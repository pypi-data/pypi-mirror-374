from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

from flask import Flask, request
from flask.signals import (
    got_request_exception,
    request_finished,
    request_started,
)

from ..core import _session_context, _user_context, logger, safe_execute, safe_execute_context
from ..identity import extract_identity

if TYPE_CHECKING:
    from ..core import Monitor

MAX_RESP_BODY_BYTES = 1024 * 1024  # 1MB limit


class SentryWsgiMiddleware:
    """WSGI middleware that always creates a transaction using environ for data sharing."""
    
    def __init__(self, app, monitor: "Monitor"):
        self.app = app
        self.monitor = monitor

    def __call__(self, environ, start_response):
        try:
            # Always create WSGI-level transaction
            start_time = time.time()

            # Create monitoring context and store in environ (we only use environ now because its available in both wsgi and inside frameworks)
            aiko_wsgi_context = self.monitor.capture_http_call(
                user_id=None, 
                session_id="unknown",  # No sessions 
            )
            aiko_wsgi_meta = aiko_wsgi_context.__enter__()
            
            # Store everything in environ instead of g
            environ['_aiko_wsgi_context'] = aiko_wsgi_context
            environ['_aiko_wsgi_meta'] = aiko_wsgi_meta
            
            # url is always reconstructed for reliability. in signal exceptions that happen midway we might get the related data needed for reconstruction in inconsistent state, therefore generating an odd URL thats gonna trigger alerts for no reason.
            # if the related fields needed for reconstruction are not changed during flask lifecycle then it's fine but perf diff should negligible anyway.
            aiko_wsgi_meta["url"] = self.reconstruct_url_from_environ(environ)
            aiko_wsgi_meta["method"] = environ.get("REQUEST_METHOD", "GET").upper()
            aiko_wsgi_meta["endpoint"] = environ.get("PATH_INFO")
            aiko_wsgi_meta["request_headers"] = self._extract_request_headers(environ)
            # req/resp body is hard or expensive to parse in wsgi, either the flask ones are used or none
            
            
            def new_start_response(status, response_headers, exc_info=None):
                with safe_execute_context("wsgi_result_write"):
                    aiko_wsgi_meta["response_headers"] = dict(response_headers)
                    aiko_wsgi_meta["status"] = int(status.split()[0]) or "unknown"

                    #if not aiko_wsgi_meta.get("request_headers"):
                    #    logger.warning(f"SIGNALS DIDNT GIVE request_headers")
                    #    aiko_wsgi_meta["request_headers"] = self._extract_request_headers(environ)
                    
                    aiko_wsgi_meta["latency_ms"] = int((time.time() - start_time) * 1000)
                    return start_response(status, response_headers, exc_info)

            try:
                result = self.app(environ, new_start_response)
            except Exception as flask_exception:
                try:
                    # Capture exception in WSGI transaction
                    aiko_wsgi_meta["status"] = 500
                    aiko_wsgi_meta["latency_ms"] = int((time.time() - start_time) * 1000)

                    aiko_wsgi_context.__exit__(type(flask_exception), flask_exception, flask_exception.__traceback__)
                except Exception:
                    logger.error("monitoring_exit_failed", exc_info=True)
                raise flask_exception
            
            try:
                aiko_wsgi_context.__exit__(None, None, None)
            except Exception:
                logger.error("monitoring_exit_failed", exc_info=True)
            
            return result    
        
        except Exception as e:
            logger.error("wsgi_middleware_failed", exc_info=True, extra={
            "error": str(e),
            "environ_path": environ.get("PATH_INFO", "unknown")
            })
            # Fail silently: Close context if open, and call original app directly
            if 'aiko_wsgi_context' in locals():  # Check if initialized
                aiko_wsgi_context.__exit__(type(e), e, e.__traceback__)
            # Return original app response to avoid crashing
            return self.app(environ, start_response)
        
    def reconstruct_url_from_environ(self, environ):
        try:
            scheme = environ.get("wsgi.url_scheme", "http")  
            host = environ.get("SERVER_NAME", "unknown")  
            port = environ.get("SERVER_PORT", "")
            path = environ.get("PATH_INFO", "")  
            query = environ.get("QUERY_STRING", "") 
            # Reconstruct (simple f-string)
            url = f"{scheme}://{host}"
            if port:
                url += f":{port}"
            url += path
            if query:
                url += f"?{query}"
            return url
        except Exception:
            return ""  

    def _extract_request_headers(self, environ):
        """Extract HTTP headers from WSGI environ to match Flask format exactly."""
        headers = {}
        for key in environ:
            if key.startswith("HTTP_"):
                name = key[5:].replace("_", "-").title()
                headers[name] = environ[key]
            # Special (no prefix)
            if key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                headers[key.replace("_", "-").title()] = environ[key]
        return headers  # Partial if keys missing (e.g., empty dict OK)

@safe_execute
def _handle_request_start(sender, **kwargs):
    """Handle Flask request_started signal"""
    logger.debug("FLASK-SIGNAL HANDLE_REQUEST_START", extra={"method": request.method, "path": request.path})
    
    # Get monitoring data from environ
    aiko_wsgi_meta = request.environ.get('_aiko_wsgi_meta')
    if not aiko_wsgi_meta:
        logger.error("no_wsgi_meta_in_flask_signal", extra={"path": request.path})
        return
    
    # Extract identity only in Flask signals 
    # TODO extract_identity can be moved on the wsgi layer (since we only use header)
    identity = extract_identity(request)
    user_id = identity.user_id or "unknown"
    session_id = "unknown"  # TODO: extract session from JWT or generate (currently not sent by the capture_http_call payload)
    
    _user_context.set(user_id)
    _session_context.set(session_id) 
    
    # Enhance the existing WSGI transaction with Flask data
    aiko_wsgi_meta["url"] = request.url
    
    if dict(request.headers):
        aiko_wsgi_meta["request_headers"] = dict(request.headers)  # Cleaner than WSGI

    request_body = request.get_json(silent=True) or {}
    if request_body is not None:
        aiko_wsgi_meta["request_body"] = request_body or {}
    
@safe_execute
def _handle_request_finish(sender, response, **kwargs):
    """Handle Flask request_finished signal - enhance WSGI transaction with response."""
    # Get monitoring data from environ
    aiko_wsgi_meta = request.environ.get('_aiko_wsgi_meta')
    
    if aiko_wsgi_meta:
        logger.debug("FLASK-SIGNAL HANDLE_REQUEST_FINISH", extra={
            "method": request.method, 
            "path": request.path, 
            "status": response.status_code
        })
        
        # Enhance WSGI transaction with rich Flask response data
        aiko_wsgi_meta["response_headers"] = dict(response.headers)
        
        # Handle response body
        if response.direct_passthrough:
            aiko_wsgi_meta["response_body"] = f"<streamed response: {response.mimetype}>"
        else:
            raw = response.get_data()[:MAX_RESP_BODY_BYTES]
            if response.is_json:
                try:
                    aiko_wsgi_meta["response_body"] = json.loads(raw)
                except Exception:
                    aiko_wsgi_meta["response_body"] = raw.decode(errors="replace")
            else:
                aiko_wsgi_meta["response_body"] = raw.decode(errors="replace")
        
        logger.debug("FLASK-SIGNAL REQUEST_FINISH OK", extra={
            "path": request.path, 
            "latency_ms": aiko_wsgi_meta.get('latency_ms', 0)
        })
    else:
        logger.warning("FLASK-SIGNAL REQUEST_FINISH NO AIKO_WSGI_META", extra={
            "method": request.method, 
            "path": request.path
        })

def instrument(app: Flask, monitor: "Monitor") -> None:
    """Instrument Flask app with always-on WSGI transactions + Flask enhancement."""
    # Store monitor in app config for signal handlers
    app.config['_aiko_monitor'] = monitor
    
    app.wsgi_app = SentryWsgiMiddleware(app.wsgi_app, monitor)
    
    request_started.connect(_handle_request_start, app)
    request_finished.connect(_handle_request_finish, app)
   # got_request_exception.connect(_handle_exception, app) not used rn
    
    logger.info("flask_instrumentation_complete", extra={"app_name": app.name})