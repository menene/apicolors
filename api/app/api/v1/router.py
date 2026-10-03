from fastapi import APIRouter

from app.api.v1.endpoints import system


router = APIRouter(prefix="/v1")
router.include_router(system.router)
