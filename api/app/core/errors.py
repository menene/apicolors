from collections.abc import Mapping
from typing import Any, Type

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException


def request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    error: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": request_id(request),
    }
    if details:
        error["details"] = details
    return JSONResponse(
        status_code=status_code,
        content={"error": error},
        headers=headers,
    )


def register_error_handlers(
    app: FastAPI, rate_limit_error: Type[RateLimitExceeded]
) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict):
            code = str(exc.detail.get("code", "http_error"))
            message = str(exc.detail.get("message", "Request failed."))
        else:
            code = {
                status.HTTP_404_NOT_FOUND: "not_found",
                status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
            }.get(exc.status_code, "http_error")
            message = str(exc.detail)
        return error_response(
            request,
            exc.status_code,
            code,
            message,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            {
                "field": ".".join(
                    str(part) for part in error["loc"] if part != "body"
                ),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        return error_response(
            request,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "validation_error",
            "La solicitud contiene datos inválidos.",
            details,
        )

    @app.exception_handler(rate_limit_error)
    async def rate_limit_exception_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        response = error_response(
            request,
            status.HTTP_429_TOO_MANY_REQUESTS,
            "rate_limit_exceeded",
            "Se excedió el límite de solicitudes.",
        )
        response.headers["Retry-After"] = "1"
        return response
