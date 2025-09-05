from __future__ import annotations
import json
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..core import logger
if TYPE_CHECKING:  # pragma: no cover
    from ..core import Monitor

MAX_RESP_BODY_BYTES = 1024 * 1024  # 1MB limit


class AikoMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, monitor: "Monitor"):
        super().__init__(app)
        self.monitor = monitor

    async def _get_response_bytes(self, response: Response) -> bytes:
        """
        Buffer the response body from the iterator and replay it.

        Works for both StreamingResponse and standard Response.
        Do not modify headers like Content-Length; Starlette/Uvicorn handle it.
        """
        # Read exactly what will be sent
        chunks: list[bytes] = [chunk async for chunk in response.body_iterator]
        body_bytes = b"".join(chunks)

        # Replay so the client still receives the body
        async def _repeat_body():
            for chunk in chunks:
                yield chunk

        response.body_iterator = _repeat_body()
        return body_bytes

    async def dispatch(self, request: Request, call_next):
        req_meta = None
        try:
            
            aiko_context = self.monitor.capture_http_call(url=str(request.url))
            req_meta = aiko_context.__enter__()
            if req_meta is not None:
                req_meta["method"] = request.method
                req_meta["request_headers"] = dict(request.headers)
                req_meta["endpoint"] = request.url.path
            
                try:
                    req_meta["request_body"] = await request.json()
                except Exception:
                    req_meta["request_body"] = {}
        except Exception as monitoring_error:
            # Log but don't fail yet
            logger.error(
                f"Monitoring setup failed: {monitoring_error}",
                exc_info=True,
                extra={"url": str(request.url), "method": request.method},
            )
        
        # now call the application
        try:
            response: Response = await call_next(request)
        except Exception as e:
            try:
                aiko_context.__exit__(None, None, None)
            except NameError:
                pass # aiko context was never created, that's fine
            raise e # app error let it raise
        
        # success case - response returned
        if req_meta is not None:
            try:
                req_meta["status"] = response.status_code

                body_bytes = await self._get_response_bytes(response)
                body_bytes = body_bytes[:MAX_RESP_BODY_BYTES]  # truncate for logging
                # capture headers after potential content-length adjustment
                req_meta["response_headers"] = dict(response.headers)

                ctype = response.headers.get("content-type", "").lower()
                try:
                    if "application/json" in ctype:
                        req_meta["response_body"] = json.loads(
                            body_bytes.decode("utf-8", errors="replace")
                        )
                    else:
                        req_meta["response_body"] = body_bytes.decode("utf-8", errors="replace")
                except Exception:
                    req_meta["response_body"] = body_bytes.decode("utf-8", errors="replace")
            
                req_meta["success"] = True
            except Exception as response_monitoring_error:
                req_meta["status"] = 500
                logger.error(
                    f"Response monitoring failed: {response_monitoring_error}",
                    exc_info=True,
                    extra={
                        "reqresp": req_meta
                    },
                )

        try:
            aiko_context.__exit__(None, None, None)
        except NameError:
            pass
        return response
                    

def instrument(app, monitor: "Monitor") -> None:
    app.add_middleware(AikoMiddleware, monitor=monitor)
