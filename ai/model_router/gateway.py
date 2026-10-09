"""Model Gateway centralizing LLM provider calls, task-based routing, retries, and timeouts."""
import asyncio
import time
from typing import Dict, Optional
from ai.configs.settings import settings
from ai.gateway.errors import AIModelException, AITimeoutException, AIValidationException
from ai.model_router.base_provider import BaseModelProvider
from ai.model_router.mock_provider import MockModelProvider
from ai.schemas.common import ModelMetadata
from ai.schemas.model_gateway import ModelRequest, ModelResponse, TaskType
from ai.utils.logging import logger


class ModelGateway:
    """Central gateway for model invocation, task-based routing, retries, and validation."""

    def __init__(self):
        self._providers: Dict[str, BaseModelProvider] = {}
        self._task_routes: Dict[TaskType, str] = {}
        self._setup_defaults()

    def _setup_defaults(self):
        """Initializes default mock provider and routes all initial task types to it."""
        default_mock = MockModelProvider(
            provider_name=settings.DEFAULT_PROVIDER,
            model_name=settings.DEFAULT_MODEL_NAME,
            version=settings.DEFAULT_MODEL_VERSION,
        )
        self.register_provider("default", default_mock)

        # Route all TaskTypes to default provider initially
        for task in TaskType:
            self._task_routes[task] = "default"

    def register_provider(self, alias: str, provider: BaseModelProvider) -> None:
        """Register a model provider instance."""
        self._providers[alias] = provider
        logger.info(f"ModelGateway registered provider alias '{alias}': {provider.get_metadata().provider}")

    def route_task(self, task_type: TaskType, provider_alias: str) -> None:
        """Assign a specific provider alias to a TaskType."""
        if provider_alias not in self._providers:
            raise AIValidationException(f"Provider alias '{provider_alias}' is not registered.")
        self._task_routes[task_type] = provider_alias
        logger.info(f"ModelGateway routed task '{task_type.value}' to provider '{provider_alias}'")

    def get_provider_for_request(self, request: ModelRequest) -> BaseModelProvider:
        """Selects provider based on model override or task route."""
        if request.model_override and request.model_override in self._providers:
            return self._providers[request.model_override]

        provider_alias = self._task_routes.get(request.task_type, "default")
        provider = self._providers.get(provider_alias)
        if not provider:
            provider = self._providers.get("default")
        if not provider:
            raise AIModelException(message="No model provider available in gateway.")
        return provider

    async def invoke(self, request: ModelRequest) -> ModelResponse:
        """Invokes model with task routing, input/output validation, timeout, and safe retries."""
        start_time = time.time()

        # 1. Input Validation
        self._validate_input(request)

        # 2. Select Provider
        provider = self.get_provider_for_request(request)
        timeout = request.timeout_seconds or settings.MODEL_TIMEOUT_SECONDS
        max_retries = settings.MODEL_MAX_RETRIES

        last_exception: Optional[Exception] = None

        # 3. Execution with Timeout & Retries
        for attempt in range(1, max_retries + 2):
            try:
                logger.info(
                    f"Model Gateway invoking task '{request.task_type.value}' "
                    f"(Attempt {attempt}/{max_retries + 1}, timeout: {timeout}s)"
                )

                response = await asyncio.wait_for(
                    provider.invoke(request),
                    timeout=timeout
                )

                # 4. Output Validation
                self._validate_output(response)

                # Add Gateway Audit Metadata
                response.audit_metadata.update({
                    "gateway_attempts": attempt,
                    "total_gateway_ms": round((time.time() - start_time) * 1000, 2),
                    "task_type": request.task_type.value
                })

                return response

            except asyncio.TimeoutError:
                last_exception = AITimeoutException(
                    message=f"Model execution timed out after {timeout}s on task '{request.task_type.value}'"
                )
                logger.warning(f"Timeout on attempt {attempt} for task '{request.task_type.value}'")

            except AIModelException as e:
                last_exception = e
                logger.warning(f"AIModelException on attempt {attempt}: {e.message}")

            except AIValidationException:
                # Do not retry on validation failures
                raise

            except Exception as e:
                last_exception = AIModelException(
                    message=f"Unexpected error calling provider: {str(e)}",
                    model_metadata=provider.get_metadata()
                )
                logger.error(f"Unexpected provider error on attempt {attempt}: {str(e)}")

            # Exponential backoff before retry (short backoff for safe retries)
            if attempt <= max_retries:
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

        # If all retries failed, raise the final exception
        if last_exception:
            raise last_exception

        raise AIModelException(message="Model invocation failed after maximum retries.")

    def _validate_input(self, request: ModelRequest) -> None:
        """Validates input payload before passing to downstream providers."""
        if not request.prompt or not request.prompt.strip():
            raise AIValidationException("Request prompt cannot be empty.", field="prompt")

    def _validate_output(self, response: ModelResponse) -> None:
        """Validates model response output."""
        if response.content is None:
            raise AIModelException(
                message="Model returned empty content payload.",
                model_metadata=response.metadata
            )


# Global singleton ModelGateway instance
model_gateway = ModelGateway()
