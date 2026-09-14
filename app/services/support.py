from app.core.config import settings
from app.models.support import CheckInRequest, CheckInResponse

CRISIS_KEYWORDS = {
    "suicide",
    "self-harm",
    "kill myself",
    "end my life",
    "hurt myself",
}


def build_support_response(payload: CheckInRequest) -> CheckInResponse:
    combined_signal = f"{payload.mood} {payload.text_signal or ''} {payload.voice_signal or ''}".lower()
    if any(keyword in combined_signal for keyword in CRISIS_KEYWORDS):
        return CheckInResponse(
            stress_band="high",
            suggested_action=(
                "If you may harm yourself or someone else, call emergency services now. "
                "Contact a licensed crisis hotline or trusted person immediately."
            ),
            model_signal_used=["mood", "stress_level", "safety_escalation"],
            disclaimer=(
                f"{settings.support_disclaimer} For imminent risk, seek emergency or crisis services now."
            ),
        )

    if payload.stress_level >= 8:
        stress_band = "high"
        suggested_action = (
            "Pause and try a 4-7-8 breathing cycle for 2 minutes, "
            "then contact a trusted person."
        )
    elif payload.stress_level >= 5:
        stress_band = "moderate"
        suggested_action = (
            "Take a short grounding break and log one stress trigger in your journal."
        )
    else:
        stress_band = "low"
        suggested_action = "Keep momentum with a brief reflection and hydration break."

    signals = ["mood", "stress_level"]
    if payload.text_signal:
        signals.append("text")
    if payload.voice_signal:
        signals.append("voice")

    return CheckInResponse(
        stress_band=stress_band,
        suggested_action=suggested_action,
        model_signal_used=signals,
        disclaimer=settings.support_disclaimer,
    )
