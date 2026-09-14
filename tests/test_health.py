from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "SoulCare API"


def test_ready_endpoint() -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"


def test_request_id_header_present() -> None:
    response = client.get("/health")
    assert response.headers["x-request-id"]
