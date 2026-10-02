from time import perf_counter

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile, status
from PIL import UnidentifiedImageError

from app.palette import extract_palette
from app.schemas import ErrorResponse, PaletteColor, PaletteResponse, RGBColor
from app.core.config import settings
from app.core.rate_limit import limiter

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

router = APIRouter(prefix="/palettes", tags=["palettes"])


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def parse_color_count(value: str) -> int:
    try:
        color_count = int(value)
    except (TypeError, ValueError):
        color_count = 0
    if not 3 <= color_count <= 8:
        raise api_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "invalid_color_count",
            "La cantidad de colores debe estar entre 3 y 8.",
        )
    return color_count


@router.post(
    "",
    response_model=PaletteResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image"},
        413: {"model": ErrorResponse, "description": "Image is too large"},
        415: {"model": ErrorResponse, "description": "Unsupported image format"},
        422: {"model": ErrorResponse, "description": "Invalid request"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Extract an image color palette",
)
@limiter.limit(settings.palette_rate_limit)
async def create_palette(
    request: Request,
    response: Response,
    image: UploadFile | None = File(None),
    color_count: str = Form("5"),
) -> PaletteResponse:
    if image is None:
        raise api_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "image_required",
            "La imagen es obligatoria.",
        )

    requested_colors = parse_color_count(color_count)
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        await image.close()
        raise api_error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "unsupported_media_type",
            "Formato no permitido. Utiliza JPEG, PNG o WebP.",
        )

    contents = await image.read(MAX_FILE_SIZE + 1)
    filename = image.filename or "imagen"
    await image.close()
    if len(contents) > MAX_FILE_SIZE:
        raise api_error(
            status.HTTP_413_CONTENT_TOO_LARGE,
            "image_too_large",
            "La imagen supera el límite de 5 MB.",
        )

    started_at = perf_counter()
    try:
        width, height, colors = extract_palette(contents, requested_colors)
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        raise api_error(
            status.HTTP_400_BAD_REQUEST,
            "invalid_image",
            "No fue posible leer la imagen.",
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
