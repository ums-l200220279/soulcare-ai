from pydantic import BaseModel, Field


class CheckInRequest(BaseModel):
    mood: str = Field(min_length=1, max_length=100)
    stress_level: int = Field(ge=1, le=10)
    text_signal: str | None = Field(default=None, max_length=500)
    voice_signal: str | None = Field(default=None, max_length=500)


class CheckInResponse(BaseModel):
    stress_band: str
    suggested_action: str
    model_signal_used: list[str]
    disclaimer: str
