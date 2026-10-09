"""Model Registry structure for registering and inspecting active AI model engines."""
from typing import Dict, List, Optional
from pydantic import BaseModel
from ai.configs.settings import settings
from ai.schemas.common import ModelMetadata
from ai.utils.logging import logger


class ModelInfo(BaseModel):
    """Detailed metadata and capabilities of a registered model engine."""
    metadata: ModelMetadata
    capabilities: List[str]
    is_active: bool = True
    timeout_seconds: float = settings.MODEL_TIMEOUT_SECONDS


class ModelRegistry:
    """Central registry managing metadata for AI models, providers, and engine versions."""

    def __init__(self):
        self._registry: Dict[str, ModelInfo] = {}
        self._register_default_models()

    def _register_default_models(self):
        """Registers default foundation model entries."""
        default_model = ModelInfo(
            metadata=ModelMetadata(
                provider=settings.DEFAULT_PROVIDER,
                model=settings.DEFAULT_MODEL_NAME,
                version=settings.DEFAULT_MODEL_VERSION,
            ),
            capabilities=["semantic-matching", "text-explanation", "summarization"],
            is_active=True,
            timeout_seconds=settings.MODEL_TIMEOUT_SECONDS,
        )
        self.register_model("default", default_model)

    def register_model(self, alias: str, model_info: ModelInfo) -> None:
        """Register a new model configuration in the registry."""
        self._registry[alias] = model_info
        logger.info(
            f"Registered model alias '{alias}': {model_info.metadata.provider}/"
            f"{model_info.metadata.model}:{model_info.metadata.version}"
        )

    def get_model(self, alias: str = "default") -> Optional[ModelInfo]:
        """Retrieve model details by alias."""
        return self._registry.get(alias)

    def get_metadata(self, alias: str = "default") -> ModelMetadata:
        """Helper to get ModelMetadata for a given alias or default."""
        info = self.get_model(alias)
        if info:
            return info.metadata
        return ModelMetadata(
            provider=settings.DEFAULT_PROVIDER,
            model=settings.DEFAULT_MODEL_NAME,
            version=settings.DEFAULT_MODEL_VERSION,
        )

    def list_models(self) -> List[ModelInfo]:
        """List all active models registered."""
        return [info for info in self._registry.values() if info.is_active]


# Global singleton instance for model registry
model_registry = ModelRegistry()
