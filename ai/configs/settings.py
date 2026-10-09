"""Configuration settings for CredSaathi AI Service."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """AI Service Configuration parameters loaded from environment variables or defaults."""

    model_config = SettingsConfigDict(
        env_prefix="AI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General Service Settings
    SERVICE_NAME: str = "CredSaathi AI Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API Prefix & Gateway Settings
    API_V1_STR: str = "/api/v1/ai"

    # Security & Gateway Credentials
    API_KEYS: str = Field(
        default="credsaathi_secret_api_key_v1,credsaathi_frontend_key_prod,credsaathi_test_api_key",
        description="Comma-separated list of authorized API keys for AI microservice gateway",
    )

    # CORS Security Configuration
    CORS_ORIGINS: str = Field(
        default="",
        description="Comma-separated list of allowed CORS origins. If empty in non-dev, wildcard origins are disabled.",
    )

    # Timeout & Rate Limiting Configurations
    DEFAULT_TIMEOUT_SECONDS: float = Field(default=30.0, description="Default request timeout in seconds")
    MODEL_TIMEOUT_SECONDS: float = Field(default=60.0, description="Timeout for external model execution")
    MODEL_MAX_RETRIES: int = Field(default=2, description="Maximum retries for safe model calls")
    RATE_LIMIT_PER_MINUTE: int = Field(default=120, description="Maximum API requests per minute per IP")

    # Default Model & Provider Configurations
    DEFAULT_PROVIDER: str = "mock-provider"
    DEFAULT_MODEL_NAME: str = "mock-llm-v1"
    DEFAULT_MODEL_VERSION: str = "1.0.0"
    LLM_API_KEY: str = Field(default="mock-key-do-not-hardcode", description="LLM Provider API Key loaded from ENV")
    LLM_BASE_URL: str = Field(default="https://api.openai.com/v1", description="LLM Base URL")

    @property
    def allowed_api_keys_list(self) -> list[str]:
        """Return allowed API keys as a clean list."""
        if not self.API_KEYS:
            return []
        return [k.strip() for k in self.API_KEYS.split(",") if k.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        """Return allowed CORS origins as a list."""
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = AISettings()
