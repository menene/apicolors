from io import BytesIO
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.rate_limit import limiter
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limits() -> None:
    limiter.reset()


def test_ping_returns_pong() -> None:
    response = client.get("/api/v1/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
    UUID(response.headers["x-request-id"])


def test_preserves_a_valid_request_id() -> None:
    response = client.get(
        "/api/v1/ping",
        headers={"X-Request-ID": "workshop-request-01"},
    )

    assert response.headers["x-request-id"] == "workshop-request-01"


def test_unversioned_ping_is_not_available() -> None:
    response = client.get("/api/ping")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_method_not_allowed_preserves_the_allow_header() -> None:
    response = client.post("/api/v1/ping")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"
    assert response.headers["allow"] == "GET"


def test_requires_an_image() -> None:
    response = client.post("/api/v1/palettes")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "image_required"
    assert response.json()["error"]["message"] == "La imagen es obligatoria."


def test_rejects_an_unsupported_media_type() -> None:
    response = client.post(
        "/api/v1/palettes",
        files={"image": ("document.pdf", b"not-a-pdf", "application/pdf")},
    )

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_media_type"
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_rejects_an_invalid_color_count() -> None:
    response = client.post(
        "/api/v1/palettes",
        files={"image": ("image.png", b"invalid", "image/png")},
        data={"color_count": "9"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_color_count"


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


def test_cors_allows_the_configured_frontend_origin() -> None:
    response = client.options(
        "/api/v1/palettes",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_does_not_allow_an_unknown_origin() -> None:
    response = client.options(
        "/api/v1/palettes",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert "access-control-allow-origin" not in response.headers


def test_palette_endpoint_has_a_stricter_rate_limit() -> None:
    assert client.post("/api/v1/palettes").status_code == 422
    assert client.post("/api/v1/palettes").status_code == 422

    response = client.post("/api/v1/palettes")

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limit_exceeded"
    assert response.headers["retry-after"] == "1"


def test_api_has_a_default_rate_limit() -> None:
    for _ in range(10):
        assert client.get("/api/v1/ping").status_code == 200

    response = client.get("/api/v1/ping")

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limit_exceeded"
