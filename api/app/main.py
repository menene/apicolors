from re import fullmatch
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.rate_limit import limiter


def create_application() -> FastAPI:
    application = FastAPI(
        title="API a todo color",
        description="Extrae los colores predominantes de una imagen.",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=list(settings.trusted_hosts),
        www_redirect=False,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Accept", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID", "Retry-After"],
        max_age=600,
    )
    application.state.limiter = limiter
    application.add_middleware(SlowAPIMiddleware)

    @application.middleware("http")
    async def add_request_id(request: Request, call_next):
        supplied_id = request.headers.get("X-Request-ID", "")
        request.state.request_id = (
            supplied_id
            if fullmatch(r"[A-Za-z0-9._-]{1,128}", supplied_id)
            else str(uuid4())
        )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    register_error_handlers(application, RateLimitExceeded)
    application.include_router(api_router)
    return application


app = create_application()
