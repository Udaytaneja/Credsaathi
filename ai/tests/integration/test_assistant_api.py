"""Integration test for POST /api/v1/ai/assistant/query endpoint."""
from fastapi import status


def test_assistant_query_api_endpoint(client, auth_headers):
    payload = {
        "query": "What are MUDRA loan categories Shishu Kishore Tarun?",
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
    assert body["data"]["citations"][0]["source_id"] == "SRC_LENDER_MUDRA"
