from fastapi import APIRouter

from app.schemas import PingResponse

router = APIRouter(tags=["system"])


@router.get(
    "/ping",
    response_model=PingResponse,
    summary="Check API availability",
)
async def ping() -> PingResponse:
    return PingResponse(message="pong")
