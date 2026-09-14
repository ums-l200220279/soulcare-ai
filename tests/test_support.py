from fastapi.testclient import TestClient

from app.main import app
from app.core.runtime import RateLimiter

client = TestClient(app)


def test_check_in_high_stress_includes_multimodal_signals() -> None:
    response = client.post(
        "/v1/support/check-in",
        json={
            "mood": "overwhelmed",
            "stress_level": 9,
            "text_signal": "I cannot focus",
            "voice_signal": "shaky speech",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["stress_band"] == "high"
    assert payload["model_signal_used"] == ["mood", "stress_level", "text", "voice"]
    assert "not a replacement" in payload["disclaimer"]
    assert response.headers["x-request-id"]


def test_check_in_validates_stress_level_bounds() -> None:
    response = client.post(
        "/v1/support/check-in",
        json={"mood": "calm", "stress_level": 11},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"


def test_check_in_escalates_crisis_language() -> None:
    response = client.post(
        "/v1/support/check-in",
        json={"mood": "panic", "stress_level": 7, "text_signal": "I want to end my life"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["stress_band"] == "high"
    assert "emergency services" in payload["suggested_action"]


def test_check_in_idempotency_returns_same_response() -> None:
    headers = {"Idempotency-Key": "fixed-key-1"}
    request_payload = {"mood": "stressed", "stress_level": 6}
    first = client.post("/v1/support/check-in", json=request_payload, headers=headers)
    second = client.post("/v1/support/check-in", json=request_payload, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_check_in_idempotency_rejects_payload_mismatch() -> None:
    headers = {"Idempotency-Key": "fixed-key-2"}
    first = client.post("/v1/support/check-in", json={"mood": "stressed", "stress_level": 6}, headers=headers)
    second = client.post("/v1/support/check-in", json={"mood": "calm", "stress_level": 2}, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 409
    payload = second.json()
    assert payload["error"]["code"] == "request_failed"


def test_rate_limit_enforced() -> None:
    original = app.state.rate_limiter
    app.state.rate_limiter = RateLimiter(limit=1, window_seconds=60)
    try:
        first = client.post("/v1/support/check-in", json={"mood": "calm", "stress_level": 3})
        second = client.post("/v1/support/check-in", json={"mood": "calm", "stress_level": 3})
    finally:
        app.state.rate_limiter = original

    assert first.status_code == 200
    assert second.status_code == 429
    payload = second.json()
    assert payload["error"]["code"] == "rate_limited"
