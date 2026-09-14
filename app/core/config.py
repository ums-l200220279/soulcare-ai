from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SoulCare API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    support_disclaimer: str = (
        "SoulCare provides wellness support and is not a replacement for emergency medical care."
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="SOULCARE_", extra="ignore")


settings = Settings()
