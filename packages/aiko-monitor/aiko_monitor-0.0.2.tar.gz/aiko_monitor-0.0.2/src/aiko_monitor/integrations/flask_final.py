from __future__ import annotations

import json
from typing import TYPE_CHECKING
from flask.signals import request_started, request_finished, request_tearing_down, got_request_exception
from flask import g, request

from ..core import safe_execute, logger

if TYPE_CHECKING:
    from ..core import Monitor

MAX_RESP_BODY_BYTES = 1024 * 1024  # 1MB limit


def _on_request_started(sender, **kwargs):
    try:
        monitor = sender.config['_aiko_monitor']

        g._aiko_context = monitor.capture_http_call(url=request.url)
        g._aiko_req_meta = g._aiko_context.__enter__()
        
        if g._aiko_context is None or g._aiko_req_meta is None:
            g._aiko_monitoring_failed = True
            logger.error("capture_http_call failed, signals stopped")
            return

        g._aiko_req_meta["method"] = request.method
        g._aiko_req_meta["request_headers"] = dict(request.headers)
        g._aiko_req_meta["request_body"] = request.get_json(silent=True) or {}
        g._aiko_req_meta["endpoint"] = request.path
        
    except Exception as e:
        g._aiko_monitoring_failed = True
        _monitoring_context = {
            "has_request_object": request is not None,
            "has_g_meta": hasattr(g, "_aiko_req_meta"),
        }
        
        extra={
            "kwargs_keys": list(kwargs.keys()) if kwargs else [],
        }
        
        extra.update(_monitoring_context) # kept for consistency
        
        # Log the error with full context but DON'T re-raise
        logger.error(
            f"Monitoring error in _on_request_started: {str(e)}", 
            exc_info=True,  # This includes the full stack trace
            extra=extra
        )

def _on_request_finished(sender, response, **kwargs):
    
    if getattr(g, '_aiko_monitoring_failed', False):
        return response  # Skip monitoring, just return response
    
    try:
        monitor = sender.config['_aiko_monitor']
        g._aiko_req_meta["status"] = response.status_code
        g._aiko_req_meta["response_headers"] = dict(response.headers)

        if response.direct_passthrough:
            g._aiko_req_meta["response_body"] = (
                f"<streamed response: {response.mimetype}>"
            )
        else:
            raw = response.get_data()[:MAX_RESP_BODY_BYTES]
            text = raw.decode(errors="replace")
            if response.is_json:
                try:
                    g._aiko_req_meta["response_body"] = json.loads(text)
                except Exception:
                    g._aiko_req_meta["response_body"] = text
            else:
                g._aiko_req_meta["response_body"] = text
    
    except Exception as e:
        _monitoring_context = {
            "has_request_object": request is not None,
            "has_response_object": response is not None,
            "has_g_meta": hasattr(g, "_aiko_req_meta"),
        }
        
        extra={}
        
        extra.update(_monitoring_context) # kept for consistency
        
        # Log the error with full context but DON'T re-raise
        logger.error(
            f"Monitoring error in _on_request_finished: {str(e)}", 
            exc_info=True,  # This includes the full stack trace
            extra=extra
        )
    
    return response # always return the response no matter what happens

def _on_request_teardown(sender, exc=None, **kwargs):
    if getattr(g, '_aiko_monitoring_failed', False):
        return # skip monitoring

    ctx = getattr(g, "_aiko_context", None)
    if ctx is not None:
        ctx.__exit__(None, None, None)
            


def instrument(app, monitor: "Monitor") -> None:    
    
    app.config['_aiko_monitor'] = monitor
    
    request_started.connect(_on_request_started, app)
    request_finished.connect(_on_request_finished, app)
    #got_request_exception.connect(_on_request_exception, app)
    request_tearing_down.connect(_on_request_teardown, app)
    
    logger.debug("flask_instrumentation_complete", extra={"app_name": app.name})