from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration for CredSaathi.

    Values are loaded from environment variables and .env.
    """

    # Application
    app_name: str = "CredSaathi API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True

    # API
    api_v1_prefix: str = "/api/v1"

    # Security
    secret_key: str = "credsaathi_dev_secret_key_must_change_in_production_32_bytes"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # AI Microservice Integration
    ai_service_url: str = "http://localhost:8000/api/v1/ai"
    ai_api_key: str = "credsaathi_secret_api_key_v1"
    ai_service_timeout: float = 10.0

    # Database
    database_url: str = "sqlite:///:memory:"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a list."""
        if not self.cors_origins:
            return []

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached application settings instance.
    """
    return Settings()  # pyright: ignore[reportCallIssue]


settings = get_settings()