from fastapi import APIRouter, Request, Response

from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas import ErrorResponse, PingResponse


router = APIRouter(tags=["system"])


@router.get(
    "/ping",
    response_model=PingResponse,
    responses={429: {"model": ErrorResponse, "description": "Rate limit exceeded"}},
    summary="Check API availability",
)
@limiter.limit(settings.api_rate_limit)
async def ping(request: Request, response: Response) -> PingResponse:
    return PingResponse(message="pong")
