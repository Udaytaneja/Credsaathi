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
    ai_service_url: str = "http://localhost:8001/api/v1/ai"
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
        """Return CORS origins as a list of sanitized strings without trailing slashes."""
        default_origins = [
            "https://credsaathi.vercel.app",
            "https://credsaathi-euuqbyvr-cod-x-titans.vercel.app",
            "http://localhost:3000",
            "http://localhost:5173",
        ]
        raw_origins = [o.strip() for o in self.cors_origins.split(",")] if self.cors_origins.strip() else default_origins
        if self.app_env.lower() in ("production", "prod"):
            for origin in (
                "https://credsaathi.vercel.app",
                "https://credsaathi-euuqbyvr-cod-x-titans.vercel.app",
            ):
                if origin not in raw_origins:
                    raw_origins.append(origin)

        origins: list[str] = []
        for item in raw_origins:
            cleaned = item.strip().rstrip("/")
            if cleaned and cleaned not in origins:
                origins.append(cleaned)
        return origins

    def check_production_safety(self) -> None:
        """Validate safety rules in non-development environments."""
        if self.app_env.lower() in ("production", "prod"):
            if "change_in_production" in self.secret_key or self.secret_key == "change-this-in-production":
                raise ValueError("CRITICAL SECURITY ERROR: SECRET_KEY must be set securely in production!")
            if self.ai_api_key == "credsaathi_secret_api_key_v1":
                raise ValueError("CRITICAL SECURITY ERROR: AI_API_KEY must be set securely in production!")
            if "*" in self.cors_origins_list:
                raise ValueError("CRITICAL SECURITY ERROR: Wildcard '*' CORS origin is not allowed in production with credentials!")



@lru_cache
def get_settings() -> Settings:
    """
    Return the cached application settings instance.
    """
    return Settings()  # pyright: ignore[reportCallIssue]


settings = get_settings()
