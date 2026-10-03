from time import perf_counter

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from PIL import UnidentifiedImageError

from app.palette import extract_palette
from app.schemas import PaletteColor, PaletteResponse, RGBColor


MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

router = APIRouter(prefix="/palettes", tags=["palettes"])


@router.post(
    "",
    response_model=PaletteResponse,
    responses={
        400: {"description": "Invalid image"},
        413: {"description": "Image is too large"},
        415: {"description": "Unsupported image format"},
        422: {"description": "Invalid request"},
    },
    summary="Extract an image color palette",
)
async def create_palette(
    image: UploadFile = File(...),
    color_count: int = Form(5, ge=3, le=8),
) -> PaletteResponse:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        await image.close()
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no permitido. Utiliza JPEG, PNG o WebP.",
        )

    contents = await image.read(MAX_FILE_SIZE + 1)
    filename = image.filename or "imagen"
    await image.close()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="La imagen supera el límite de 5 MB.",
        )

    started_at = perf_counter()
    try:
        width, height, colors = extract_palette(contents, color_count)
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fue posible leer la imagen.",
        ) from None

    return PaletteResponse(
        filename=filename,
        color_count=len(colors),
        width=width,
        height=height,
        processing_ms=round((perf_counter() - started_at) * 1000, 2),
        colors=[
            PaletteColor(
                hex=color.hex,
                rgb=RGBColor(red=color.red, green=color.green, blue=color.blue),
                percentage=color.percentage,
            )
            for color in colors
        ],
    )
