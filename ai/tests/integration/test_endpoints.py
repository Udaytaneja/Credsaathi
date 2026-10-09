"""Integration tests for FastAPI gateway endpoints."""
from unittest.mock import patch
import pytest
from fastapi import status
from ai.gateway.errors import AIModelException, AITimeoutException


def test_health_endpoint(client):
    response = client.get("/api/v1/ai/health")
    assert response.status_code == status.HTTP_200_OK

    json_body = response.json()
    assert json_body["success"] is True
    assert json_body["data"]["status"] == "healthy"
    assert json_body["data"]["service"] == "CredSaathi AI Service"
    assert json_body["model"]["provider"] == "mock-provider"
    assert "request_id" in json_body
    assert json_body["errors"] == []


def test_models_endpoint(client):
    response = client.get("/api/v1/ai/models")
    assert response.status_code == status.HTTP_200_OK

    json_body = response.json()
    assert json_body["success"] is True
    assert isinstance(json_body["data"], list)
    assert len(json_body["data"]) >= 1
    assert json_body["data"][0]["metadata"]["model"] == "mock-llm-v1"


def test_custom_request_id_header(client):
    custom_id = "test-correlation-id-999"
    response = client.get("/api/v1/ai/health", headers={"X-Request-ID": custom_id})

    assert response.status_code == status.HTTP_200_OK
    assert response.headers.get("X-Request-ID") == custom_id
    json_body = response.json()
    assert json_body["request_id"] == custom_id


def test_unauthorized_access(client):
    # Passing invalid or missing API key -> 401 Unauthorized
    response = client.post("/api/v1/ai/scheme-match", json={}, headers={"X-API-Key": "invalid_key"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    json_body = response.json()
    assert json_body["success"] is False
    assert json_body["errors"][0]["code"] == "UNAUTHORIZED"


def test_malformed_request(client, auth_headers):
    # Invalid data types / missing required fields -> Validation Error
    response = client.post("/api/v1/ai/scheme-match", json={"invalid_field": 123}, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_successful_scheme_matching_endpoint(client, auth_headers):
    payload = {
        "applicant_context": {
            "applicant_id": "test_app_01",
            "category": "Women",
            "income_annual": 300000.0,
            "purpose": "Business expansion",
        },
        "candidate_schemes": [
            {
                "scheme_id": "SCH_001",
                "scheme_name": "Mudra Yojana",
                "category": "General",
                "description": "Micro business loan scheme",
                "eligibility_criteria": ["Micro enterprise owner"],
                "required_documents": ["Aadhaar"],
            }
        ],
    }

    response = client.post("/api/v1/ai/scheme-match", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    json_body = response.json()
    assert json_body["success"] is True
    assert "matches" in json_body["data"]
    assert json_body["model"]["provider"] == "mock-provider"


def test_successful_document_extraction_endpoint(client, auth_headers):
    payload = {
        "document_type": "identity_proof",
        "file_name": "pan_card.pdf",
        "file_text_override": "INCOME TAX DEPARTMENT GOVT OF INDIA PAN ABCDE1234F NAME RAMESH",
    }

    response = client.post("/api/v1/ai/extract-document", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    json_body = response.json()
    assert json_body["success"] is True
    assert "fields" in json_body["data"]


def test_successful_financial_explanation_endpoint(client, auth_headers):
    payload = {
        "validated_income": 600000.0,
        "turnover": 1200000.0,
        "revenue": 1100000.0,
        "expenses": 350000.0,
        "existing_liabilities": 100000.0,
        "existing_loans": [],
        "repayment_information": "Clean track record, 0 defaults",
        "cash_flow_information": "Positive net operating cash flow",
        "loan_requirement": 400000.0,
        "currency": "INR",
    }

    response = client.post("/api/v1/ai/financial-explanation", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    json_body = response.json()
    assert json_body["success"] is True
    assert "summary" in json_body["data"]


def test_successful_assistant_query_endpoint(client, auth_headers):
    payload = {
        "query": "What is the Mudra loan limit?",
        "language": "en",
        "authenticated_user_id": "user_asst_01",
    }

    response = client.post("/api/v1/ai/assistant/query", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    json_body = response.json()
    assert json_body["success"] is True
    assert "answer" in json_body["data"]


def test_model_failure_error_envelope(client, auth_headers):
    valid_payload = {
        "applicant_context": {
            "applicant_id": "test_app_01",
            "category": "Women",
            "income_annual": 300000.0,
            "purpose": "Business expansion",
        },
        "candidate_schemes": [
            {
                "scheme_id": "SCH_001",
                "scheme_name": "Mudra Yojana",
                "category": "General",
                "description": "Micro business loan scheme",
                "eligibility_criteria": ["Micro enterprise owner"],
                "required_documents": ["Aadhaar"],
            }
        ],
    }

    with patch(
        "ai.matching.service.scheme_matching_service.match_schemes",
        side_effect=AIModelException("Downstream model provider connection refused"),
    ):
        response = client.post("/api/v1/ai/scheme-match", json=valid_payload, headers=auth_headers)
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        json_body = response.json()
        assert json_body["success"] is False
        assert json_body["errors"][0]["code"] == "MODEL_EXECUTION_ERROR"


def test_model_timeout_error_envelope(client, auth_headers):
    valid_payload = {
        "applicant_context": {
            "applicant_id": "test_app_01",
            "category": "Women",
            "income_annual": 300000.0,
            "purpose": "Business expansion",
        },
        "candidate_schemes": [
            {
                "scheme_id": "SCH_001",
                "scheme_name": "Mudra Yojana",
                "category": "General",
                "description": "Micro business loan scheme",
                "eligibility_criteria": ["Micro enterprise owner"],
                "required_documents": ["Aadhaar"],
            }
        ],
    }

    with patch(
        "ai.matching.service.scheme_matching_service.match_schemes",
        side_effect=AITimeoutException("Operation timed out after 10.0s"),
    ):
        response = client.post("/api/v1/ai/scheme-match", json=valid_payload, headers=auth_headers)
        assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        json_body = response.json()
        assert json_body["success"] is False
        assert json_body["errors"][0]["code"] == "OPERATION_TIMEOUT"
