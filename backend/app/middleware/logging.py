"""Structured logging and request ID middleware."""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("sasis")
logger.setLevel(logging.INFO)

# JSON-like formatting for production
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    "%(asctime)s  %(levelname)-5s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
))
logger.addHandler(_handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with duration and status."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start = datetime.now(timezone.utc)

        logger.info(
            "req=%s  %s %s  client=%s",
            request_id, request.method, request.url.path,
            request.client.host if request.client else "?",
        )

        try:
            response: Response = await call_next(request)
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            logger.info(
                "req=%s  -> %s  %.3fs",
                request_id, response.status_code, duration,
            )
            return response
        except Exception as exc:
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            logger.exception(
                "req=%s  unhandled: %s  %.3fs",
                request_id, exc, duration,
            )
            raise
