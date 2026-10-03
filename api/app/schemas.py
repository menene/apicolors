from pydantic import BaseModel, Field


class RGBColor(BaseModel):
    red: int = Field(ge=0, le=255)
    green: int = Field(ge=0, le=255)
    blue: int = Field(ge=0, le=255)


class PaletteColor(BaseModel):
    hex: str = Field(pattern=r"^#[0-9A-F]{6}$")
    rgb: RGBColor
    percentage: float = Field(ge=0, le=100)


class PaletteResponse(BaseModel):
    filename: str
    color_count: int = Field(ge=1, le=8)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    processing_ms: float = Field(ge=0)
    colors: list[PaletteColor]


class PingResponse(BaseModel):
    message: str = Field(examples=["pong"])
