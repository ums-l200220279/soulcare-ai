from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rejects_payload_over_limit() -> None:
    body = '{"mood":"' + ("x" * 20000) + '","stress_level":5}'
    response = client.post(
        "/v1/support/check-in",
        content=body,
        headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"


def test_security_headers_present() -> None:
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "default-src 'none'" in response.headers["content-security-policy"]
