from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ping_returns_pong() -> None:
    response = client.get("/api/v1/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_unversioned_ping_is_not_available() -> None:
    response = client.get("/api/ping")

    assert response.status_code == 404
