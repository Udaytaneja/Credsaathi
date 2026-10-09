"""Integration test for POST /api/v1/ai/financial-explanation endpoint."""
from fastapi import status


def test_financial_explanation_api_endpoint(client, auth_headers):
    payload = {
        "validated_income": 500000.0,
        "turnover": 1200000.0,
        "revenue": 1100000.0,
        "expenses": 350000.0,
        "existing_liabilities": 100000.0,
        "existing_loans": [],
        "repayment_information": "Clean track record, 0 defaults",
        "cash_flow_information": "Positive net operating cash flow",
        "loan_requirement": 400000.0,
        "currency": "INR"
    }

    response = client.post("/api/v1/ai/financial-explanation", json=payload, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["success"] is True
    assert "summary" in body["data"]
    assert body["data"]["source"] == "backend_validated_data"
    assert len(body["data"]["key_facts"]) >= 4
    assert any("500,000.00" in f for f in body["data"]["key_facts"])
    assert "disclaimer" in body["data"]
