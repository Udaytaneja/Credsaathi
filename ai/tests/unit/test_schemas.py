"""Unit tests for Pydantic base schemas and ResponseEnvelope."""
from ai.schemas.common import ErrorDetail, ModelMetadata, ResponseEnvelope


def test_model_metadata_instantiation():
    meta = ModelMetadata(provider="TestProvider", model="TestModel", version="1.0")
    assert meta.provider == "TestProvider"
    assert meta.model == "TestModel"
    assert meta.version == "1.0"


def test_response_envelope_success():
    data = {"result": "ok"}
    meta = ModelMetadata(provider="P", model="M", version="V")
    envelope = ResponseEnvelope.success_response(data=data, model_metadata=meta, request_id="req-123")

    assert envelope.success is True
    assert envelope.data == {"result": "ok"}
    assert envelope.model.model == "M"
    assert envelope.request_id == "req-123"
    assert len(envelope.errors) == 0


def test_response_envelope_error():
    err = ErrorDetail(code="BAD_INPUT", message="Field required", field="name")
    envelope = ResponseEnvelope.error_response(errors=[err], request_id="req-456")

    assert envelope.success is False
    assert envelope.data is None
    assert envelope.request_id == "req-456"
    assert len(envelope.errors) == 1
    assert envelope.errors[0].code == "BAD_INPUT"
    assert envelope.errors[0].field == "name"
