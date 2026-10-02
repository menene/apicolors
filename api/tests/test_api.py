from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def test_ping_returns_pong() -> None:
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
    assert response.headers["x-request-id"]


def test_unversioned_health_route_is_not_available() -> None:
    response = client.get("/api/health")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_requires_an_image() -> None:
    response = client.post("/api/v1/palettes")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "image_required"
    assert response.json()["error"]["message"] == "La imagen es obligatoria."


def test_extracts_a_palette_from_png() -> None:
    image = Image.new("RGB", (12, 12), "#E63946")
    for x in range(6, 12):
        for y in range(12):
            image.putpixel((x, y), (69, 123, 157))
    contents = BytesIO()
    image.save(contents, format="PNG")

    response = client.post(
        "/api/v1/palettes",
        files={"image": ("colores.png", contents.getvalue(), "image/png")},
        data={"color_count": "3"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["color_count"] == 2
    assert payload["width"] == 12
    assert sum(color["percentage"] for color in payload["colors"]) == 100


def test_cors_allows_configured_frontend_origin() -> None:
    response = client.options(
        "/api/v1/palettes",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
