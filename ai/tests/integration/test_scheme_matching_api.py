"""Integration test for POST /api/v1/ai/scheme-match endpoint."""
from fastapi import status


def test_scheme_match_api_endpoint(client, auth_headers):
    payload = {
        "applicant_context": {
            "applicant_id": "user_anon_77",
            "category": "Women",
            "state": "Delhi",
            "income_annual": 400000.0,
            "purpose": "Opening boutique"
        },
        "candidate_schemes": [
            {
                "scheme_id": "SCH_MAHILA_01",
                "scheme_name": "Mahila Samriddhi Yojana",
                "category": "Women",
                "description": "Micro loans for women micro-entrepreneurs",
                "eligibility_criteria": ["Must be woman applicant"],
                "required_documents": ["Bank Statement", "Aadhaar Card"],
                "backend_eligibility_status": "ELIGIBLE",
                "source_reference": "Govt Scheme Portal",
                "last_verified": "2026-10-01"
            }
        ],
        "language": "en"
    }

    response = client.post("/api/v1/ai/scheme-match", json=payload, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["success"] is True
    assert "matches" in body["data"]
    assert len(body["data"]["matches"]) == 1

    match = body["data"]["matches"][0]
    assert match["scheme_id"] == "SCH_MAHILA_01"
    assert 0.0 <= match["relevance_score"] <= 0.99
    assert match["eligibility_status"] == "ELIGIBLE"
    assert "disclaimer" in body["data"]
