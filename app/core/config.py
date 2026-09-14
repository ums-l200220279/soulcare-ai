from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SoulCare API"
    app_env: Literal["local", "staging", "production"] = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    request_body_limit_bytes: int = 16384
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    idempotency_ttl_seconds: int = 300
    data_retention_days: int = 30
    incident_contact_email: str = "oncall@soulcare.local"
    support_disclaimer: str = (
        "SoulCare provides wellness support and is not a replacement for emergency medical care."
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="SOULCARE_", extra="ignore")

    @field_validator("request_body_limit_bytes", "rate_limit_requests", "rate_limit_window_seconds")
    @classmethod
    def _must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be greater than 0")
        return value

    @field_validator("idempotency_ttl_seconds")
    @classmethod
    def _idempotency_window(cls, value: int) -> int:
        if value < 60:
            raise ValueError("must be at least 60 seconds")
        return value

    @field_validator("data_retention_days")
    @classmethod
    def _retention_bounds(cls, value: int) -> int:
        if value < 1 or value > 365:
            raise ValueError("must be between 1 and 365 days")
        return value

    @model_validator(mode="after")
    def _validate_environment_controls(self) -> "Settings":
        if self.app_env in {"staging", "production"}:
            if "*" in self.cors_allowed_origins:
                raise ValueError("wildcard CORS origin is not allowed in staging/production")
            if "@" not in self.incident_contact_email:
                raise ValueError("incident contact email must be valid for staging/production")
        return self


settings = Settings()
