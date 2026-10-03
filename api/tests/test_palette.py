from io import BytesIO

from PIL import Image

from app.palette import ExtractedColor, extract_palette


def test_hex_color() -> None:
    color = ExtractedColor(red=42, green=157, blue=143, percentage=100.0)

    assert color.hex == "#2A9D8F"


def test_extracts_colors_and_preserves_original_dimensions() -> None:
    image = Image.new("RGB", (240, 120), "#E63946")
    for x in range(120, 240):
        for y in range(120):
            image.putpixel((x, y), (69, 123, 157))
    contents = BytesIO()
    image.save(contents, format="PNG")

    width, height, colors = extract_palette(contents.getvalue(), 2)

    assert (width, height) == (240, 120)
    assert len(colors) == 2
    assert sum(color.percentage for color in colors) == 100
