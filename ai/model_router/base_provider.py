"""Abstract Base Class for LLM / AI Model Providers."""
from abc import ABC, abstractmethod
from ai.schemas.common import ModelMetadata
from ai.schemas.model_gateway import ModelRequest, ModelResponse


class BaseModelProvider(ABC):
    """Abstract interface that all model providers (Mock, OpenAI, Anthropic, HuggingFace) must implement."""

    @abstractmethod
    async def invoke(self, request: ModelRequest) -> ModelResponse:
        """Invokes the model provider with a standardized ModelRequest and returns a ModelResponse."""
        pass

    @abstractmethod
    def get_metadata(self) -> ModelMetadata:
        """Returns provider, model name, and version metadata."""
        pass
