"""Unit tests for configuration settings and ModelRegistry."""
from ai.configs.settings import AISettings
from ai.model_router.registry import ModelInfo, ModelRegistry
from ai.schemas.common import ModelMetadata


def test_ai_settings_defaults():
    s = AISettings()
    assert s.SERVICE_NAME == "CredSaathi AI Service"
    assert s.API_V1_STR == "/api/v1/ai"
    assert s.DEFAULT_TIMEOUT_SECONDS == 30.0
    assert s.RATE_LIMIT_PER_MINUTE == 120


def test_model_registry_registration_and_lookup():
    reg = ModelRegistry()
    assert reg.get_model("default") is not None

    custom_info = ModelInfo(
        metadata=ModelMetadata(provider="OpenAI", model="gpt-4o", version="2026"),
        capabilities=["vision", "agent"],
        is_active=True
    )
    reg.register_model("gpt4", custom_info)

    retrieved = reg.get_model("gpt4")
    assert retrieved is not None
    assert retrieved.metadata.provider == "OpenAI"
    assert retrieved.metadata.model == "gpt-4o"
    assert "vision" in retrieved.capabilities

    models = reg.list_models()
    assert len(models) == 2
