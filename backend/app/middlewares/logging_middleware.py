"""Logging middleware for the application."""

import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests and responses."""

    def __init__(self, app: ASGIApp, logger=None):
        super().__init__(app)
        self.logger = logger or get_logger(__name__)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        self.logger.info("=== INCOMING REQUEST ===")
        self.logger.info("Method: %s", request.method)
        self.logger.info("URL: %s", request.url)
        self.logger.info("Path: %s", request.url.path)
        self.logger.info("Query Params: %s", dict(request.query_params))

        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            self.logger.info("=== OUTGOING RESPONSE ===")
            self.logger.info("Status Code: %s", response.status_code)
            self.logger.info("Process Time: %.4fs", process_time)
            self.logger.info("=== END RESPONSE ===")
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            self.logger.error("=== REQUEST ERROR ===")
            self.logger.error("Error Type: %s", type(exc).__name__)
            self.logger.error("Error Message: %s", str(exc))
            self.logger.error("Process Time: %.4fs", process_time)
            self.logger.error("=== END ERROR ===")
            raise exc
