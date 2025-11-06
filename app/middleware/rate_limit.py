import time
import uuid
from typing import Dict, List

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        *,
        window_seconds: int = 60,
        post_limit: int = 10,
        global_limit: int = 1000
    ):
        super().__init__(app)
        self.window = window_seconds
        self.post_limit = post_limit
        self.global_limit = global_limit
        self.store: Dict[str, List[Dict]] = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()

        events = self.store.get(ip, [])
        events = [e for e in events if e["t"] > now - self.window]

        # count POSTs to /api/v1/books
        post_events = [
            e
            for e in events
            if e["method"] == "POST" and e["path"].startswith("/api/v1/books")
        ]
        if request.method == "POST" and request.url.path.startswith("/api/v1/books"):
            if len(post_events) >= self.post_limit:
                retry_after = (
                    int((post_events[0]["t"] + self.window) - now)
                    if post_events
                    else self.window
                )
                correlation_id = str(uuid.uuid4())
                return JSONResponse(
                    status_code=429,
                    content={
                        "type": "https://api.readinglist.com/errors/too-many-requests",
                        "title": "Too Many Requests",
                        "status": 429,
                        "detail": "Rate limit exceeded",
                        "instance": request.url.path,
                        "correlation_id": correlation_id,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    },
                    headers={"Retry-After": str(retry_after)},
                )

        # global check
        if len(events) >= self.global_limit:
            retry_after = (
                int((events[0]["t"] + self.window) - now) if events else self.window
            )
            correlation_id = str(uuid.uuid4())
            return JSONResponse(
                status_code=429,
                content={
                    "type": "https://api.readinglist.com/errors/too-many-requests",
                    "title": "Too Many Requests",
                    "status": 429,
                    "detail": "Rate limit exceeded",
                    "instance": request.url.path,
                    "correlation_id": correlation_id,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                },
                headers={"Retry-After": str(retry_after)},
            )

        events.append({"t": now, "method": request.method, "path": request.url.path})
        self.store[ip] = events

        response = await call_next(request)
        return response
