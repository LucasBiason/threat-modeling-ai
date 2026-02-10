"""Exception handling middleware."""

import datetime
import json
import traceback
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class CatchExceptionsMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions in the FastAPI application."""

    def __init__(
        self,
        app: ASGIApp,
        logger=None,
        pass_through: (
            tuple[tuple[type[Exception], int, Callable[[Exception], dict]], ...] | None
        ) = None,
    ):
        super().__init__(app)
        from threat_modeling_shared.logging import get_logger

        self.logger = logger or get_logger(__name__)
        self.pass_through = pass_through or ()

    def safe_serialize(self, obj: Any) -> Any:
        """Safely serialize objects for JSON response."""
        if hasattr(obj, "__dict__"):
            try:
                return {k: self.safe_serialize(v) for k, v in obj.__dict__.items()}
            except Exception:
                return str(obj)
        elif isinstance(obj, (list, tuple)):
            return [self.safe_serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self.safe_serialize(v) for k, v in obj.items()}
        else:
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            response = await call_next(request)
            return response
        except ResponseValidationError as exc:
            self.logger.error(
                "Validation Error on %s %s: %s",
                request.method,
                request.url.path,
                exc.errors(),
            )
            error_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
            return self._create_error_response(
                status_code=422,
                content={
                    "detail": "Validation Error",
                    "errors": exc.errors(),
                    "timestamp": error_time,
                },
            )
        except Exception as exc:
            for exc_cls, status_code, content_builder in self.pass_through:
                if isinstance(exc, exc_cls):
                    return self._create_error_response(
                        status_code=status_code,
                        content=content_builder(exc),
                    )
            error_traceback = traceback.format_exc()
            error_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

            self.logger.error("=== EXCEPTION DETAILS ===")
            self.logger.error("Request: %s %s", request.method, request.url.path)
            self.logger.error("Exception Type: %s", type(exc).__name__)
            self.logger.error("Exception Message: %s", str(exc))
            self.logger.error("Timestamp: %s", error_time)
            self.logger.error("Full Traceback: %s", error_traceback)
            self.logger.error("=== END EXCEPTION DETAILS ===")

            safe_content = {
                "error": str(exc),
                "traceback": error_traceback,
                "timestamp": error_time,
                "request_path": str(request.url.path),
                "request_method": request.method,
            }

            return self._create_error_response(
                status_code=500,
                content=self.safe_serialize(safe_content),
            )

    def _create_error_response(self, status_code: int, content: dict) -> Response:
        error_response = JSONResponse(status_code=status_code, content=content)
        self._add_cors_headers(error_response)
        return error_response

    def _add_cors_headers(self, response: Response) -> None:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "accept, accept-encoding, authorization, Authorization, content-type, "
            "dnt, origin, user-agent, x-csrftoken, x-requested-with, "
            "x-forwarded-for, x-real-ip, x-forwarded-proto"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"
