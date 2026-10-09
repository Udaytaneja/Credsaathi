"""Integration test for Saakshi Assistant API endpoint."""
from fastapi import status


def test_saakshi_assistant_api_endpoint(client, auth_headers):
    payload = {
        "query": "What are the required documents for PMEGP?",
        "language": "en",
        "authenticated_user_id": "user_ramesh_01"
    }

    response = client.post("/api/v1/ai/assistant/query", json=payload, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["success"] is True
    assert "answer" in body["data"]
    assert body["data"]["safety_flags"]["evidence_found"] is True
    assert len(body["data"]["citations"]) >= 1
    assert "disclaimer" in body["data"]
