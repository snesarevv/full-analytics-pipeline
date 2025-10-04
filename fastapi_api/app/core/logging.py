import logging
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import time


def setup_logging():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.EventRenamer("message"),
            structlog.processors.JSONRenderer(),
        ]
    )


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        logger = structlog.get_logger().bind(
            request_id=req_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        logger.info("http_request")
        response.headers["X-Request-Id"] = req_id
        return response
