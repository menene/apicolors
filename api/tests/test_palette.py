from app.palette import ExtractedColor


def test_hex_color() -> None:
    color = ExtractedColor(red=42, green=157, blue=143, percentage=100.0)
    assert color.hex == "#2A9D8F"
