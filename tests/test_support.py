from fastapi.testclient import TestClient

from app.main import app

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


def test_check_in_validates_stress_level_bounds() -> None:
    response = client.post(
        "/v1/support/check-in",
        json={"mood": "calm", "stress_level": 11},
    )

    assert response.status_code == 422
