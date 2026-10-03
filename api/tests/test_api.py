from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


def test_ping_returns_pong() -> None:
    response = client.get("/api/v1/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_unversioned_ping_is_not_available() -> None:
    response = client.get("/api/ping")

    assert response.status_code == 404


def test_requires_an_image() -> None:
    response = client.post("/api/v1/palettes")

    assert response.status_code == 422


def test_rejects_an_unsupported_media_type() -> None:
    response = client.post(
        "/api/v1/palettes",
        files={"image": ("document.pdf", b"not-a-pdf", "application/pdf")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == (
        "Formato no permitido. Utiliza JPEG, PNG o WebP."
    )


def test_rejects_an_invalid_color_count() -> None:
    response = client.post(
        "/api/v1/palettes",
        files={"image": ("image.png", b"invalid", "image/png")},
        data={"color_count": "9"},
    )

    assert response.status_code == 422


def test_extracts_a_palette_from_png() -> None:
    image = Image.new("RGB", (12, 12), "#E63946")
    for x in range(6, 12):
        for y in range(12):
            image.putpixel((x, y), (69, 123, 157))
    contents = BytesIO()
    image.save(contents, format="PNG")

    response = client.post(
        "/api/v1/palettes",
        files={"image": ("colors.png", contents.getvalue(), "image/png")},
        data={"color_count": "3"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "colors.png"
    assert payload["color_count"] == 2
    assert payload["width"] == 12
    assert payload["height"] == 12
    assert sum(color["percentage"] for color in payload["colors"]) == 100
