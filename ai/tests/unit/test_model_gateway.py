"""Unit tests for CredSaathi AI Model Gateway and Provider Abstraction."""
import pytest
from pydantic import ValidationError
from ai.gateway.errors import AIModelException, AITimeoutException, AIValidationException
from ai.model_router.gateway import ModelGateway
from ai.model_router.mock_provider import MockModelProvider
from ai.schemas.model_gateway import ModelRequest, TaskType


@pytest.mark.asyncio
async def test_successful_mock_invocation():
    gateway = ModelGateway()
    req = ModelRequest(
        task_type=TaskType.CLASSIFICATION,
        prompt="Check eligibility for scheme A",
        user_id="user_123"
    )

    response = await gateway.invoke(req)

    assert response is not None
    assert response.content == "ELIGIBLE"
    assert response.structured_output["category"] == "ELIGIBLE"
    assert response.metadata.provider == "mock-provider"
    assert response.cost.total_tokens > 0
    assert response.request_id == req.request_id
    assert response.audit_metadata["task_type"] == "classification"


@pytest.mark.asyncio
async def test_task_based_routing():
    gateway = ModelGateway()
    custom_mock = MockModelProvider(provider_name="custom-provider", model_name="custom-model")
    gateway.register_provider("custom", custom_mock)
    gateway.route_task(TaskType.FINANCIAL_EXPLANATION, "custom")

    req = ModelRequest(
        task_type=TaskType.FINANCIAL_EXPLANATION,
        prompt="Explain debt ratio"
    )

    res = await gateway.invoke(req)
    assert res.metadata.provider == "custom-provider"
    assert res.metadata.model == "custom-model"


@pytest.mark.asyncio
async def test_invalid_input_validation():
    gateway = ModelGateway()

    with pytest.raises(ValidationError):
        # Empty string prompt fails Pydantic schema validation
        ModelRequest(task_type=TaskType.CLASSIFICATION, prompt="")

    with pytest.raises(ValidationError):
        # Whitespace-only prompt fails Pydantic schema validation
        ModelRequest(task_type=TaskType.SUMMARIZATION, prompt="   ")


@pytest.mark.asyncio
async def test_timeout_handling():
    gateway = ModelGateway()
    slow_mock = MockModelProvider(delay_seconds=2.0)
    gateway.register_provider("slow", slow_mock)

    req = ModelRequest(
        task_type=TaskType.EXTRACTION,
        prompt="Extract PAN details",
        model_override="slow",
        timeout_seconds=0.1
    )

    with pytest.raises(AITimeoutException):
        await gateway.invoke(req)


@pytest.mark.asyncio
async def test_provider_failure_and_retries():
    gateway = ModelGateway()
    failing_mock = MockModelProvider(should_fail=True, failure_message="Upstream API 500 error")
    gateway.register_provider("failing", failing_mock)

    req = ModelRequest(
        task_type=TaskType.RAG,
        prompt="Query FAQ",
        model_override="failing"
    )

    with pytest.raises(AIModelException) as exc_info:
        await gateway.invoke(req)

    assert "Upstream API 500 error" in exc_info.value.message


@pytest.mark.asyncio
async def test_malformed_output():
    gateway = ModelGateway()
    malformed_mock = MockModelProvider(should_return_malformed=True)
    gateway.register_provider("malformed", malformed_mock)

    req = ModelRequest(
        task_type=TaskType.EXTRACTION,
        prompt="Extract document JSON",
        model_override="malformed"
    )

    res = await gateway.invoke(req)
    assert res.content.startswith("INVALID_JSON")
    assert res.structured_output is None


@pytest.mark.asyncio
async def test_model_metadata_verification():
    gateway = ModelGateway()
    mock_prov = MockModelProvider(provider_name="test-prov", model_name="test-mod", version="2.5.0")
    gateway.register_provider("test_alias", mock_prov)

    req = ModelRequest(
        task_type=TaskType.TRANSLATION,
        prompt="Translate to Hindi",
        model_override="test_alias"
    )

    res = await gateway.invoke(req)
    assert res.metadata.provider == "test-prov"
    assert res.metadata.model == "test-mod"
    assert res.metadata.version == "2.5.0"
