from fastapi import APIRouter

from app.api.v1.endpoints import palettes, system


router = APIRouter(prefix="/v1")
router.include_router(system.router)
router.include_router(palettes.router)
