from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit maximum request body size in bytes.
    If exceeded — returns 413 Payload Too Large.
    """

    def __init__(self, app, *, max_body_size: int = 1_000_000):
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            if body and len(body) > self.max_body_size:
                return JSONResponse(
                    status_code=413,
                    content={
                        "type": "https://api.readinglist.com/errors/payload-too-large",
                        "title": "Payload Too Large",
                        "status": 413,
                        "detail": "Request payload is too large",
                        "instance": request.url.path,
                    },
                )

            async def receive():
                return {"type": "http.request", "body": body}

            request._receive = receive

        return await call_next(request)
